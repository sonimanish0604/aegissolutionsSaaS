# Change Management Policy

## Purpose
This policy defines how changes to source code, infrastructure, and configuration are requested,
developed, reviewed, tested, approved, and recorded in order to ensure system stability, security,
and compliance.

## Scope
This policy applies to:
- Application source code
- Infrastructure as Code (IaC) and deployment workflows
- Configuration and operational scripts

## Change Workflow

1. **Request / Plan**
   - A GitHub Issue must be created before any code changes begin.
   - The Issue must describe purpose, scope, impact, and rollback considerations.

2. **Develop**
   - A feature branch is created from the main development branch and named to reference the Issue ID.
   - Commits reference the Issue ID.

3. **Review / Approval**
   - A Pull Request (PR) is created to merge the feature branch.
   - Automated checks (security tests, linting, build, regression) must pass.
   - Required reviewer approval is needed prior to merge.

4. **Test / Verify**
   - CI pipelines run automated unit, integration, and regression tests.
   - Changes that affect security or data integrity require additional verification.

5. **Merge / Release**
   - PR is merged only to protected branches.
   - Automated dependency updates created by GitHub Dependabot are treated as pre-approved standard changes. These PRs may proceed without a dedicated Issue provided automated checks succeed and branch protections remain enforced. All other changes require a linked Issue with documented approval.

6. **Audit Logging**
   - Each change produces a signed record containing Issue → Branch → PR → Commits → Tests → Approvals → Deployment.
   - Audit logs are retained in S3 Object Lock (Compliance Mode).

## Emergency Change Procedure
Emergency changes bypass approval only to restore critical function.
A retrospective review Issue is created within 24 hours.

## Roles (Solo Developer Model)
- Developer and Approver may be the same individual when documented as a single-operator organization.
- The audit manifest ensures accountability and non-repudiation.

## Compliance Mapping
| Framework | Control Area |
|----------|--------------|
| ISO 27001:2022 | A.8.32 Change Management |
| SOC 2 Trust Services Criteria | CC8.1–CC8.4 |
| NIST SP 800-53 | CM-3, CM-5, CM-8 |
