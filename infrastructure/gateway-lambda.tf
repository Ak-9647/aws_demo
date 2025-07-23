# Lambda function for AgentCore Gateway target
resource "aws_lambda_function" "analytics_gateway_target" {
  filename         = "analytics_gateway_target.zip"
  function_name    = "${var.project_name}-analytics-gateway-target"
  role            = aws_iam_role.lambda_gateway.arn
  handler         = "index.handler"
  runtime         = "python3.11"
  timeout         = 30
  memory_size     = 256

  environment {
    variables = {
      POSTGRES_CONNECTION_STRING = aws_secretsmanager_secret.database_connection.arn
      ANALYTICS_API_KEY         = aws_secretsmanager_secret.analytics_api_key.arn
      LOG_LEVEL                 = "INFO"
    }
  }

  depends_on = [
    aws_iam_role_policy_attachment.lambda_gateway_basic,
    aws_cloudwatch_log_group.lambda_gateway,
    data.archive_file.analytics_gateway_target,
  ]

  tags = {
    Name        = "${var.project_name}-analytics-gateway-target"
    Project     = var.project_name
    Environment = var.environment
  }
}

# Lambda function code
data "archive_file" "analytics_gateway_target" {
  type        = "zip"
  output_path = "analytics_gateway_target.zip"
  source {
    content = file("${path.module}/lambda/simple_gateway_target.py")
    filename = "index.py"
  }
}

# IAM role for Lambda
resource "aws_iam_role" "lambda_gateway" {
  name = "${var.project_name}-lambda-gateway-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name        = "${var.project_name}-lambda-gateway-role"
    Project     = var.project_name
    Environment = var.environment
  }
}

# IAM policy for Lambda gateway
resource "aws_iam_policy" "lambda_gateway" {
  name        = "${var.project_name}-lambda-gateway-policy"
  description = "Policy for analytics gateway Lambda function"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = [
          aws_secretsmanager_secret.database_connection.arn,
          aws_secretsmanager_secret.analytics_api_key.arn
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "rds:DescribeDBInstances",
          "rds:DescribeDBClusters"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })
}

# Attach policies to Lambda role
resource "aws_iam_role_policy_attachment" "lambda_gateway_basic" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
  role       = aws_iam_role.lambda_gateway.name
}

resource "aws_iam_role_policy_attachment" "lambda_gateway_policy" {
  policy_arn = aws_iam_policy.lambda_gateway.arn
  role       = aws_iam_role.lambda_gateway.name
}

# CloudWatch Log Group for Lambda
resource "aws_cloudwatch_log_group" "lambda_gateway" {
  name              = "/aws/lambda/${var.project_name}-analytics-gateway-target"
  retention_in_days = 14

  tags = {
    Name        = "${var.project_name}-lambda-gateway-logs"
    Project     = var.project_name
    Environment = var.environment
  }
}

# Lambda permission for AgentCore Gateway
resource "aws_lambda_permission" "allow_agentcore_gateway" {
  statement_id  = "AllowExecutionFromAgentCoreGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.analytics_gateway_target.function_name
  principal     = "bedrock.amazonaws.com"
  source_arn    = "arn:aws:bedrock:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:agent-gateway/*"
}

# Output Lambda ARN for gateway configuration
output "analytics_gateway_lambda_arn" {
  description = "ARN of the analytics gateway Lambda function"
  value       = aws_lambda_function.analytics_gateway_target.arn
}