const express = require('express');
const router = express.Router();
const bcrypt = require('bcryptjs');
const userModel = require('../models/user');
const producer = require('../config/kafka');

router.get('/login', (req, res) => {
  res.render('login', { title: 'Login' });
});

router.post('/login', async (req, res) => {
  const { username, password } = req.body;
  try {
    const user = await userModel.findUserByUsername(username);
    if (!user) {
      return res.status(401).send('Invalid credentials');
    }
    const isMatch = await bcrypt.compare(password, user.password);
    if (!isMatch) {
      return res.status(401).send('Invalid credentials');
    }
    // REDIRECT TO LIBRARY PAGE
    console.log(`[Auth] Login successful for ${username}. Setting cookie and redirecting...`);
    
    // Set Cookie (HttpOnly is safer, but for this simple multi-service demo without shared secret/JWT, 
    // we'll keep it simple. Path=/ ensures Media Service can see it too if on same domain)
    res.cookie('username', user.username, { path: '/', httpOnly: true });
    
    res.redirect(`/library`);
  } catch (err) {
    console.error(err);
    res.status(500).send('Server Error');
  }
});

router.get('/logout', (req, res) => {
  console.log(`[Auth] Logging out user`);
  res.clearCookie('username', { path: '/' });
  res.redirect('/auth/login');
});

router.get('/register', (req, res) => {
  res.render('register', { title: 'Register' });
});

router.post('/register', async (req, res) => {
  const { username, password } = req.body;
  try {
    const existingUser = await userModel.findUserByUsername(username);
    if (existingUser) {
      return res.status(400).send('User already exists');
    }
    const hashedPassword = await bcrypt.hash(password, 10);
    const newUser = await userModel.createUser(username, hashedPassword);
    
    // Send Kafka Event
    await producer.send({
      topic: 'user-registered',
      messages: [
        { value: JSON.stringify({ userId: newUser.id, username: newUser.username }) },
      ],
    });
    console.log(`Event sent: user-registered for ${newUser.username}`);

    res.redirect('/auth/login');
  } catch (err) {
    console.error(err);
    res.status(500).send('Server Error');
  }
});

module.exports = router;
