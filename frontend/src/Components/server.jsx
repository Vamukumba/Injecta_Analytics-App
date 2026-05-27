import express from 'express';
import cors from 'cors';
import { MongoClient } from 'mongodb';
import crypto from 'crypto';

const app = express();

// Allow React to talk to this server and parse JSON
app.use(cors());
app.use(express.json());

// --- 1. YOUR DATABASE CONNECTION ---
// Replace with your actual MongoDB connection string!
const MONGO_URI = "YOUR_MONGO_CONNECTION_STRING";
const client = new MongoClient(MONGO_URI);
let usersCollection;

async function connectDB() {
  try {
    await client.connect();
    const db = client.db('injecta_market_engine');
    usersCollection = db.collection('users');
    console.log("MongoDB Connected Successfully!");
  } catch (error) {
    console.error("DB Connection Error:", error);
  }
}
connectDB();

// --- 2. YOUR EXACT HASHING LOGIC ---
function makeHashes(password) {
  return crypto.createHash('sha256').update(String(password)).digest('hex');
}

function checkHashes(password, hashedText) {
  return makeHashes(password) === hashedText;
}

// --- 3. LOGIN & REGISTER ENDPOINTS ---
app.post('/api/register', async (req, res) => {
  const { username, password } = req.body;

  if (!usersCollection) {
    return res.status(500).json({ success: false, message: "Database not connected" });
  }

  const existingUser = await usersCollection.findOne({ username });
  if (existingUser) {
    return res.status(400).json({ success: false, message: "Username already taken" });
  }

  await usersCollection.insertOne({
    username: username,
    password: makeHashes(password)
  });

  res.json({ success: true, message: "User created successfully!" });
});

app.post('/api/login', async (req, res) => {
  const { username, password } = req.body;

  if (!usersCollection) {
    return res.status(500).json({ success: false, message: "Database not connected" });
  }

  const user = await usersCollection.findOne({ username });
  
  if (user && checkHashes(password, user.password)) {
    res.json({ success: true, message: "Login successful!" });
  } else {
    res.status(401).json({ success: false, message: "Invalid credentials" });
  }
});

// Start the server
const PORT = 5000;
app.listen(PORT, () => {
  console.log(`JavaScript Backend running on http://localhost:${PORT}`);
});                                                                