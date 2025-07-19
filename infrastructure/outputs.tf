output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.main.id
}

output "public_subnet_ids" {
  description = "IDs of the public subnets"
  value       = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  description = "IDs of the private subnets"
  value       = aws_subnet.private[*].id
}

output "s3_bucket_name" {
  description = "Name of the S3 bucket for agent logs"
  value       = aws_s3_bucket.agent_logs.bucket
}

output "s3_bucket_arn" {
  description = "ARN of the S3 bucket for agent logs"
  value       = aws_s3_bucket.agent_logs.arn
}

output "ecr_agent_repository_url" {
  description = "URL of the ECR repository for agent images"
  value       = aws_ecr_repository.agent.repository_url
}

output "ecr_gui_repository_url" {
  description = "URL of the ECR repository for GUI images"
  value       = aws_ecr_repository.gui.repository_url
}

output "agentcore_runtime_role_arn" {
  description = "ARN of the AgentCore Runtime IAM role"
  value       = aws_iam_role.agentcore_runtime.arn
}

output "ecs_task_execution_role_arn" {
  description = "ARN of the ECS task execution IAM role"
  value       = aws_iam_role.ecs_task_execution.arn
}