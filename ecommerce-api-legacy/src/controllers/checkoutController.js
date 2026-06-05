const UserModel = require('../models/userModel');
const CourseModel = require('../models/courseModel');
const EnrollmentModel = require('../models/enrollmentModel');
const PaymentModel = require('../models/paymentModel');
const AuditLogModel = require('../models/auditLogModel');
const { hashPassword } = require('../services/passwordService');

class CheckoutController {
  constructor(db) {
    this.userModel = new UserModel(db);
    this.courseModel = new CourseModel(db);
    this.enrollmentModel = new EnrollmentModel(db);
    this.paymentModel = new PaymentModel(db);
    this.auditLogModel = new AuditLogModel(db);
  }

  validateInput({ userName, email, courseId, creditCard }) {
    const errors = [];
    if (!userName || typeof userName !== 'string') errors.push('userName is required');
    if (!email || typeof email !== 'string' || !email.includes('@')) errors.push('valid email is required');
    if (!courseId || !Number.isInteger(Number(courseId))) errors.push('courseId must be an integer');
    if (!creditCard || typeof creditCard !== 'string' || !/^\d+$/.test(creditCard)) errors.push('creditCard must be a numeric string');
    return errors;
  }

  async processCheckout({ userName, email, password, courseId, creditCard }) {
    // Validate input
    const errors = this.validateInput({ userName, email, courseId, creditCard });
    if (errors.length > 0) {
      const err = new Error(errors.join(', '));
      err.status = 400;
      throw err;
    }

    const numericCourseId = Number(courseId);

    // Find active course
    const course = await this.courseModel.findActiveById(numericCourseId);
    if (!course) {
      const err = new Error('Curso não encontrado');
      err.status = 404;
      throw err;
    }

    // Find or create user
    let user = await this.userModel.findByEmail(email);
    let userId;

    if (!user) {
      const hashedPassword = await hashPassword(password || '123456');
      userId = await this.userModel.create(userName, email, hashedPassword);
    } else {
      userId = user.id;
    }

    // Process payment
    const paymentStatus = creditCard.startsWith('4') ? 'PAID' : 'DENIED';
    if (paymentStatus === 'DENIED') {
      const err = new Error('Pagamento recusado');
      err.status = 400;
      throw err;
    }

    // Create enrollment
    const enrollmentId = await this.enrollmentModel.create(userId, numericCourseId);

    // Create payment record
    await this.paymentModel.create(enrollmentId, course.price, paymentStatus);

    // Audit log
    await this.auditLogModel.create(`Checkout curso ${numericCourseId} por ${userId}`);

    return { msg: 'Sucesso', enrollment_id: enrollmentId };
  }
}

module.exports = CheckoutController;
