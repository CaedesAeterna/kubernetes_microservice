const express = require('express');
const router = express.Router();
const libraryModel = require('../models/library');
const userModel = require('../models/user');

router.get('/', async (req, res) => {
  const username = req.cookies.username;
  if (!username) return res.redirect('/auth/login');

  try {
    const user = await userModel.findUserByUsername(username);
    const rawStats = await libraryModel.getStats(user.id);
    const library = await libraryModel.getUserLibrary(user.id); // For recent activity
    
    let total = 0;
    let ratingSum = 0;
    let ratingCount = 0;
    const byType = {};
    const byStatus = {};

    rawStats.forEach(row => {
        const count = parseInt(row.total_items);
        total += count;
        
        // Avg Rating logic (row.avg_rating is per group)
        if (row.avg_rating) {
            ratingSum += parseFloat(row.avg_rating) * count;
            ratingCount += count;
        }

        // By Type
        if (row.media_type) {
            byType[row.media_type] = (byType[row.media_type] || 0) + count;
        }

        // By Status
        if (row.status) {
            byStatus[row.status] = (byStatus[row.status] || 0) + count;
        }
    });

    const avgRating = ratingCount > 0 ? (ratingSum / ratingCount).toFixed(1) : 0;

    res.render('profile', { 
        title: 'My Profile', 
        username, 
        user,
        stats: { total, avgRating, byType, byStatus },
        recent: library.slice(0, 5) 
    });
  } catch (err) {
    console.error(err);
    res.status(500).send("Server Error");
  }
});

router.get('/edit', async (req, res) => {
    const username = req.cookies.username;
    if (!username) return res.redirect('/auth/login');
    
    try {
        const user = await userModel.findUserByUsername(username);
        res.render('profile_edit', { title: 'Edit Profile', username, user });
    } catch (err) {
        console.error(err);
        res.redirect('/profile');
    }
});

router.post('/edit', async (req, res) => {
    const username = req.cookies.username;
    const { email, bio } = req.body;
    
    try {
        await userModel.updateUser(username, email, bio);
        res.redirect('/profile');
    } catch (err) {
        console.error(err);
        res.status(500).send("Error updating profile");
    }
});

module.exports = router;
