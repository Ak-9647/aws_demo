# S3 bucket for agent logs
resource "aws_s3_bucket" "agent_logs" {
  bucket = "${var.project_name}-agent-logs-${random_id.bucket_suffix.hex}"

  tags = {
    Name        = "${var.project_name}-agent-logs"
    Environment = var.environment
  }
}

# S3 bucket encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "agent_logs" {
  bucket = aws_s3_bucket.agent_logs.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
    bucket_key_enabled = true
  }
}

# S3 bucket versioning
resource "aws_s3_bucket_versioning" "agent_logs" {
  bucket = aws_s3_bucket.agent_logs.id
  versioning_configuration {
    status = "Enabled"
  }
}

# S3 bucket public access block
resource "aws_s3_bucket_public_access_block" "agent_logs" {
  bucket = aws_s3_bucket.agent_logs.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Random ID for unique bucket naming
resource "random_id" "bucket_suffix" {
  byte_length = 4
}