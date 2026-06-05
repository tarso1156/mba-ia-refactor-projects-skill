class ReportController {
  constructor(db) {
    this.db = db;
  }

  async getFinancialReport() {
    const query = `
      SELECT
        c.id as course_id, c.title as course_title,
        e.id as enrollment_id,
        u.name as user_name,
        p.amount as payment_amount, p.status as payment_status
      FROM courses c
      LEFT JOIN enrollments e ON e.course_id = c.id
      LEFT JOIN users u ON u.id = e.user_id
      LEFT JOIN payments p ON p.enrollment_id = e.id
    `;

    const rows = await this.db.all(query);

    // Group by course
    const coursesMap = {};
    for (const row of rows) {
      if (!coursesMap[row.course_id]) {
        coursesMap[row.course_id] = {
          course: row.course_title,
          revenue: 0,
          students: [],
        };
      }

      if (row.enrollment_id && row.payment_status === 'PAID') {
        coursesMap[row.course_id].revenue += row.payment_amount || 0;
      }

      if (row.enrollment_id) {
        coursesMap[row.course_id].students.push({
          student: row.user_name || 'Unknown',
          paid: row.payment_status === 'PAID' ? (row.payment_amount || 0) : 0,
        });
      }
    }

    return Object.values(coursesMap);
  }
}

module.exports = ReportController;
