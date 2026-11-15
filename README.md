# Equipment Maintenance Platform

## Why I’m Building This

I’m building this project to refresh my AWS skills and strengthen my
understanding of Python, Linux, Terraform, Docker, Jenkins, and CI/CD.

My goal is to understand how the components work together, explain my
design decisions, and troubleshoot failures throughout the system.

## The Scenario

This application will use fictional equipment and maintenance data.

A user submits an equipment issue. The application stores the request
and places work in a queue. A background worker processes it and updates
its status. A containerized reporting service generates maintenance reports.

This scenario gives each cloud component a practical responsibility.

## Planned Components

| Component | Purpose |
|---|---|
| Dashboard | Submit requests and view their status |
| API Gateway and Lambda | Receive and validate requests |
| DynamoDB | Store equipment and maintenance requests |
| SQS and worker Lambda | Process requests in the background |
| ECR and ECS Fargate | Store and run the reporting container |
| Terraform | Create and destroy AWS infrastructure |
| GitHub and Jenkins | Track code and automate testing and deployment |
| CloudWatch | Collect logs and help diagnose failures |

## Cost Approach

I will deploy AWS resources for lab sessions and destroy them afterward.
Application development and local testing will run on my computer.

## Current Progress

- Created the project folders.
- Created and activated a Python virtual environment.
- Added Git ignore rules.
- Initialized a local Git repository.