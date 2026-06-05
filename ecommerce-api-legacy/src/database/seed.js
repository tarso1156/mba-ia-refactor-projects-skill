const { hashPassword } = require('../services/passwordService');

async function seed(db) {
  const user = await db.get("SELECT COUNT(*) as count FROM users");
  if (user.count > 0) return;

  const hashedPassword = await hashPassword('123');

  await db.run(
    "INSERT INTO users (name, email, pass) VALUES (?, ?, ?)",
    ['Leonan', 'leonan@fullcycle.com.br', hashedPassword]
  );
  await db.run(
    "INSERT INTO courses (title, price, active) VALUES (?, ?, ?), (?, ?, ?)",
    ['Clean Architecture', 997.00, 1, 'Docker', 497.00, 1]
  );
  await db.run(
    "INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)",
    [1, 1]
  );
  await db.run(
    "INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)",
    [1, 997.00, 'PAID']
  );

  console.log('[Seed] Database seeded successfully');
}

module.exports = { seed };
