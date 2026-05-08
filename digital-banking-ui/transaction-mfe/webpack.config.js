const { shareAll, withModuleFederationPlugin } = require('@angular-architects/module-federation/webpack');

module.exports = withModuleFederationPlugin({
  name: 'transaction',
  filename: 'remoteEntry.js',
  exposes: {
    './Module': './src/app/transaction/transaction.module.ts',
  },

  shared: shareAll({
    singleton: true,
    strictVersion: false,
    requiredVersion: 'auto',
    includeSecondaryEntrypoints: true,
  }),
});
