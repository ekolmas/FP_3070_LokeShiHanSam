import express from "express";
import path from "path";
import { spawn } from "child_process";
import { getDb } from "../db.js";

const router = express.Router();

function requireAuth(req, res, next) {
  if (!req.session.userId) return res.redirect("/");
  next();
}

// --- helper: fetch 30 articles from NewsAPI (or your source) ---
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

// --- helper: call python main.py via stdin/stdout JSON ---
/*"""
    Expected payload from Node:
    {
      "articles": [ {newsapi-like article}, ... up to 30 ],
      "user_pref": { "preferences": { "sources": [...], "topics": [...], "style": [...] } },
      "model_endpoint": "z-ai/....",         # OPTIONAL
      "top_k": 5,                            # OPTIONAL
      "output_dir": "tts_output"             # OPTIONAL
    }
    """*/
function runPythonPipeline({ articles, user_pref }) {
  return new Promise((resolve, reject) => {
    const pythonExe = process.env.PYTHON_EXE || "python";

    // IMPORTANT: set correct path to your python main.py
    const scriptPath = path.join(
      process.cwd(),
      "../backend",
      "pipeline",
      "main.py"
    );

    const child = spawn(pythonExe, ["-u", scriptPath], {
      cwd: process.cwd(),
      env: {
        ...process.env,
        PYTHONUNBUFFERED: "1",
      },
    });


    let stdout = "";
    let stderr = "";

    child.stdout.on("data", (data) => {
      const text = data.toString();
      stdout += text;
      console.log("\x1b[36m[PYTHON]\x1b[0m", text.trim());
    });

    child.stderr.on("data", (data) => {
      const text = data.toString();
      stderr += text;
      console.error("\x1b[31m[PYTHON ERROR]\x1b[0m", text.trim());
    });


    child.on("error", (err) => {
      reject(err);
    });

    child.on("close", (code) => {
      // python prints JSON to stdout even on error
      try {
        const parsed = JSON.parse(stdout || "{}");
        if (code === 0 && parsed.ok) return resolve(parsed);

        // show python error message + stderr
        const msg = parsed.error || `Python exited with code ${code}`;
        return reject(new Error(`${msg}\n\nPY STDERR:\n${stderr}`));
      } catch (e) {
        return reject(
          new Error(
            `Failed to parse python output as JSON.\n\nSTDOUT:\n${stdout}\n\nSTDERR:\n${stderr}`
          )
        );
      }
    });

    // send JSON to python stdin
    const payload = {
      articles,
      user_pref,
      model_endpoint: process.env.OPENROUTER_MODEL || "z-ai/glm-4.5-air:free",
    };

    child.stdin.write(JSON.stringify(payload));
    child.stdin.end();
  });
}

// GET /podcast
router.get("/podcast", requireAuth, async (req, res) => {
  const db = await getDb();
  const doc = await db
    .collection("preferences")
    .findOne({ user_id: req.session.userId });

  // If no prefs -> redirect to /preferences
  if (!doc || !doc.preferences) return res.redirect("/preferences");

  try {
    // 1) get 30 articles
    const articles = await fetch30Articles();

    // 2) call python pipeline
    const result = await runPythonPipeline({
      articles,
      user_pref: { preferences: doc.preferences },
    });

    // 3) render
    res.render("podcast", {
      title: "Podcast",
      email: req.session.email,
      podcastTitle: result.podcast_title,
      imageUrl: result.image_url,
      recommended: result.recommended, // includes audio_path, title, url, etc
    });
  } catch (err) {
    console.error(err);
    res.status(500).render("error", {
      title: "Error",
      message: err.message,
    });
  }
});

export default router;
