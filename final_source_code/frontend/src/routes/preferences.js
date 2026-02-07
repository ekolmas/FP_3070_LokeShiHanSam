import express from "express";
import { getDb } from "../db.js";

const router = express.Router();

function requireAuth(req, res, next) {
  if (!req.session.userId) return res.redirect("/signin"); // better than "/"
  next();
}

// Predefined options (you control these)
const TOPIC_OPTIONS = [
  "technology",
  "business",
  "world",
  "sports",
  "science",
  "health",
  "entertainment",
];

const SOURCE_OPTIONS = [
  "bbc",
  "reuters",
  "cnn",
  "the-verge",
  "techcrunch",
  "espn",
];

const STYLE_OPTIONS = ["breaking", "recap", "analysis", "daily"];

router.get("/preferences", requireAuth, async (req, res) => {
  const db = await getDb();
  const existing = await db
    .collection("preferences")
    .findOne({ user_id: req.session.userId });

  const prefs = existing?.preferences || { topics: [], sources: [], style: ["daily"] };

  res.render("preferences", {
    title: "Preferences",
    username: req.session.username || req.session.email, // depending on your auth
    prefs,
    TOPIC_OPTIONS,
    SOURCE_OPTIONS,
    STYLE_OPTIONS,
  });
});

// POST /preferences -> save -> /podcast
router.post("/preferences", requireAuth, async (req, res) => {
  // When using checkboxes:
  // - if user checks 1 box => string
  // - if user checks many => array
  // - if none => undefined
  const toArray = (v) => {
    if (!v) return [];
    return Array.isArray(v) ? v : [v];
  };

  const topics = toArray(req.body.topics).filter((t) => TOPIC_OPTIONS.includes(t));
  const sources = toArray(req.body.sources).filter((s) => SOURCE_OPTIONS.includes(s));
  const style = toArray(req.body.style).filter((st) => STYLE_OPTIONS.includes(st));


  const db = await getDb();
  await db.collection("preferences").updateOne(
    { user_id: req.session.userId },
    {
      $set: {
        user_id: req.session.userId,
        // store username/email if you want, but no duration
        username: req.session.username,
        preferences: { sources, topics, style },
        updated_at: new Date(),
      },
    },
    { upsert: true }
  );

  res.redirect("/podcast");
});

export default router;
