module.exports = {
  testEnvironment: "jsdom",
  roots: ["<rootDir>/tests/js"],
  setupFiles: ["<rootDir>/tests/js/setup.js"],
  moduleDirectories: ["node_modules", "<rootDir>"],
  testMatch: ["**/tests/js/**/*.test.js"],
  collectCoverageFrom: ["mkdocs_macros_utils/static/js/x-twitter-widget.js"],
  coverageDirectory: "coverage",
  transform: {
    "^.+\\.js$": "babel-jest",
  },
};
