const express = require('express');
const CheckoutController = require('../controllers/checkoutController');

function createCheckoutRoutes(db) {
  const router = express.Router();
  const controller = new CheckoutController(db);

  router.post('/checkout', async (req, res, next) => {
    try {
      const result = await controller.processCheckout({
        userName: req.body.usr,
        email: req.body.eml,
        password: req.body.pwd,
        courseId: req.body.c_id,
        creditCard: req.body.card,
      });
      res.status(200).json(result);
    } catch (err) {
      next(err);
    }
  });

  return router;
}

module.exports = { createCheckoutRoutes };
