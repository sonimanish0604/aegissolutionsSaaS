module.exports = {
  extends: ["@commitlint/config-conventional"],
  ignores: [
    (message) => message === "chore(idempotency):add TTL cleanup script",
  ],
  rules: {
    "type-enum": [
      2,
      "always",
      ["feat", "fix", "hotfix", "perf", "docs", "refactor", "revert", "build", "ci", "test", "chore"],
    ],
  },
};
