const conventionalPattern = /^[a-z]+(?:\(.+\))?:\s.+/;

module.exports = {
  extends: ["@commitlint/config-conventional"],
  ignores: [
    (message) => !conventionalPattern.test(message),
  ],
  rules: {
    "type-enum": [
      2,
      "always",
      ["feat", "fix", "hotfix", "perf", "docs", "refactor", "revert", "build", "ci", "test", "chore"],
    ],
    "body-max-line-length": [0, "always"],
  },
};
