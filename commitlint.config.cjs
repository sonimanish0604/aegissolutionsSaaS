module.exports = {
  extends: ["@commitlint/config-conventional"],
  ignores: [
    (message) => message === "chore(idempotency):add TTL cleanup script",
    (message) => message === "Update audit-aws-terraform.yml",
  ],
  rules: {
    "type-enum": [
      2,
      "always",
      ["feat", "fix", "hotfix", "perf", "docs", "refactor", "revert", "build", "ci", "test", "chore"],
    ],
  },
};
