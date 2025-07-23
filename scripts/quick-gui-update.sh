#!/bin/bash
# Quick GUI Update - Different Approach
# Force update with new task definition

set -e

echo "🚀 Quick GUI Update - New Approach"

# Configuration
REGION="us-west-2"
CLUSTER_NAME="production-analytics-agent-cluster"
SERVICE_NAME="production-analytics-agent-gui-service"
ACCOUNT_ID="280383026847"
ECR_URI="${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/production-analytics-agent-gui"
NEW_TAG="v4.1-modern-$(date +%s)"

echo "Using image: ${ECR_URI}:${NEW_TAG}"

# Tag and push with timestamp
docker tag production-analytics-agent-gui:v4.1-modern ${ECR_URI}:${NEW_TAG}
docker push ${ECR_URI}:${NEW_TAG}

# Create new task definition JSON
cat > /tmp/new-task-def.json << EOF
{
  "family": "production-analytics-agent-gui",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "executionRoleArn": "arn:aws:iam::${ACCOUNT_ID}:role/production-analytics-agent-gui-execution-role",
  "taskRoleArn": "arn:aws:iam::${ACCOUNT_ID}:role/production-analytics-agent-gui-task-role",
  "containerDefinitions": [
    {
      "name": "gui",
      "image": "${ECR_URI}:${NEW_TAG}",
      "portMappings": [
        {
          "containerPort": 8501,
          "protocol": "tcp"
        }
      ],
      "essential": true,
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/production-analytics-agent-gui",
          "awslogs-region": "${REGION}",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "environment": [
        {
          "name": "AWS_DEFAULT_REGION",
          "value": "${REGION}"
        }
      ]
    }
  ]
}
EOF

# Register new task definition
echo "Registering new task definition..."
NEW_TASK_DEF_ARN=$(aws ecs register-task-definition \
  --region ${REGION} \
  --cli-input-json file:///tmp/new-task-def.json \
  --query 'taskDefinition.taskDefinitionArn' \
  --output text)

echo "New task definition: ${NEW_TASK_DEF_ARN}"

# Update service with new task definition
echo "Updating service..."
aws ecs update-service \
  --cluster ${CLUSTER_NAME} \
  --service ${SERVICE_NAME} \
  --task-definition ${NEW_TASK_DEF_ARN} \
  --region ${REGION} > /dev/null

echo "✅ Service updated! Checking status..."

# Quick status check
aws ecs describe-services \
  --cluster ${CLUSTER_NAME} \
  --services ${SERVICE_NAME} \
  --region ${REGION} \
  --query 'services[0].{Status:status,TaskDefinition:taskDefinition,RunningCount:runningCount}'

echo ""
echo "🌐 GUI URL: http://analytics-gui-alb-1184070249.us-west-2.elb.amazonaws.com/"
echo "⏳ New version should be live in 2-3 minutes"

# Clean up
rm -f /tmp/new-task-def.json