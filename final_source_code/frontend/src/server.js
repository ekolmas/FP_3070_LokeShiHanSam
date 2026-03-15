// Main entry point for the Express server. Sets up middleware, session handling and routes
import express from "express";
import path from "path";
import dotenv from "dotenv";
import session from "express-session";
import MongoStore from "connect-mongo";
import morgan from "morgan";

//Import the other routers
import authRouter from "./routes/auth.js";
import preferencesRouter from "./routes/preferences.js";
import podcastRouter from "./routes/podcast.js";

dotenv.config();

// initialize express app
const app = express();
const PORT = process.env.PORT || 3000;

// initialize view engine EJS
app.set("view engine", "ejs");
// Set views directory to src/views
app.set("views", path.join(process.cwd(), "src", "views"));

// Initialize middleware
app.use(express.urlencoded({ extended: true }));
app.use(express.json());

// Serve static files from src/public and tts_output for audio
app.use("/public", express.static(path.join(process.cwd(), "src", "public")));
app.use("/audio", express.static(path.join(process.cwd(), "tts_output")));

// Use morgan for logging in development
app.use(morgan("dev"));

// express session stored in mongo
app.use(
    session({
        secret: process.env.SESSION_SECRET,
        resave: false,
        saveUninitialized: false,
        store: MongoStore.create({
            mongoUrl: process.env.MONGO_URI,
            dbName: process.env.MONGO_DB,
            collectionName: "sessions",
        }),
        cookie: { httpOnly: true },
    })
);

// Routes
app.use("/", authRouter);
app.use("/", preferencesRouter);
app.use("/", podcastRouter);

// Start server
app.listen(PORT, () => {
    console.log(`Server running: http://localhost:${PORT}`);
});

// Default route redirects to signin
app.get("/", (req, res) => { res.redirect("/signin") });
