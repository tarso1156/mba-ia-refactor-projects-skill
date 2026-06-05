const express = require('express');
const UserController = require('../controllers/userController');

function createUserRoutes(db) {
  const router = express.Router();
  const controller = new UserController(db);

  router.delete('/users/:id', async (req, res, next) => {
    try {
      const result = await controller.deleteUser(req.params.id);
      res.json(result);
    } catch (err) {
      next(err);
    }
  });

  return router;
}

module.exports = { createUserRoutes };
