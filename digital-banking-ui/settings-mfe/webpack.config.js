const { shareAll, withModuleFederationPlugin } = require('@angular-architects/module-federation/webpack');

module.exports = withModuleFederationPlugin({
  name: 'settings',
  filename: 'remoteEntry.js',
  exposes: {
    './Module': './src/app/settings/settings.module.ts',
  },

  shared: shareAll({
    singleton: true,
    strictVersion: false,
    requiredVersion: 'auto',
    includeSecondaryEntrypoints: true,
  }),
});
