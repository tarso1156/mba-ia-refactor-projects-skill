const bcrypt = require('bcrypt');

const SALT_ROUNDS = 10;

async function hashPassword(password) {
  return bcrypt.hash(password, SALT_ROUNDS);
}

async function verifyPassword(password, hashed) {
  return bcrypt.compare(password, hashed);
}

module.exports = { hashPassword, verifyPassword };
