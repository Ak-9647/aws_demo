# Gateway Supporting Infrastructure
# Lambda functions and resources to support AgentCore Gateways
# Note: AgentCore Gateways are created through the AWS Console

# Secrets for gateway authentication
resource "aws_secretsmanager_secret" "analytics_api_key" {
  name        = "${var.project_name}-analytics-api-key"
  description = "API key for external analytics service"
  
  tags = {
    Name        = "${var.project_name}-analytics-api-key"
    Project     = var.project_name
    Environment = var.environment
  }
}

resource "aws_secretsmanager_secret_version" "analytics_api_key" {
  secret_id = aws_secretsmanager_secret.analytics_api_key.id
  secret_string = jsonencode({
    api_key = "your-analytics-api-key-here"
  })
}

resource "aws_secretsmanager_secret" "database_connection" {
  name        = "${var.project_name}-database-connection"
  description = "Database connection string for analytics"
  
  tags = {
    Name        = "${var.project_name}-database-connection"
    Project     = var.project_name
    Environment = var.environment
  }
}

resource "aws_secretsmanager_secret_version" "database_connection" {
  secret_id = aws_secretsmanager_secret.database_connection.id
  secret_string = jsonencode({
    connection_string = "postgresql://analytics_user:${random_password.db_password.result}@${aws_rds_cluster.analytics.endpoint}:5432/analytics"
  })
}

# S3 bucket for analytics data
resource "aws_s3_bucket" "analytics_data" {
  bucket = "${var.project_name}-analytics-data-${random_id.bucket_suffix.hex}"
  
  tags = {
    Name        = "${var.project_name}-analytics-data"
    Project     = var.project_name
    Environment = var.environment
    Purpose     = "Analytics Data Storage"
  }
}

resource "aws_s3_bucket_versioning" "analytics_data" {
  bucket = aws_s3_bucket.analytics_data.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "analytics_data" {
  bucket = aws_s3_bucket.analytics_data.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# RDS cluster for analytics database
resource "aws_rds_cluster" "analytics" {
  cluster_identifier      = "${var.project_name}-analytics-cluster"
  engine                 = "aurora-postgresql"
  engine_version         = "15.4"
  database_name          = "analytics"
  master_username        = "analytics_admin"
  master_password        = random_password.db_password.result
  
  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.analytics.name
  
  backup_retention_period = 7
  preferred_backup_window = "03:00-04:00"
  
  skip_final_snapshot = true
  
  tags = {
    Name        = "${var.project_name}-analytics-cluster"
    Project     = var.project_name
    Environment = var.environment
  }
}

resource "aws_rds_cluster_instance" "analytics" {
  count              = 1
  identifier         = "${var.project_name}-analytics-${count.index}"
  cluster_identifier = aws_rds_cluster.analytics.id
  instance_class     = "db.t3.medium"
  engine             = aws_rds_cluster.analytics.engine
  engine_version     = aws_rds_cluster.analytics.engine_version
  
  tags = {
    Name        = "${var.project_name}-analytics-instance-${count.index}"
    Project     = var.project_name
    Environment = var.environment
  }
}

resource "random_password" "db_password" {
  length  = 16
  special = true
}

resource "aws_db_subnet_group" "analytics" {
  name       = "${var.project_name}-analytics-subnet-group"
  subnet_ids = aws_subnet.private[*].id

  tags = {
    Name        = "${var.project_name}-analytics-subnet-group"
    Project     = var.project_name
    Environment = var.environment
  }
}

resource "aws_security_group" "rds" {
  name        = "${var.project_name}-rds-sg"
  description = "Security group for RDS analytics cluster"
  vpc_id      = aws_vpc.main.id

  ingress {
    description     = "PostgreSQL from ECS tasks"
    from_port       = 5432
    to_port         = 5432
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
    Name        = "${var.project_name}-rds-sg"
    Project     = var.project_name
    Environment = var.environment
  }
}

# Outputs for gateway configuration
output "analytics_api_secret_arn" {
  description = "ARN of the analytics API key secret"
  value       = aws_secretsmanager_secret.analytics_api_key.arn
}

output "database_connection_secret_arn" {
  description = "ARN of the database connection secret"
  value       = aws_secretsmanager_secret.database_connection.arn
}

output "analytics_data_bucket" {
  description = "Name of the analytics data S3 bucket"
  value       = aws_s3_bucket.analytics_data.bucket
}

output "rds_cluster_endpoint" {
  description = "RDS cluster endpoint"
  value       = aws_rds_cluster.analytics.endpoint
}