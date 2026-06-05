const config = {
  port: parseInt(process.env.PORT, 10) || 3000,
  nodeEnv: process.env.NODE_ENV || 'development',
  paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || (() => {
    if (process.env.NODE_ENV === 'production') {
      throw new Error('PAYMENT_GATEWAY_KEY is required in production');
    }
    return 'pk_test_dev_only';
  })(),
  smtpUser: process.env.SMTP_USER || 'dev@localhost',
};

function validateConfig() {
  if (config.nodeEnv === 'production') {
    const required = ['PAYMENT_GATEWAY_KEY'];
    const missing = required.filter(key => !process.env[key]);
    if (missing.length > 0) {
      throw new Error(`Missing required environment variables: ${missing.join(', ')}`);
    }
  }
}

module.exports = { config, validateConfig };
