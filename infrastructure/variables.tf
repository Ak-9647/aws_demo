variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-west-2"
}

variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "production-analytics-agent"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "prod"
}