// utils/db.js
const mysql = require('mysql2');

// Create a connection pool with automatic handling of dropped connections
const connection = mysql.createPool({
  host: 'HOST',
  user: 'readonly',
  password: 'PASSWORD',
  database: 'gett',
  waitForConnections: true, // wait for connection if pool is busy
  connectionLimit: 10, // limit the number of connections in the pool
  queueLimit: 0, // no limit for waiting requests
});

// Handle disconnections and reconnect automatically
connection.on('error', (err) => {
  if (err.code === 'PROTOCOL_CONNECTION_LOST') {
    console.error('Database connection was closed.');
  } else if (err.code === 'ER_CON_COUNT_ERROR') {
    console.error('Database has too many connections.');
  } else if (err.code === 'ECONNREFUSED') {
    console.error('Database connection was refused.');
  } else {
    console.error('Unexpected MySQL error:', err);
  }
});

// Export the connection for use in other modules
module.exports = connection; // Using `.promise()` for promise-based queries
