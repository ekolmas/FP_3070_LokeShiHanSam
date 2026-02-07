import express from "express";
import path from "path";
import dotenv from "dotenv";
import session from "express-session";
import MongoStore from "connect-mongo";
import morgan from "morgan";
//Import the other routes
import authRouter from "./routes/auth.js";
import preferencesRouter from "./routes/preferences.js";
import podcastRouter from "./routes/podcast.js";

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3000;

// View engine
app.set("view engine", "ejs");
app.set("views", path.join(process.cwd(), "src", "views"));

// Middleware
app.use(express.urlencoded({ extended: true }));
app.use(express.json());
app.use("/public", express.static(path.join(process.cwd(), "src", "public")));
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
app.use("/audio", express.static(path.join(process.cwd(), "tts_output")));

app.listen(PORT, () => {
    console.log(`Server running: http://localhost:${PORT}`);
});

app.get("/", (req, res) => { res.redirect("/signin") });
