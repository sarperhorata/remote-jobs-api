const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
  app.use(
    '/api',
    createProxyMiddleware({
      target: 'http://localhost:8001',
      changeOrigin: true,
      secure: false,
      logLevel: 'debug',
      onProxyReq: function(proxyReq, req, res) {
        console.log('🔗 Proxying request:', req.method, req.url, '->', proxyReq.path);
      },
      onProxyRes: function(proxyRes, req, res) {
        console.log('✅ Proxy response:', proxyRes.statusCode, req.url);
      },
      onError: function(err, req, res) {
        console.error('❌ Proxy error:', err.message, req.url);
      }
    })
  );
}; 