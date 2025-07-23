# AgentCore Identity Configuration
# Manages authentication and authorization for the analytics agent

# Cognito User Pool for user authentication
resource "aws_cognito_user_pool" "analytics_users" {
  name = "${var.project_name}-users"

  # Password policy
  password_policy {
    minimum_length    = 8
    require_lowercase = true
    require_numbers   = true
    require_symbols   = true
    require_uppercase = true
  }

  # User attributes
  schema {
    attribute_data_type = "String"
    name               = "email"
    required           = true
    mutable           = true
  }

  schema {
    attribute_data_type = "String"
    name               = "department"
    required           = false
    mutable           = true
  }

  schema {
    attribute_data_type = "String"
    name               = "role"
    required           = false
    mutable           = true
  }

  # Account recovery
  account_recovery_setting {
    recovery_mechanism {
      name     = "verified_email"
      priority = 1
    }
  }

  # Email configuration
  email_configuration {
    email_sending_account = "COGNITO_DEFAULT"
  }

  # Auto-verified attributes
  auto_verified_attributes = ["email"]

  tags = {
    Name        = "${var.project_name}-user-pool"
    Project     = var.project_name
    Environment = var.environment
  }
}

# Cognito User Pool Client
resource "aws_cognito_user_pool_client" "analytics_client" {
  name         = "${var.project_name}-client"
  user_pool_id = aws_cognito_user_pool.analytics_users.id

  # OAuth configuration
  allowed_oauth_flows                  = ["code", "implicit"]
  allowed_oauth_flows_user_pool_client = true
  allowed_oauth_scopes                = ["email", "openid", "profile"]
  
  # Callback URLs for the application
  callback_urls = [
    "https://${aws_lb.gui.dns_name}/callback",
    "http://localhost:8501/callback"  # For local development
  ]
  
  logout_urls = [
    "https://${aws_lb.gui.dns_name}/logout",
    "http://localhost:8501/logout"
  ]

  # Supported identity providers
  supported_identity_providers = ["COGNITO"]

  # Token validity (in minutes for access/id tokens, days for refresh)
  access_token_validity  = 60    # 1 hour
  id_token_validity     = 60    # 1 hour  
  refresh_token_validity = 30    # 30 days
  
  token_validity_units {
    access_token  = "minutes"
    id_token      = "minutes"
    refresh_token = "days"
  }

  # Prevent user existence errors
  prevent_user_existence_errors = "ENABLED"

  # Read and write attributes
  read_attributes  = ["email", "email_verified", "custom:department", "custom:role"]
  write_attributes = ["email", "custom:department", "custom:role"]
}

# Cognito User Pool Domain
resource "aws_cognito_user_pool_domain" "analytics_domain" {
  domain       = "${var.project_name}-auth-${random_id.bucket_suffix.hex}"
  user_pool_id = aws_cognito_user_pool.analytics_users.id
}

# Identity Pool for federated identities
resource "aws_cognito_identity_pool" "analytics_identity" {
  identity_pool_name               = "${var.project_name}-identity"
  allow_unauthenticated_identities = false

  cognito_identity_providers {
    client_id               = aws_cognito_user_pool_client.analytics_client.id
    provider_name           = aws_cognito_user_pool.analytics_users.endpoint
    server_side_token_check = false
  }

  tags = {
    Name        = "${var.project_name}-identity-pool"
    Project     = var.project_name
    Environment = var.environment
  }
}

# IAM roles for authenticated users
resource "aws_iam_role" "authenticated_role" {
  name = "${var.project_name}-authenticated-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRoleWithWebIdentity"
        Effect = "Allow"
        Principal = {
          Federated = "cognito-identity.amazonaws.com"
        }
        Condition = {
          StringEquals = {
            "cognito-identity.amazonaws.com:aud" = aws_cognito_identity_pool.analytics_identity.id
          }
          "ForAnyValue:StringLike" = {
            "cognito-identity.amazonaws.com:amr" = "authenticated"
          }
        }
      }
    ]
  })

  tags = {
    Name        = "${var.project_name}-authenticated-role"
    Project     = var.project_name
    Environment = var.environment
  }
}

# Policy for authenticated users
resource "aws_iam_policy" "authenticated_policy" {
  name        = "${var.project_name}-authenticated-policy"
  description = "Policy for authenticated analytics users"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "bedrock:InvokeAgent",
          "bedrock:GetAgent",
          "bedrock:ListAgents"
        ]
        Resource = [
          "arn:aws:bedrock:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:agent/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.analytics_data.arn,
          "${aws_s3_bucket.analytics_data.arn}/*"
        ]
        Condition = {
          StringLike = {
            "s3:prefix" = ["analytics-data/*", "exports/*"]
          }
        }
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "authenticated_policy" {
  role       = aws_iam_role.authenticated_role.name
  policy_arn = aws_iam_policy.authenticated_policy.arn
}

# Attach the role to the identity pool
resource "aws_cognito_identity_pool_roles_attachment" "analytics_roles" {
  identity_pool_id = aws_cognito_identity_pool.analytics_identity.id

  roles = {
    "authenticated" = aws_iam_role.authenticated_role.arn
  }
}

# User groups for role-based access
resource "aws_cognito_user_group" "analytics_admins" {
  name         = "analytics-admins"
  user_pool_id = aws_cognito_user_pool.analytics_users.id
  description  = "Analytics administrators with full access"
  precedence   = 1
  role_arn     = aws_iam_role.analytics_admin_role.arn
}

resource "aws_cognito_user_group" "analytics_users" {
  name         = "analytics-users"
  user_pool_id = aws_cognito_user_pool.analytics_users.id
  description  = "Regular analytics users with read access"
  precedence   = 2
  role_arn     = aws_iam_role.analytics_user_role.arn
}

# Admin role with full permissions
resource "aws_iam_role" "analytics_admin_role" {
  name = "${var.project_name}-admin-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRoleWithWebIdentity"
        Effect = "Allow"
        Principal = {
          Federated = "cognito-identity.amazonaws.com"
        }
        Condition = {
          StringEquals = {
            "cognito-identity.amazonaws.com:aud" = aws_cognito_identity_pool.analytics_identity.id
          }
        }
      }
    ]
  })
}

# User role with limited permissions
resource "aws_iam_role" "analytics_user_role" {
  name = "${var.project_name}-user-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRoleWithWebIdentity"
        Effect = "Allow"
        Principal = {
          Federated = "cognito-identity.amazonaws.com"
        }
        Condition = {
          StringEquals = {
            "cognito-identity.amazonaws.com:aud" = aws_cognito_identity_pool.analytics_identity.id
          }
        }
      }
    ]
  })
}

# Admin policy with full access
resource "aws_iam_policy" "analytics_admin_policy" {
  name        = "${var.project_name}-admin-policy"
  description = "Full access policy for analytics administrators"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "bedrock:*",
          "s3:*",
          "rds:*",
          "dynamodb:*",
          "elasticache:*"
        ]
        Resource = "*"
      }
    ]
  })
}

# User policy with read-only access
resource "aws_iam_policy" "analytics_user_policy" {
  name        = "${var.project_name}-user-policy"
  description = "Read-only access policy for analytics users"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "bedrock:InvokeAgent",
          "bedrock:GetAgent",
          "s3:GetObject",
          "s3:ListBucket"
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "admin_policy" {
  role       = aws_iam_role.analytics_admin_role.name
  policy_arn = aws_iam_policy.analytics_admin_policy.arn
}

resource "aws_iam_role_policy_attachment" "user_policy" {
  role       = aws_iam_role.analytics_user_role.name
  policy_arn = aws_iam_policy.analytics_user_policy.arn
}

# Data sources for current AWS account and region
data "aws_region" "current" {}

# Outputs for application configuration
output "cognito_user_pool_id" {
  description = "Cognito User Pool ID"
  value       = aws_cognito_user_pool.analytics_users.id
}

output "cognito_client_id" {
  description = "Cognito User Pool Client ID"
  value       = aws_cognito_user_pool_client.analytics_client.id
}

output "cognito_domain" {
  description = "Cognito Domain for authentication"
  value       = aws_cognito_user_pool_domain.analytics_domain.domain
}

output "identity_pool_id" {
  description = "Cognito Identity Pool ID"
  value       = aws_cognito_identity_pool.analytics_identity.id
}