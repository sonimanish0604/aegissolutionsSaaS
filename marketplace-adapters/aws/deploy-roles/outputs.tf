output "deploy_role_arns" {
  description = "Map of environment to the IAM role ARN used for deployments."
  value = {
    for key, mod in module.deploy_roles : key => mod.role_arn
  }
}

output "github_oidc_provider_arn" {
  description = "ARN of the GitHub Actions OIDC provider."
  value       = aws_iam_openid_connect_provider.github.arn
}
