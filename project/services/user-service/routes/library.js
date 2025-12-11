const express = require('express');
const router = express.Router();
const libraryModel = require('../models/library');
const userModel = require('../models/user');

// Middleware to check if user is "logged in" (Simulated via cookie or query param for this MVP)
// For simplicity in this CLI context, we will ask for username in query or body, 
// or assume a 'session' if we had a browser with cookies. 
// REAL WORLD: Use JWT or Session Cookies.
// MVP HACK: We'll accept ?username=... query param to identify the user for GET routes.

router.get('/', async (req, res) => {
  const username = req.cookies.username || req.query.username;
  console.log(`[Library] Fetching library for user: ${username}`);
  
  if (!username) return res.redirect('/auth/login');

  try {
    const user = await userModel.findUserByUsername(username);
    if (!user) {
        console.log(`[Library] User not found: ${username}`);
        return res.redirect('/auth/login');
    }

    const library = await libraryModel.getUserLibrary(user.id);
    console.log(`[Library] Found ${library.length} items for ${username}`);
    res.render('library', { title: 'My Library', library, username });
  } catch (err) {
    console.error("[Library] Error:", err);
    res.status(500).send("Server Error");
  }
});

router.get('/history', async (req, res) => {
  const username = req.cookies.username;
  const { title } = req.query; // Optional filter by title

  if (!username) return res.redirect('/auth/login');

  try {
    const user = await userModel.findUserByUsername(username);
    if (!user) return res.redirect('/auth/login');

    let history;
    if (title) {
        history = await libraryModel.getHistoryByTitle(user.id, title);
    } else {
        history = await libraryModel.getHistory(user.id);
    }
    
    res.render('history', { title: 'History', history, username, filterTitle: title });
  } catch (err) {
    console.error("[History] Error:", err);
    res.status(500).send("Server Error");
  }
});

router.post('/add', async (req, res) => {
  const username = req.cookies.username || req.body.username;
  const { mediaId, mediaTitle, mediaType, status } = req.body;
  console.log(`[Library] Adding item: ${mediaTitle} (${mediaType}) for user: ${username}`);

  try {
    const user = await userModel.findUserByUsername(username);
    if (!user) return res.status(400).send("User not found");

    await libraryModel.addToLibrary(user.id, mediaId, mediaTitle, mediaType, status);
    console.log(`[Library] Item added successfully`);
    res.redirect(`/library`);
  } catch (err) {
    console.error("[Library] Error adding item:", err);
    res.status(500).send("Error adding to library");
  }
});

router.post('/update', async (req, res) => {
    // rating might be "" if left empty in the form. Convert to null for DB.
    let { id, username, status, progress, rating } = req.body;
    
    if (rating === "") {
        rating = null;
    }

    try {
        await libraryModel.updateEntry(id, status, progress, rating);
        res.redirect(`/library`);
    } catch (err) {
        console.error(err);
        res.status(500).send("Error updating entry");
    }
});

module.exports = router;
