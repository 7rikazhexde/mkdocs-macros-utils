module.exports = {
  testEnvironment: "jsdom",
  roots: ["<rootDir>/tests/js"],
  setupFiles: ["<rootDir>/tests/js/setup.js"],
  moduleDirectories: ["node_modules", "<rootDir>"],
  testMatch: ["**/tests/js/**/*.test.js"],
  collectCoverageFrom: ["mkdocs_macros_utils/static/js/**/*.js"],
  coverageDirectory: "coverage/js",
  transform: {
    "^.+\\.js$": "babel-jest",
  },
};
