const express = require('express');
const ReportController = require('../controllers/reportController');

function createReportRoutes(db) {
  const router = express.Router();
  const controller = new ReportController(db);

  router.get('/admin/financial-report', async (req, res, next) => {
    try {
      const report = await controller.getFinancialReport();
      res.json(report);
    } catch (err) {
      next(err);
    }
  });

  return router;
}

module.exports = { createReportRoutes };
