import express from "express";
import bcrypt from "bcrypt";
import { getDb } from "../db.js";

const router = express.Router();

// GET /signin
router.get("/signin", (req, res) => {
    if (req.session.userId) return res.redirect("/post-login");
    res.render("signin", { title: "Sign In", error: null });
});

// GET /signup
router.get("/signup", (req, res) => {
    if (req.session.userId) return res.redirect("/post-login");
    res.render("signup", { title: "Sign Up", error: null });
});

// POST /auth/signup -> create user
router.post("/auth/signup", async (req, res) => {
    try {
        const { username, password } = req.body;

        if (!username || !password) {
            return res.status(400).render("signup", { title: "Sign Up", error: "Missing username or password" });
        }

        const db = await getDb();
        const users = db.collection("users");

        // Check if username already exists
        const existing = await users.findOne({ username });
        if (existing) {
            return res.status(400).render("signup", { title: "Sign Up", error: "Username already taken" });
        }

        // Hash password
        const password_hash = await bcrypt.hash(password, 10);

        const r = await users.insertOne({
            username,
            password_hash,
            created_at: new Date(),
        });

        // Log in immediately after signup (optional)
        req.session.userId = String(r.insertedId);
        req.session.username = username;

        res.redirect("/post-login");
    } catch (e) {
        console.error("SIGNUP ERROR:", e);
        res.status(500).render("signup", { title: "Sign Up", error: e.message });
    }
});

// POST /auth/signin -> verify user
router.post("/auth/signin", async (req, res) => {
    try {
        const { username, password } = req.body;

        const db = await getDb();
        const users = db.collection("users");

        const user = await users.findOne({ username });
        if (!user) {
            return res.status(401).render("signin", { title: "Sign In", error: "Invalid username or password" });
        }

        const ok = await bcrypt.compare(password, user.password_hash);
        if (!ok) {
            return res.status(401).render("signin", { title: "Sign In", error: "Invalid username or password" });
        }

        req.session.userId = String(user._id);
        req.session.username = user.username;

        res.redirect("/post-login");
    } catch (e) {
        console.error("SIGNIN ERROR:", e);
        res.status(500).render("signin", { title: "Sign In", error: e.message });
    }
});

// GET /post-login -> if no preferences -> /preferences else /podcast
router.get("/post-login", async (req, res) => {
    if (!req.session.userId) return res.redirect("/signin");

    const db = await getDb();
    const prefs = db.collection("preferences");

    const existing = await prefs.findOne({ user_id: req.session.userId });

    if (!existing) return res.redirect("/preferences");
    return res.redirect("/podcast");
});

// GET /logout
router.get("/logout", (req, res) => {
    req.session.destroy(() => res.redirect("/signin"));
});

export default router;
