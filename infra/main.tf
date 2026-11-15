terraform {
  required_version = ">= 1.10, < 2.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

resource "aws_dynamodb_table" "requests" {
  name         = "maintenance-requests-lab"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "request_id"

  attribute {
    name = "request_id"
    type = "S"
  }

  tags = {
    Project     = "equipment-maintenance-platform"
    Environment = "lab"
  }
}

output "requests_table_name" {
  value = aws_dynamodb_table.requests.name
}

resource "aws_sqs_queue" "requests_dlq" {
  name                      = "maintenance-requests-dlq-lab"
  message_retention_seconds = 86400

  tags = {
    Project     = "equipment-maintenance-platform"
    Environment = "lab"
  }
}

resource "aws_sqs_queue" "requests" {
  name                       = "maintenance-requests-queue-lab"
  visibility_timeout_seconds = 60
  message_retention_seconds  = 86400
  sqs_managed_sse_enabled    = true

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.requests_dlq.arn
    maxReceiveCount     = 3
  })

  tags = {
    Project     = "equipment-maintenance-platform"
    Environment = "lab"
  }
}

output "requests_queue_url" {
  value = aws_sqs_queue.requests.url
}