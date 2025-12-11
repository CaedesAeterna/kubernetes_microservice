const express = require('express');
const router = express.Router();
const userModel = require('../models/user');
const libraryModel = require('../models/library');

router.get('/', async (req, res) => {
  const username = req.cookies.username;
  if (!username) return res.redirect('/auth/login');

  try {
    const user = await userModel.findUserByUsername(username);
    if (!user) return res.redirect('/auth/login');

    const rawStats = await libraryModel.getStats(user.id);
    
    // Process stats for display
    const stats = {
        total: 0,
        avgRating: 0,
        byType: {},
        byStatus: {}
    };

    let ratingSum = 0;
    let ratingCount = 0;

    rawStats.forEach(row => {
        const count = parseInt(row.total_items);
        stats.total += count;
        
        // Type breakdown
        if (!stats.byType[row.media_type]) stats.byType[row.media_type] = 0;
        stats.byType[row.media_type] += count;

        // Status breakdown
        if (!stats.byStatus[row.status]) stats.byStatus[row.status] = 0;
        stats.byStatus[row.status] += count;

        // Avg Rating Calc
        if (row.avg_rating) {
            ratingSum += (parseFloat(row.avg_rating) * count);
            ratingCount += count;
        }
    });

    stats.avgRating = ratingCount > 0 ? (ratingSum / ratingCount).toFixed(1) : "N/A";

    res.render('profile', { title: 'My Profile', user, stats, username });
  } catch (err) {
    console.error(err);
    res.status(500).send("Server Error");
  }
});

module.exports = router;
