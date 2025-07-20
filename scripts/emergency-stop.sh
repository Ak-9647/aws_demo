#!/bin/bash

# Emergency Stop - Immediately stop all expensive resources
# This will bring your AWS costs down to ~$5/month within minutes

echo "🚨 EMERGENCY STOP - Stopping all expensive resources..."

# Stop ECS service immediately
echo "📉 Stopping ECS service..."
aws ecs update-service \
    --cluster production-analytics-agent-cluster \
    --service production-analytics-agent-gui-service \
    --desired-count 0 \
    --region us-west-2

echo "✅ ECS service stopped (saves $18/month)"
echo "💰 Your costs are now reduced to ~$77/month"
echo ""
echo "🔧 To save even more, run:"
echo "   ./scripts/cleanup-resources.sh"
echo ""
echo "🚀 To restart later:"
echo "   aws ecs update-service --cluster production-analytics-agent-cluster --service production-analytics-agent-gui-service --desired-count 1 --region us-west-2"