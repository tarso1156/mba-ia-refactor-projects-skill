const express = require('express');
const { config, validateConfig } = require('./config/settings');
const { errorHandler } = require('./middlewares/errorHandler');
const Database = require('./database');
const { seed } = require('./database/seed');
const { createCheckoutRoutes } = require('./routes/checkoutRoutes');
const { createReportRoutes } = require('./routes/reportRoutes');
const { createUserRoutes } = require('./routes/userRoutes');

async function bootstrap() {
  validateConfig();

  const app = express();
  app.use(express.json({ limit: '10kb' }));

  // Request logging
  app.use((req, res, next) => {
    const start = Date.now();
    res.on('finish', () => {
      const ms = Date.now() - start;
      console.log(`${req.method} ${req.originalUrl} ${res.statusCode} ${ms}ms`);
    });
    next();
  });

  // Initialize database
  const db = new Database();
  await db.initSchema();
  await seed(db);

  // Register routes (dependency injection via factory)
  app.use('/api', createCheckoutRoutes(db));
  app.use('/api', createReportRoutes(db));
  app.use('/api', createUserRoutes(db));

  // Error handler (must be last middleware)
  app.use(errorHandler);

  app.listen(config.port, () => {
    console.log(`Ecommerce API running on port ${config.port}`);
  });
}

bootstrap().catch(err => {
  console.error('Failed to start application:', err.message);
  process.exit(1);
});
