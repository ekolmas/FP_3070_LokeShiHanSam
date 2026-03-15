//Router for authentication with GET auth/signin, GET auth/signup, POST auth/signin, POST auth/signup, GET post-login, GET logout 
import express from "express";
import bcrypt from "bcrypt";
import { getDb } from "../db.js";

const router = express.Router();

// GET /signin renders signin page or redirects to /post-login if already signed in
router.get("/signin", (req, res) => {
    if (req.session.userId) {
        return res.redirect("/post-login")
    };
    res.render("signin", { title: "Sign In", error: null });
});

// GET /signup renders signup page or redirects to /post-login if already signed in
router.get("/signup", (req, res) => {
    if (req.session.userId) {
        return res.redirect("/post-login")
    };
    res.render("signup", { title: "Sign Up", error: null });
});

// POST /auth/signup creates new user, hashes password and stores in db
// User is logged in immediately
router.post("/auth/signup", async (req, res) => {
    try {
        // get username and password from form
        const { username, password } = req.body;

        // validation to check if username and password are provided
        if (!username || !password) {
            return res.status(400).render("signup", { title: "Sign Up", error: "Missing username or password" });
        }

        const db = await getDb();
        const users = db.collection("users");

        // Check if username already exists
        const userExists = await users.findOne({ username });
        if (userExists) {
            return res.status(400).render("signup", { title: "Sign Up", error: "Username already taken" });
        }

        // Hash password with bcrypt with 10 salt rounds
        const password_hash = await bcrypt.hash(password, 10);

        // insert new user into db
        const r = await users.insertOne({
            username,
            password_hash,
            created_at: new Date(),
        });

        // login user immediately by setting session and redirecting to post-login
        req.session.userId = String(r.insertedId);
        req.session.username = username;

        res.redirect("/post-login");
    } catch (e) {
        console.error("Sign Up Error:", e);
        res.status(500).render("signup", { title: "Sign Up", error: e.message });
    }
});

// POST /auth/signin authenticates user, sets sessions and redirect to /post-login
router.post("/auth/signin", async (req, res) => {
    try {
        // get username and password from form
        const { username, password } = req.body;

        const db = await getDb();
        const users = db.collection("users");

        // get user from db by username
        const user = await users.findOne({ username });
        // if user not found, return error 
        if (!user) {
            return res.status(401).render("signin", { title: "Sign In", error: "Invalid username or password" });
        }

        // compare password with hash in db using bcrypt
        const ok = await bcrypt.compare(password, user.password_hash);
        // if password does not match, return error
        if (!ok) {
            return res.status(401).render("signin", { title: "Sign In", error: "Invalid username or password" });
        }

        // set session and redirect to post-login
        req.session.userId = String(user._id);
        req.session.username = user.username;

        res.redirect("/post-login");
    } catch (e) {
        console.error("Sign In Error:", e);
        res.status(500).render("signin", { title: "Sign In", error: e.message });
    }
});

// GET /post-login checks if user entered preferences, if not redirect to /preferences, else redirect to /podcast
router.get("/post-login", async (req, res) => {
    // if not logged in redirect to signin
    if (!req.session.userId) return res.redirect("/signin");

    const db = await getDb();
    const prefs = db.collection("preferences");

    // check if user has preferences set
    const preferenceExists = await prefs.findOne({ user_id: req.session.userId });

    // if no preference go to preference setting page
    if (!preferenceExists) {
        return res.redirect("/preferences")
    };

    // else go to podcast page
    return res.redirect("/podcast");
});

// GET /logout destroys session and redirects to signin
router.get("/logout", (req, res) => {
    req.session.destroy(() => res.redirect("/signin"));
});

export default router;
