const express = require('express');
const path = require('path');
const dotenv = require('dotenv');
const cookieParser = require('cookie-parser');
const userModel = require('./models/user');
const libraryModel = require('./models/library');
const authRoutes = require('./routes/auth');
const libraryRoutes = require('./routes/library');
const profileRoutes = require('./routes/profile');
const apiRoutes = require('./routes/api');
const requireAuth = require('./middleware/sessionAuth');
const runConsumer = require('./kafka_consumer');

const app = express();
const port = process.env.PORT || 3000;

// Initialize DB
userModel.createTable();
libraryModel.createLibraryTable();

// Start Kafka Consumer
runConsumer().catch(console.error);

// Middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(cookieParser());

app.use((req, res, next) => {
  console.log(`[User Service] Received request: ${req.method} ${req.url}`);
  next();
});

// View Engine
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));

// Routes
// We mount at both specific paths (for local dev) and root (for Ingress stripping)
app.use('/auth', authRoutes);
app.use('/library', requireAuth, libraryRoutes);
app.use('/profile', requireAuth, profileRoutes);
app.use('/api', requireAuth, apiRoutes); // Internal API
app.use('/', authRoutes);
app.use('/', requireAuth, libraryRoutes);
app.use('/', requireAuth, profileRoutes);
app.use('/', requireAuth, apiRoutes);

app.get('/', (req, res) => {
  res.render('index', { title: 'Home' });
});

// Catch-all for debugging
app.use((req, res) => {
  console.log(`[User Service] 404 - No route matched for ${req.method} ${req.url}`);
  res.status(404).send(`Cannot GET ${req.url} (User Service Debug)`);
});

app.listen(port, () => {
  console.log(`Server is running on port ${port}`);
});
