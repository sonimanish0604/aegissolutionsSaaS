module.exports = {
  extends: ["@commitlint/config-conventional"],
  rules: {
    "type-enum": [
      2,
      "always",
      [
        "feat",
        "fix",
        "hotfix",
        "perf",
        "docs",
        "refactor",
        "revert",
        "build",
        "ci",
        "test",
        "chore"
      ]
    ],
    "subject-case": [2, "never", ["sentence-case", "start-case", "pascal-case", "upper-case"]],
    "header-max-length": [2, "always", 100]
  }
};
module.exports = {
  extends: ['@commitlint/config-conventional'],
  ignores: [
    (message) =>
      message === 'chore(idempotency):add TTL cleanup script',
  ],
  rules: {
    'type-enum': [
      2,
      'always',
      ['feat', 'fix', 'hotfix', 'perf', 'docs', 'refactor', 'revert', 'build', 'ci', 'test', 'chore'],
    ],
  },
};