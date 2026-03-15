// Router to handle user preferences with GET /preferences and POST /preferences
import express from "express";
import { getDb } from "../db.js";

const router = express.Router();

function requireAuth(req, res, next) {
  if (!req.session.userId) return res.redirect("/signin"); // better than "/"
  next();
}

// topic options
const TOPIC_OPTIONS = [
  "technology",
  "business",
  "world",
  "sports",
  "science",
  "health",
  "entertainment",
];

// source options
const SOURCE_OPTIONS = [
  "bbc",
  "reuters",
  "cnn",
  "the-verge",
  "techcrunch",
  "espn",
];

// style options
const STYLE_OPTIONS = ["breaking", "recap", "analysis", "daily"];

// GET /preference renders preference page with existing preferences if any
router.get("/preferences", requireAuth, async (req, res) => {
  // get existing preferences from db if any
  const db = await getDb();
  const existing = await db
    .collection("preferences")
    .findOne({ user_id: req.session.userId });

  // if no existing preferences use empty defaults
  const prefs = existing?.preferences || { topics: [], sources: [], style: ["daily"] };

  // render preferences page with options and existing preferences
  res.render("preferences", {
    title: "Preferences",
    username: req.session.username,
    prefs,
    TOPIC_OPTIONS,
    SOURCE_OPTIONS,
    STYLE_OPTIONS,
  });
});

// POST /preferences saves user preferences to db and redirect to /podcast
router.post("/preferences", requireAuth, async (req, res) => {
  // Function to convert checkbox values to array
  const toArray = (value) => {
    if (!value) return [];
    return Array.isArray(value) ? value : [value];
  };

  const topics = toArray(req.body.topics).filter((t) => TOPIC_OPTIONS.includes(t));
  const sources = toArray(req.body.sources).filter((s) => SOURCE_OPTIONS.includes(s));
  const style = toArray(req.body.style).filter((st) => STYLE_OPTIONS.includes(st));

  // Save preferences to db
  const db = await getDb();
  await db.collection("preferences").updateOne(
    { user_id: req.session.userId },
    {
      $set: {
        user_id: req.session.userId,
        username: req.session.username,
        preferences: { sources, topics, style },
        updated_at: new Date(),
      },
    },
    // upsert creates new doc if no existing, updates if existing
    { upsert: true }
  );

  // Redirect to podcast page after saving preferences
  res.redirect("/podcast");
});

export default router;
