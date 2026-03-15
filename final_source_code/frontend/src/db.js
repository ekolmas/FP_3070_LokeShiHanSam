// This file connects to MongoDB and exports a function to get the database instance
import dotenv from "dotenv";
import { MongoClient, ObjectId } from "mongodb";

// Load .env here so this file is safe to import anywhere
dotenv.config();

const MONGO_URI = process.env.MONGO_URI;
const MONGO_DB = process.env.MONGO_DB;

if (!MONGO_URI) throw new Error("Missing MONGO_URI in .env");
if (!MONGO_DB) throw new Error("Missing MONGO_DB in .env");

let client;
let db;

// Function purpose: Get the database instance, connecting to MongoDB if not already connected
// Other files can use this function to get the db instance
export async function getDb() {
    if (!client) client = new MongoClient(MONGO_URI);
    if (!db) {
        await client.connect();
        db = client.db(MONGO_DB);
    }
    return db;
}

// Export ObjectId for in other files that need MongoDB IDs
export { ObjectId };
