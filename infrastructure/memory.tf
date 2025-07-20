# DynamoDB table for conversation history
resource "aws_dynamodb_table" "conversation_history" {
  name           = "${var.project_name}-conversation-history"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "session_id"
  range_key      = "timestamp"

  attribute {
    name = "session_id"
    type = "S"
  }

  attribute {
    name = "timestamp"
    type = "N"
  }

  attribute {
    name = "user_id"
    type = "S"
  }

  global_secondary_index {
    name     = "user-index"
    hash_key = "user_id"
    range_key = "timestamp"
    projection_type = "ALL"
  }

  ttl {
    attribute_name = "expires_at"
    enabled        = true
  }

  tags = {
    Name        = "${var.project_name}-conversation-history"
    Environment = var.environment
  }
}

# DynamoDB table for user preferences
resource "aws_dynamodb_table" "user_preferences" {
  name           = "${var.project_name}-user-preferences"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "user_id"

  attribute {
    name = "user_id"
    type = "S"
  }

  tags = {
    Name        = "${var.project_name}-user-preferences"
    Environment = var.environment
  }
}

# ElastiCache subnet group
resource "aws_elasticache_subnet_group" "redis" {
  name       = "${var.project_name}-redis-subnet-group"
  subnet_ids = aws_subnet.private[*].id

  tags = {
    Name        = "${var.project_name}-redis-subnet-group"
    Environment = var.environment
  }
}

# Security group for Redis
resource "aws_security_group" "redis" {
  name        = "${var.project_name}-redis-sg"
  description = "Security group for Redis ElastiCache"
  vpc_id      = aws_vpc.main.id

  ingress {
    description     = "Redis from ECS tasks"
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs_tasks.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "${var.project_name}-redis-sg"
    Environment = var.environment
  }
}

# ElastiCache Redis cluster
resource "aws_elasticache_replication_group" "redis" {
  replication_group_id         = "${var.project_name}-redis"
  description                  = "Redis cluster for session memory"
  
  node_type                    = "cache.t3.micro"
  port                         = 6379
  parameter_group_name         = "default.redis7"
  
  num_cache_clusters           = 1
  
  subnet_group_name            = aws_elasticache_subnet_group.redis.name
  security_group_ids           = [aws_security_group.redis.id]
  
  at_rest_encryption_enabled   = true
  transit_encryption_enabled   = false  # Simplified for development
  
  automatic_failover_enabled   = false  # Single node for cost optimization
  
  tags = {
    Name        = "${var.project_name}-redis"
    Environment = var.environment
  }
}

# Lambda function for memory cleanup
resource "aws_lambda_function" "memory_cleanup" {
  filename         = "memory_cleanup.zip"
  function_name    = "${var.project_name}-memory-cleanup"
  role            = aws_iam_role.lambda_memory.arn
  handler         = "memory_cleanup.lambda_handler"
  runtime         = "python3.11"
  timeout         = 300

  environment {
    variables = {
      CONVERSATION_TABLE = aws_dynamodb_table.conversation_history.name
      PREFERENCES_TABLE  = aws_dynamodb_table.user_preferences.name
      REDIS_ENDPOINT     = aws_elasticache_replication_group.redis.primary_endpoint_address
    }
  }

  tags = {
    Name        = "${var.project_name}-memory-cleanup"
    Environment = var.environment
  }
}

# IAM role for Lambda memory functions
resource "aws_iam_role" "lambda_memory" {
  name = "${var.project_name}-lambda-memory-role"

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
    Name        = "${var.project_name}-lambda-memory-role"
    Environment = var.environment
  }
}

# IAM policy for Lambda memory functions
resource "aws_iam_policy" "lambda_memory" {
  name        = "${var.project_name}-lambda-memory-policy"
  description = "IAM policy for Lambda memory management functions"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      },
      {
        Effect = "Allow"
        Action = [
          "dynamodb:Query",
          "dynamodb:Scan",
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:DeleteItem"
        ]
        Resource = [
          aws_dynamodb_table.conversation_history.arn,
          "${aws_dynamodb_table.conversation_history.arn}/index/*",
          aws_dynamodb_table.user_preferences.arn
        ]
      }
    ]
  })
}

# Attach policy to role
resource "aws_iam_role_policy_attachment" "lambda_memory" {
  role       = aws_iam_role.lambda_memory.name
  policy_arn = aws_iam_policy.lambda_memory.arn
}

# CloudWatch event rule for memory cleanup
resource "aws_cloudwatch_event_rule" "memory_cleanup" {
  name                = "${var.project_name}-memory-cleanup"
  description         = "Trigger memory cleanup daily"
  schedule_expression = "rate(1 day)"

  tags = {
    Name        = "${var.project_name}-memory-cleanup"
    Environment = var.environment
  }
}

# CloudWatch event target
resource "aws_cloudwatch_event_target" "memory_cleanup" {
  rule      = aws_cloudwatch_event_rule.memory_cleanup.name
  target_id = "MemoryCleanupTarget"
  arn       = aws_lambda_function.memory_cleanup.arn
}

# Lambda permission for CloudWatch Events
resource "aws_lambda_permission" "allow_cloudwatch" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.memory_cleanup.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.memory_cleanup.arn
}