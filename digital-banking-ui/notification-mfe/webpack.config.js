const { shareAll, withModuleFederationPlugin } = require('@angular-architects/module-federation/webpack');

module.exports = withModuleFederationPlugin({
  name: 'notification',
  filename: 'remoteEntry.js',
  exposes: {
    './Module': './src/app/notification/notification.module.ts',
  },

  shared: shareAll({
    singleton: true,
    strictVersion: false,
    requiredVersion: 'auto',
    includeSecondaryEntrypoints: true,
  }),
});
