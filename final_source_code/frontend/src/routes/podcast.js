// Router for podcast page with GET /podcast, POST /podcast/start and GET /podcast/events/:jobId
// This file also runs the python pipeline and retrieve news articles from NewsAPI
import express from "express";
import path from "path";
import { spawn } from "child_process";
import { getDb } from "../db.js";

const router = express.Router();

import EventEmitter from "events";
import { randomUUID } from "crypto";

//job id to track state of each generation, allowing front end to display progress
const jobs = new Map();

// Function purpose: check if user is authenticated
function requireAuth(req, res, next) {
  if (!req.session.userId) {
    return res.redirect("/")
  };
  next();
}

// Function purpose: fetch 30 news articles from NewsAPI for AI podcast generation pipeline
async function fetch30Articles() {
  // get API key from env
  const apiKey = process.env.NEWSAPI_KEY;
  if (!apiKey) throw new Error("Missing NEWSAPI_KEY in .env");

  // fetch top 30 tech news articles
  const url =
    `https://newsapi.org/v2/top-headlines?` +
    new URLSearchParams({
      language: "en",
      pageSize: "30",
      category: "technology",
    });

  // call NewsAPI with API key in header
  const resp = await fetch(url, {
    headers: { "X-Api-Key": apiKey },
  });

  // handle NewsAPI errors
  if (!resp.ok) {
    const error = await resp.text();
    throw new Error(`NewsAPI error: ${error}`);
  }

  // return array of articles
  const data = await resp.json();
  return data.articles;
}

//Function purpose: start python pipeline and return jobId to track progress
function startPythonPipelineJob({ db, articles, user_pref }) {
  // Generate random unique job ID
  const jobId = randomUUID();
  // Create event emitter
  const emitter = new EventEmitter();

  //create job to track state of python pipeline 
  jobs.set(jobId, {
    emitter,
    items: [],
    done: false,
    error: null,
    meta: null,
    startedAt: Date.now(),
  });

  // Start python pipeline as child process
  const pythonExe = process.env.PYTHON_EXE || "python";
  const scriptPath = path.join(process.cwd(), "../backend", "pipeline", "main.py");

  const child = spawn(pythonExe, ["-u", scriptPath], {
    cwd: process.cwd(),
    env: { ...process.env, PYTHONUNBUFFERED: "1" },
  });

  let buf = "";
  let stderr = "";

  // Listen to stdout for messages from python pipeline
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

        // when python emits item_ready，done or error, update job state
        if (msg.type === "item_ready") {
          const item = msg.item;

          // Convert output path to static path /audio/<folder>/<file>
          if (item.audio_path && !item.audio_url) {
            const parts = item.audio_path.split(path.sep);
            const folder = parts[parts.length - 2];
            const file = parts[parts.length - 1];
            item.audio_url = `/audio/${folder}/${file}`;
          }

          // Emit item_ready event for frontend
          job.items.push(item);
          emitter.emit("msg", { type: "item_ready", item });
        }
        // if python emits done, mark job as done and store metadata into mongodb for other users to retrieve
        else if (msg.type === "done") {
          job.done = true;
          job.meta = msg;
          emitter.emit("msg", msg);
          emitter.emit("end");

          const generationMs = Date.now() - job.startedAt;

          //podcast_id must match naming in TTS output
          const podcastId = msg.podcast_id; // use jobId if python didn't send one

          //public static audio URL
          const audioUrl = `/audio/${podcastId}/${podcastId}.wav`;

          console.log("Podcast generated added into the db and server")

          // Store podcast metadata into MongoDB
          await db.collection("podcasts").insertOne({
            podcast_id: podcastId,
            created_at: new Date().toISOString().slice(0, 10), // YYYY-MM-DD
            podcast_title: msg.podcast_title || "Daily Podcast",
            image_url: msg.image_url || null,
            audio_path: audioUrl,
            generation_time: generationMs,
          });

        }
        // if python emits error, emit error
        else if (msg.type === "error") {
          job.error = msg.error || "Unknown error";
          emitter.emit("msg", { type: "error", error: job.error });
          emitter.emit("end");
        }
        // if python emits anything else
        else {
          // fallback: forward anything else
          emitter.emit("msg", msg);
        }
      } catch (e) {
        console.error("Python error:", e);
      }
    }
  });

  // listen for stderr from python process
  child.stderr.on("data", (error) => {
    stderr += error.toString();
    console.error("Error", error.toString().trim());
  });

  // listen for python process exit
  child.on("close", (code) => {
    const job = jobs.get(jobId);
    if (!job) return;

    if (code !== 0 && !job.done && !job.error) {
      job.error = `Python exited with code ${code}`;
      emitter.emit("msg", { type: "error", error: errText });
      emitter.emit("end");
    }
  });

  //  send data to python process to start pipeline
  child.stdin.write(
    JSON.stringify({
      articles,
      user_pref,
      model_endpoint: process.env.OPENROUTER_MODEL || "z-ai/glm-4.5-air:free",
    })
  );
  child.stdin.end();

  // Return jobId to update frontend on progress
  return jobId;
}


// /podcast renders podcast page, if no user preference go back to preference setting page
// Loads the latest generated podcast to reduce waiting time for users
router.get("/podcast", requireAuth, async (req, res) => {
  const db = await getDb();

  // if no user preference go back to preference setting page
  const prefDoc = await db.collection("preferences").findOne({ user_id: req.session.userId });
  if (!prefDoc?.preferences) return res.redirect("/preferences");

  // Load some latestt pre generated podcasts 
  const latestPodcast = await db
    .collection("podcasts")
    .findOne({}, { sort: { created_at: -1, _id: -1 } });

  // Render podcast page with latest podcast preloaded
  res.render("podcast", {
    title: "Podcast",
    username: req.session.username,
    preloaded: latestPodcast ? [latestPodcast] : [],
  });
});

// POST /podcast/start starts the python pipeline and returns jobId to track progress
router.post("/podcast/start", requireAuth, async (req, res) => {
  try {
    const db = await getDb();

    // get user preferences from db, if no preferences return error
    const prefDoc = await db
      .collection("preferences")
      .findOne({ user_id: req.session.userId });

    if (!prefDoc?.preferences) {
      return res.status(400).json({ ok: false, error: "Preferences not set" });
    }

    // fetch 30 news articles from NewsAPI
    const articles = await fetch30Articles();

    // start python pipeline and get jobID to track progress
    const jobId = startPythonPipelineJob({
      db,
      articles,
      user_pref: { preferences: prefDoc.preferences },
    });

    // Return jobId to frontend to track progress
    return res.json({ ok: true, jobId });
  } catch (err) {
    console.error("Error", err);
    return res.status(500).json({ ok: false, error: err.message });
  }
});

// GET /podcast/events/:jobId listens for events from python pipeline for frontend real time updates
router.get("/podcast/events/:jobId", requireAuth, (req, res) => {
  // get and check job exists, if not return 404
  const job = jobs.get(req.params.jobId);
  if (!job) return res.status(404).end();

  // Set headers for response, to make sure evenet stream is not cached and connection is kept alive
  res.setHeader("Content-Type", "text/event-stream");
  res.setHeader("Cache-Control", "no-cache");
  res.setHeader("Connection", "keep-alive");

  // function to send message to frontend
  const send = (obj) => res.write(`data: ${JSON.stringify(obj)}\n\n`);

  // Send any buffered items immediately
  for (const item of job.items) send({ type: "item_ready", item });

  // if job is done, send message immediately
  if (job.done) {
    send({ type: "done", ...(job.meta || {}) });
    return res.end();
  }

  // if job has error, send error message immediately
  if (job.error) {
    send({ type: "error", error: job.error });
    return res.end();
  }

  // function to listen for messages and send to frontend
  const onMsg = (m) => send(m);
  // function to listen when job ends, end response and close connection to frontend
  const onEnd = () => res.end();

  job.emitter.on("msg", onMsg);
  job.emitter.once("end", onEnd);

  // if connections is closed, remove listeners
  req.on("close", () => {
    job.emitter.off("msg", onMsg);
  });
});



export default router;
