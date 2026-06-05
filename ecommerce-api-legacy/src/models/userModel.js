class UserModel {
  constructor(db) {
    this.db = db;
  }

  async findByEmail(email) {
    return this.db.get('SELECT * FROM users WHERE email = ?', [email]);
  }

  async findById(id) {
    return this.db.get('SELECT * FROM users WHERE id = ?', [id]);
  }

  async create(name, email, hashedPassword) {
    const result = await this.db.run(
      'INSERT INTO users (name, email, pass) VALUES (?, ?, ?)',
      [name, email, hashedPassword]
    );
    return result.lastID;
  }

  async deleteById(id) {
    return this.db.run('DELETE FROM users WHERE id = ?', [id]);
  }

  static toPublic(user) {
    if (!user) return null;
    const { pass, ...publicData } = user;
    return publicData;
  }
}

module.exports = UserModel;
