variable "aws_region" {
  description = "AWS region for deployment"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name used as prefix for all resources"
  type        = string
  default     = "retail-dashboard"
}

variable "container_image" {
  description = "Docker image URI from ECR (e.g. 123456789.dkr.ecr.us-east-1.amazonaws.com/retail-sales-dashboard:latest)"
  type        = string
}

variable "desired_count" {
  description = "Number of Fargate tasks to run"
  type        = number
  default     = 2
}

variable "task_cpu" {
  description = "Fargate task CPU units (1 vCPU = 1024)"
  type        = string
  default     = "512"
}

variable "task_memory" {
  description = "Fargate task memory in MiB"
  type        = string
  default     = "1024"
}
