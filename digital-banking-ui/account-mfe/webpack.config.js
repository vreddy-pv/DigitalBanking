const { shareAll, withModuleFederationPlugin } = require('@angular-architects/module-federation/webpack');

module.exports = withModuleFederationPlugin({
  name: 'account',
  filename: 'remoteEntry.js',
  exposes: {
    './Module': './src/app/account/account.module.ts',
  },

  shared: shareAll({
    singleton: true,
    strictVersion: false,
    requiredVersion: 'auto',
    includeSecondaryEntrypoints: true,
  }),
});
