// ================================
// Configuration
// ================================
const CONFIG = {
  API_BASE_URL: window.location.hostname === 'localhost' 
    ? 'http://localhost:8195/api/v1'
    : '/api/v1',
  APP_NAME: "Who's My Neta Nepal",
  APP_NAME_NEPALI: 'को हो मेरो नेता नेपाल',
  ITEMS_PER_PAGE: 12,
  NEPAL_CENTER: [28.3949, 84.1240],
  ENABLE_ANALYTICS: true,
  CACHE_DURATION: 5 * 60 * 1000, // 5 minutes
};

// Make CONFIG globally available
window.APP_CONFIG = CONFIG;
