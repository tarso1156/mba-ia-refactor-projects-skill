const UserModel = require('../models/userModel');
const EnrollmentModel = require('../models/enrollmentModel');
const PaymentModel = require('../models/paymentModel');

class UserController {
  constructor(db) {
    this.userModel = new UserModel(db);
    this.enrollmentModel = new EnrollmentModel(db);
    this.paymentModel = new PaymentModel(db);
  }

  async deleteUser(userId) {
    // Get enrollment IDs for cascade delete
    const enrollments = await this.enrollmentModel.findByUserId(userId);
    const enrollmentIds = enrollments.map(e => e.id);

    // Delete in order: payments -> enrollments -> user
    await this.paymentModel.deleteByEnrollmentIds(enrollmentIds);
    await this.enrollmentModel.deleteByUserId(userId);
    await this.userModel.deleteById(userId);

    return { message: 'Usuário deletado com sucesso' };
  }
}

module.exports = UserController;
