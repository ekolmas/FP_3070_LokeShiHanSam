import express from "express";
import path from "path";
import { spawn } from "child_process";
import { getDb } from "../db.js";

const router = express.Router();

import EventEmitter from "events";
import { randomUUID } from "crypto";

const jobs = new Map(); // jobId -> { emitter, items, done, error, startedAt, meta }


function requireAuth(req, res, next) {
  if (!req.session.userId) return res.redirect("/");
  next();
}

async function fetch30Articles() {
  const apiKey = process.env.NEWSAPI_KEY;
  if (!apiKey) throw new Error("Missing NEWSAPI_KEY in .env");

  // Example query (tune however you like)
  const url =
    `https://newsapi.org/v2/top-headlines?` +
    new URLSearchParams({
      language: "en",
      pageSize: "30",
      category: "technology", // or "business" etc
    });

  const resp = await fetch(url, {
    headers: { "X-Api-Key": apiKey },
  });

  if (!resp.ok) {
    const t = await resp.text();
    throw new Error(`NewsAPI error ${resp.status}: ${t}`);
  }

  const data = await resp.json();
  return data.articles || [];
}

function startPythonPipelineJob({ db, articles, user_pref }) {
  const jobId = randomUUID();
  const emitter = new EventEmitter();

  jobs.set(jobId, {
    emitter,
    items: [],
    done: false,
    error: null,
    meta: null,
    startedAt: Date.now(),
  });

  const pythonExe = process.env.PYTHON_EXE || "python";
  const scriptPath = path.join(process.cwd(), "../backend", "pipeline", "main.py");

  const child = spawn(pythonExe, ["-u", scriptPath], {
    cwd: process.cwd(),
    env: { ...process.env, PYTHONUNBUFFERED: "1" },
  });

  let buf = "";
  let stderr = "";

  child.stdout.on("data", async (chunk) => {
    buf += chunk.toString();

    const lines = buf.split("\n");
    buf = lines.pop() || "";

    for (const line of lines) {
      const t = line.trim();
      if (!t) continue;

      try {
        const msg = JSON.parse(t);
        const job = jobs.get(jobId);
        if (!job) return;

        // If your python emits item_ready/done/error, handle them:
        if (msg.type === "item_ready") {
          const item = msg.item;

          // Convert absolute path -> /audio/<folder>/<file>
          if (item.audio_path && !item.audio_url) {
            const parts = item.audio_path.split(path.sep);
            const folder = parts[parts.length - 2];
            const file = parts[parts.length - 1];
            item.audio_url = `/audio/${folder}/${file}`;
          }

          job.items.push(item);
          emitter.emit("msg", { type: "item_ready", item });
        } else if (msg.type === "done") {
          job.done = true;
          job.meta = msg;
          emitter.emit("msg", msg);
          emitter.emit("end");

          const generationMs = Date.now() - job.startedAt;

          // ✅ podcast_id must match folder/file naming in TTS output
          const podcastId = msg.podcast_id || jobId; // use jobId if python didn't send one

          // ✅ public audio URL (since /audio maps to backend/tts_output)
          const audioUrl = `/audio/${podcastId}/${podcastId}.wav`;

          console.log("Podcast generated added into the db and server")
          await db.collection("podcasts").insertOne({
            podcast_id: podcastId,
            created_at: new Date().toISOString().slice(0, 10), // YYYY-MM-DD
            podcast_title: msg.podcast_title || "Daily Podcast",
            image_url: msg.image_url || null,
            audio_path: audioUrl,
            generation_time: generationMs,
          });

        } else if (msg.type === "error") {
          job.error = msg.error || "Unknown error";
          emitter.emit("msg", { type: "error", error: job.error });
          emitter.emit("end");
        } else {
          // fallback: forward anything else
          emitter.emit("msg", msg);
        }
      } catch (e) {
        // If python prints non-JSON logs to stdout, it will break streaming.
        // Keep logs on stderr only.
      }
    }
  });

  child.stderr.on("data", (d) => {
    stderr += d.toString();
    console.error("[PY STDERR]", d.toString().trim());
  });

  child.on("close", (code) => {
    const job = jobs.get(jobId);
    if (!job) return;

    // If python exits without sending done/error events
    if (!job.done && !job.error) {
      job.error = `Python exited with code ${code}`;
      emitter.emit("msg", { type: "error", error: job.error, stderr });
      emitter.emit("end");
    }
  });

  child.stdin.write(
    JSON.stringify({
      articles,
      user_pref,
      top_k: 5,
      model_endpoint: process.env.OPENROUTER_MODEL || "z-ai/glm-4.5-air:free",
      output_dir: process.env.TTS_OUTPUT_DIR || "tts_output",
      seen_train: [],
    })
  );
  child.stdin.end();

  return jobId;
}


// Function purpose: render the podcast page with preloaded daily podcasts to reduce waiting time for users.
router.get("/podcast", requireAuth, async (req, res) => {
  const db = await getDb();

  // if no user preference go back to preference setting page
  const prefDoc = await db.collection("preferences").findOne({ user_id: req.session.userId });
  if (!prefDoc?.preferences) return res.redirect("/preferences");

  // Load some latestt pre generated podcasts 
  const latestPodcast = await db
    .collection("podcasts")
    .findOne({}, { sort: { created_at: -1, _id: -1 } });


  res.render("podcast", {
    title: "Podcast",
    username: req.session.username,
    preloaded: latestPodcast ? [latestPodcast] : [],
  });
});

//Function Purpose: To start podcast generation
router.post("/podcast/start", requireAuth, async (req, res) => {
  try {
    const db = await getDb();

    const prefDoc = await db
      .collection("preferences")
      .findOne({ user_id: req.session.userId });

    if (!prefDoc?.preferences) {
      return res.status(400).json({ ok: false, error: "Preferences not set" });
    }

    const articles = await fetch30Articles();

    const jobId = startPythonPipelineJob({
      db,
      articles,
      user_pref: { preferences: prefDoc.preferences },
    });

    return res.json({ ok: true, jobId });
  } catch (err) {
    console.error("Error in /podcast/start:", err);
    return res.status(500).json({ ok: false, error: err.message || "Failed to start" });
  }
});

router.get("/podcast/events/:jobId", requireAuth, (req, res) => {
  const job = jobs.get(req.params.jobId);
  if (!job) return res.status(404).end();

  res.setHeader("Content-Type", "text/event-stream");
  res.setHeader("Cache-Control", "no-cache");
  res.setHeader("Connection", "keep-alive");

  const send = (obj) => res.write(`data: ${JSON.stringify(obj)}\n\n`);

  // Send any buffered items immediately
  for (const item of job.items) send({ type: "item_ready", item });

  if (job.done) {
    send({ type: "done", ...(job.meta || {}) });
    return res.end();
  }

  if (job.error) {
    send({ type: "error", error: job.error });
    return res.end();
  }

  const onMsg = (m) => send(m);
  const onEnd = () => res.end();

  job.emitter.on("msg", onMsg);
  job.emitter.once("end", onEnd);

  req.on("close", () => {
    job.emitter.off("msg", onMsg);
  });
});



export default router;
