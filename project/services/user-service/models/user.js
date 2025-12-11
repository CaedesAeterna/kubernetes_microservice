const pool = require('../config/db');

const createTable = async () => {
  const query = `
    CREATE TABLE IF NOT EXISTS users (
      id SERIAL PRIMARY KEY,
      username VARCHAR(100) UNIQUE NOT NULL,
      password VARCHAR(100) NOT NULL,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
  `;
  try {
    await pool.query(query);
    console.log("Users table created successfully");
  } catch (err) {
    console.error("Error creating users table", err);
  }
};

const createUser = async (username, password) => {
  const query = 'INSERT INTO users (username, password) VALUES ($1, $2) RETURNING *';
  const values = [username, password];
  const res = await pool.query(query, values);
  return res.rows[0];
};

const findUserByUsername = async (username) => {
  const query = 'SELECT * FROM users WHERE username = $1';
  const res = await pool.query(query, [username]);
  return res.rows[0];
};

module.exports = {
  createTable,
  createUser,
  findUserByUsername,
};
