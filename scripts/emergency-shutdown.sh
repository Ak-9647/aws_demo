#!/bin/bash

echo "🚨 Emergency Shutdown - Production Analytics Agent"
echo "=================================================="

# Stop ECS service immediately
echo "⏹️  Stopping ECS GUI service..."
aws ecs update-service \
  --cluster production-analytics-agent-cluster \
  --service production-analytics-agent-gui-service \
  --desired-count 0 \
  --region us-west-2

echo "✅ ECS service stopped - saves ~$18/month"

# Optional: Remove expensive resources
read -p "🤔 Remove expensive resources (NAT gateways, ALB)? This saves ~$68/month (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "💰 Removing expensive resources..."
    cd infrastructure
    terraform destroy \
      -target=aws_nat_gateway.main \
      -target=aws_eip.nat \
      -target=aws_lb.gui \
      -target=aws_lb_listener.gui \
      -target=aws_lb_target_group.gui \
      -auto-approve
    echo "✅ Expensive resources removed - total savings ~$68/month"
fi

echo ""
echo "💰 Cost Summary:"
echo "- ECS stopped: ~$18/month saved"
echo "- If expensive resources removed: ~$68/month saved"
echo "- Remaining cost: ~$27-77/month (depending on choices)"
echo ""
echo "🔄 To restart: Run 'terraform apply' in infrastructure folder"
echo "✅ Shutdown complete!"