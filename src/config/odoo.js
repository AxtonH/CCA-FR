// Read from environment variables or use defaults
export const ODOO_URL = process.env.REACT_APP_ODOO_URL || 'https://prezlab.odoo.com/';
export const ODOO_DB = process.env.REACT_APP_ODOO_DB || 'odoo-ps-psae-prezlab-main-10779811';

// Email configuration
export const DEFAULT_SENDER_EMAIL = process.env.REACT_APP_DEFAULT_SENDER_EMAIL || '';
export const DEFAULT_SENDER_PASSWORD = process.env.REACT_APP_DEFAULT_SENDER_PASSWORD || '';
export const DEFAULT_SMTP_SERVER = process.env.REACT_APP_DEFAULT_SMTP_SERVER || 'smtp.gmail.com';
export const DEFAULT_SMTP_PORT = process.env.REACT_APP_DEFAULT_SMTP_PORT || '587';

// Allowed users
export const ALLOWED_USER_EMAILS = process.env.REACT_APP_ALLOWED_USER_EMAILS 
  ? process.env.REACT_APP_ALLOWED_USER_EMAILS.split(',').map(email => email.trim())
  : ['omar.elhasan@prezlab.com', 'sanad.zaqtan@prezlab.com'];


