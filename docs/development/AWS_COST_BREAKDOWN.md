# 💰 AWS Cost Breakdown & Management

## 🏷️ **Current AWS Resources & Costs**

### **💸 ONGOING COSTS (24/7 charges)**

#### 1. **NAT Gateways** - 🔴 **HIGHEST COST**
- **Cost**: ~$45/month ($0.045/hour × 2 NAT gateways × 24h × 30 days)
- **Purpose**: Allow private subnets to access internet
- **Usage**: Always running regardless of traffic
- **💡 Cost Optimization**: Can be removed if not using private subnet internet access

#### 2. **Application Load Balancer (ALB)**
- **Cost**: ~$16/month ($0.0225/hour × 24h × 30 days)
- **Purpose**: Routes traffic to GUI containers
- **Usage**: Always running
- **💡 Cost Optimization**: Essential for production, but can be stopped when not in use

#### 3. **Elastic IP Addresses**
- **Cost**: ~$7.20/month ($0.005/hour × 2 EIPs × 24h × 30 days)
- **Purpose**: Static IPs for NAT gateways
- **Usage**: Always allocated
- **💡 Cost Optimization**: Released when NAT gateways are destroyed

### **📊 USAGE-BASED COSTS (Pay per use)**

#### 4. **ECS Fargate (GUI Container)**
- **Cost**: ~$15-30/month (depends on usage)
- **Calculation**: 
  - CPU: 0.5 vCPU × $0.04048/vCPU-hour = ~$14.50/month
  - Memory: 1GB × $0.004445/GB-hour = ~$3.20/month
- **Usage**: Only when GUI container is running
- **💡 Cost Optimization**: Can scale to 0 when not needed

#### 5. **S3 Storage**
- **Cost**: ~$0.50/month (for small datasets)
- **Calculation**: 
  - Storage: ~20GB × $0.023/GB = ~$0.46/month
  - Requests: Minimal for analytics use
- **Usage**: Pay for data stored
- **💡 Cost Optimization**: Very cheap, can keep running

#### 6. **ECR (Container Registry)**
- **Cost**: ~$1-2/month
- **Calculation**: ~2GB container images × $0.10/GB = ~$0.20/month
- **Usage**: Pay for storage of container images
- **💡 Cost Optimization**: Very cheap, can keep running

#### 7. **CloudWatch Logs**
- **Cost**: ~$2-5/month
- **Calculation**: Log ingestion and storage
- **Usage**: Pay for logs generated
- **💡 Cost Optimization**: Can reduce retention period

#### 8. **AgentCore (Bedrock)**
- **Cost**: Pay per request
- **Calculation**: Depends on usage volume
- **Usage**: Only when processing queries
- **💡 Cost Optimization**: No cost when not used

### **🆓 FREE RESOURCES**
- VPC, Subnets, Route Tables
- Security Groups
- IAM Roles and Policies
- ECS Cluster (without tasks)

## 💰 **ESTIMATED TOTAL MONTHLY COST**

### **🔴 Full Production (Always On)**
```
NAT Gateways:        $45.00
Load Balancer:       $16.00
Elastic IPs:         $7.20
ECS Fargate:         $17.70
S3 Storage:          $0.50
ECR Storage:         $0.20
CloudWatch:          $3.00
AgentCore:           $5-20 (usage-based)
------------------------
TOTAL:              ~$95-115/month
```

### **🟡 Development Mode (Scaled Down)**
```
Load Balancer:       $16.00
ECS Fargate:         $0.00 (scaled to 0)
S3 Storage:          $0.50
ECR Storage:         $0.20
CloudWatch:          $1.00
AgentCore:           $0-5 (minimal usage)
------------------------
TOTAL:              ~$18-23/month
```

### **🟢 Completely Stopped**
```
S3 Storage:          $0.50
ECR Storage:         $0.20
CloudWatch:          $0.50
------------------------
TOTAL:              ~$1.20/month
```

## 🛑 **HOW TO STOP SERVICES TO SAVE COSTS**

### **Option 1: Scale Down (Keep Infrastructure)**
```bash
# Scale ECS service to 0 (stops GUI)
aws ecs update-service \
  --cluster production-analytics-agent-cluster \
  --service production-analytics-agent-gui-service \
  --desired-count 0 \
  --region us-west-2

# This saves ~$17/month on Fargate costs
```

### **Option 2: Destroy Expensive Resources**
```bash
cd infrastructure

# Remove NAT gateways and ALB (saves ~$68/month)
terraform destroy \
  -target=aws_nat_gateway.main \
  -target=aws_eip.nat \
  -target=aws_lb.gui \
  -target=aws_lb_listener.gui \
  -target=aws_lb_target_group.gui \
  -target=aws_ecs_service.gui \
  -auto-approve
```

### **Option 3: Complete Shutdown**
```bash
cd infrastructure

# Destroy everything except S3 and ECR
terraform destroy -auto-approve

# This brings cost down to ~$1.20/month
```

## 🔄 **HOW TO RESTART SERVICES**

### **Scale Up ECS Service**
```bash
aws ecs update-service \
  --cluster production-analytics-agent-cluster \
  --service production-analytics-agent-gui-service \
  --desired-count 1 \
  --region us-west-2
```

### **Rebuild Infrastructure**
```bash
cd infrastructure
terraform apply -auto-approve
```

## 💡 **COST OPTIMIZATION STRATEGIES**

### **🟢 Immediate Savings (No Impact)**
1. **Remove NAT Gateways** if private subnet internet access isn't needed
   - **Savings**: $45/month
   - **Impact**: Private subnets can't access internet (containers can still work)

2. **Use Spot Instances** for development
   - **Savings**: Up to 70% on Fargate costs
   - **Impact**: Containers may be interrupted

### **🟡 Medium-term Savings**
1. **Schedule Auto-scaling**
   - Scale down during nights/weekends
   - **Savings**: 50-70% on compute costs
   - **Impact**: Service unavailable during scaled-down periods

2. **Use Reserved Capacity**
   - Commit to 1-year usage for discounts
   - **Savings**: 20-40% on consistent workloads

### **🔴 Development-Only Mode**
1. **Remove Load Balancer**
   - Access GUI directly via ECS task IP
   - **Savings**: $16/month
   - **Impact**: No high availability, harder to access

## 📊 **COST MONITORING SETUP**

### **Set Up Billing Alerts**
```bash
# Create budget alert for $50/month
aws budgets create-budget \
  --account-id $(aws sts get-caller-identity --query Account --output text) \
  --budget '{
    "BudgetName": "Analytics-Agent-Budget",
    "BudgetLimit": {
      "Amount": "50",
      "Unit": "USD"
    },
    "TimeUnit": "MONTHLY",
    "BudgetType": "COST"
  }'
```

### **Daily Cost Monitoring**
- Enable AWS Cost Explorer
- Set up CloudWatch billing alarms
- Use AWS Cost Anomaly Detection

## 🎯 **RECOMMENDED APPROACH**

### **For Development/Testing**
1. Scale ECS service to 0 when not using: **Saves $17/month**
2. Remove NAT gateways if not needed: **Saves $45/month**
3. **Total monthly cost**: ~$30-50

### **For Production**
1. Keep everything running for reliability
2. Set up auto-scaling based on usage
3. Monitor costs weekly
4. **Total monthly cost**: ~$95-115

### **For Occasional Use**
1. Use Terraform to destroy/recreate as needed
2. Keep S3 and ECR for data/images
3. **Cost when stopped**: ~$1.20/month
4. **Rebuild time**: ~10 minutes

## 🚨 **EMERGENCY COST STOP**

If you see unexpected charges, run this immediately:

```bash
# Stop all compute resources
aws ecs update-service --cluster production-analytics-agent-cluster --service production-analytics-agent-gui-service --desired-count 0 --region us-west-2

# Destroy expensive resources
cd infrastructure
terraform destroy -target=aws_nat_gateway.main -target=aws_eip.nat -target=aws_lb.gui -auto-approve
```

This will bring your costs down to under $5/month within an hour.