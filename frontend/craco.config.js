module.exports = {
  webpack: {
    configure: (webpackConfig) => {
      // Remove any deprecated webpack config
      if (webpackConfig.devServer) {
        delete webpackConfig.devServer.onAfterSetupMiddleware;
        delete webpackConfig.devServer.onBeforeSetupMiddleware;
      }
      return webpackConfig;
    },
  },
}; 