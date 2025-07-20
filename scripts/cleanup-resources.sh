#!/bin/bash

# AWS Resource Cleanup Script
# Use this to stop/remove AWS resources to save costs

set -e

REGION="us-west-2"
CLUSTER_NAME="production-analytics-agent-cluster"
SERVICE_NAME="production-analytics-agent-gui-service"

echo "🧹 AWS Resource Cleanup Script"
echo "================================"

# Function to check if AWS CLI is configured
check_aws_cli() {
    if ! aws sts get-caller-identity &> /dev/null; then
        echo "❌ AWS CLI not configured or no permissions"
        exit 1
    fi
    echo "✅ AWS CLI configured"
}

# Function to scale ECS service to 0
scale_down_ecs() {
    echo "📉 Scaling down ECS service..."
    
    # Check if service exists
    if aws ecs describe-services --cluster $CLUSTER_NAME --services $SERVICE_NAME --region $REGION &> /dev/null; then
        aws ecs update-service \
            --cluster $CLUSTER_NAME \
            --service $SERVICE_NAME \
            --desired-count 0 \
            --region $REGION
        echo "✅ ECS service scaled to 0 (saves ~$18/month)"
    else
        echo "ℹ️  ECS service not found or already stopped"
    fi
}

# Function to remove expensive resources via Terraform
remove_expensive_resources() {
    echo "💰 Removing expensive resources..."
    
    cd infrastructure
    
    # Remove NAT gateways, EIPs, and Load Balancer
    terraform destroy \
        -target=aws_nat_gateway.main \
        -target=aws_eip.nat \
        -target=aws_lb.gui \
        -target=aws_lb_listener.gui \
        -target=aws_lb_target_group.gui \
        -target=aws_security_group.alb \
        -target=aws_ecs_service.gui \
        -auto-approve
    
    echo "✅ Expensive resources removed (saves ~$68/month)"
    cd ..
}

# Function to completely destroy all infrastructure
destroy_all() {
    echo "🔥 DESTROYING ALL INFRASTRUCTURE..."
    echo "⚠️  This will remove everything except S3 data!"
    
    read -p "Are you sure? Type 'yes' to continue: " confirm
    if [ "$confirm" != "yes" ]; then
        echo "❌ Cancelled"
        exit 1
    fi
    
    cd infrastructure
    terraform destroy -auto-approve
    echo "✅ All infrastructure destroyed (cost: ~$1.20/month)"
    cd ..
}

# Function to show current costs
show_current_resources() {
    echo "📊 Current AWS Resources:"
    echo "========================"
    
    # ECS Service status
    echo "🐳 ECS Service:"
    if aws ecs describe-services --cluster $CLUSTER_NAME --services $SERVICE_NAME --region $REGION --query 'services[0].{Status:status,Running:runningCount,Desired:desiredCount}' 2>/dev/null; then
        echo ""
    else
        echo "   Service not found"
    fi
    
    # Load Balancer status
    echo "⚖️  Load Balancers:"
    aws elbv2 describe-load-balancers --region $REGION --query 'LoadBalancers[?contains(LoadBalancerName, `analytics`)].{Name:LoadBalancerName,State:State.Code}' --output table 2>/dev/null || echo "   No load balancers found"
    
    # NAT Gateways
    echo "🌐 NAT Gateways:"
    aws ec2 describe-nat-gateways --region $REGION --query 'NatGateways[?State==`available`].{ID:NatGatewayId,State:State}' --output table 2>/dev/null || echo "   No NAT gateways found"
    
    # Elastic IPs
    echo "📍 Elastic IPs:"
    aws ec2 describe-addresses --region $REGION --query 'Addresses[].{IP:PublicIp,Associated:AssociationId}' --output table 2>/dev/null || echo "   No Elastic IPs found"
}

# Function to restart services
restart_services() {
    echo "🚀 Restarting services..."
    
    cd infrastructure
    terraform apply -auto-approve
    echo "✅ Services restarted"
    cd ..
}

# Main menu
show_menu() {
    echo ""
    echo "Choose an option:"
    echo "1) Show current resources and costs"
    echo "2) Scale down ECS service only (saves $18/month)"
    echo "3) Remove expensive resources (saves $68/month)"
    echo "4) DESTROY ALL infrastructure (saves $95/month)"
    echo "5) Restart all services"
    echo "6) Exit"
    echo ""
}

# Main execution
main() {
    check_aws_cli
    
    while true; do
        show_menu
        read -p "Enter your choice (1-6): " choice
        
        case $choice in
            1)
                show_current_resources
                ;;
            2)
                scale_down_ecs
                echo "💰 Monthly savings: ~$18"
                echo "📝 To restart: aws ecs update-service --cluster $CLUSTER_NAME --service $SERVICE_NAME --desired-count 1 --region $REGION"
                ;;
            3)
                remove_expensive_resources
                echo "💰 Monthly savings: ~$68"
                echo "📝 To restart: cd infrastructure && terraform apply"
                ;;
            4)
                destroy_all
                echo "💰 Monthly savings: ~$95"
                echo "📝 To restart: cd infrastructure && terraform apply"
                ;;
            5)
                restart_services
                ;;
            6)
                echo "👋 Goodbye!"
                exit 0
                ;;
            *)
                echo "❌ Invalid option. Please choose 1-6."
                ;;
        esac
        
        echo ""
        read -p "Press Enter to continue..."
    done
}

# Run main function
main