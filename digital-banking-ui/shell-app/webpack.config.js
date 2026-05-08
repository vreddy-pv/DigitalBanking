const { shareAll, withModuleFederationPlugin } = require('@angular-architects/module-federation/webpack');

module.exports = withModuleFederationPlugin({
  name: 'shell',
  filename: 'remoteEntry.js',
  exposes: {},

  remotes: {
    'account': 'http://localhost:4201/remoteEntry.js',
    'transaction': 'http://localhost:4202/remoteEntry.js',
    'transfer': 'http://localhost:4203/remoteEntry.js',
    'notification': 'http://localhost:4204/remoteEntry.js',
    'settings': 'http://localhost:4205/remoteEntry.js',
  },

  shared: shareAll({
    singleton: true,
    strictVersion: false,
    requiredVersion: 'auto',
    includeSecondaryEntrypoints: true,
  }),
});
