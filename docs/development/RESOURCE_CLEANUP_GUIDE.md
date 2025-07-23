# 🧹 AWS Resource Cleanup Guide

## 🎯 **Quick Reference**

### **🚨 Emergency Stop (Immediate)**
```bash
./scripts/emergency-stop.sh
```
**Effect**: Stops ECS service immediately, saves $18/month

### **🖥️ Interactive Cleanup**
```bash
./scripts/cleanup-resources.sh
```
**Effect**: Menu-driven cleanup with multiple options

### **🐍 Advanced Management**
```bash
python3 scripts/resource_manager.py --interactive
```
**Effect**: Advanced resource management with cost tracking

## 📊 **Cleanup Options & Savings**

### **Option 1: Scale Down ECS Only**
- **Savings**: ~$18/month
- **What it does**: Stops GUI container, keeps infrastructure
- **Restart time**: ~2 minutes
- **Command**: 
  ```bash
  ./scripts/resource_manager.py --cleanup-1
  ```

### **Option 2: Remove Expensive Resources**
- **Savings**: ~$68/month  
- **What it does**: Removes NAT gateways, load balancer, EIPs
- **Restart time**: ~10 minutes
- **Command**:
  ```bash
  ./scripts/resource_manager.py --cleanup-2
  ```

### **Option 3: Destroy Everything**
- **Savings**: ~$95/month
- **What it does**: Removes all infrastructure except S3/ECR
- **Restart time**: ~15 minutes
- **Command**:
  ```bash
  ./scripts/resource_manager.py --cleanup-3
  ```

## 🔄 **Restart Commands**

### **Restart ECS Service Only**
```bash
aws ecs update-service \
  --cluster production-analytics-agent-cluster \
  --service production-analytics-agent-gui-service \
  --desired-count 1 \
  --region us-west-2
```

### **Restart All Infrastructure**
```bash
cd infrastructure
terraform apply -auto-approve
```

### **Using Resource Manager**
```bash
python3 scripts/resource_manager.py --restart-all
```

## 📈 **Cost Monitoring**

### **Check Current Status**
```bash
python3 scripts/resource_manager.py --status
```

**Shows**:
- ECS service status
- Load balancer status  
- NAT gateway count
- Elastic IP allocation
- Recent AWS costs
- Estimated savings

### **Example Output**:
```
📊 AWS Resource Summary
==================================================
🐳 ECS Service: ACTIVE
   Running: 1/1
⚖️  Load Balancers: 1 found
   analytics-gui-alb: active
🌐 NAT Gateways: 2 active
📍 Elastic IPs: 2 allocated

💰 Recent Costs (Last 7 days):
   Amazon Elastic Compute Cloud: $12.45
   Amazon Elastic Load Balancing: $3.22
   Amazon Virtual Private Cloud: $8.90
   TOTAL: $24.57

💡 Estimated Monthly Savings:
   Scale down ECS: ~$18/month
   Remove expensive resources: ~$68/month
   Destroy all: ~$95/month
```

## ⚡ **Quick Commands Reference**

### **Emergency Situations**
```bash
# Immediate stop (saves $18/month)
./scripts/emergency-stop.sh

# Remove expensive resources (saves $68/month)
./scripts/cleanup-resources.sh
# Choose option 3

# Nuclear option - destroy everything (saves $95/month)
./scripts/cleanup-resources.sh
# Choose option 4
```

### **Daily Management**
```bash
# Check what's running and costing money
python3 scripts/resource_manager.py --status

# Scale down for the night
python3 scripts/resource_manager.py --cleanup-1

# Scale back up in the morning
python3 scripts/resource_manager.py --restart-ecs
```

### **Weekend/Vacation Mode**
```bash
# Friday evening - remove expensive resources
python3 scripts/resource_manager.py --cleanup-2

# Monday morning - restart everything
python3 scripts/resource_manager.py --restart-all
```

## 🛡️ **Safety Features**

### **What's Protected**
- **S3 Data**: Never deleted (your uploaded data is safe)
- **ECR Images**: Never deleted (your container images are safe)
- **IAM Roles**: Never deleted (permissions preserved)

### **Confirmation Required**
- **Destroy All**: Requires typing 'yes' to confirm
- **Expensive Operations**: Shows cost impact before proceeding
- **Terraform State**: Preserved for easy restoration

### **Rollback Capability**
- All operations can be reversed
- Terraform state tracks what was removed
- Simple commands to restore everything

## 📋 **Recommended Usage Patterns**

### **For Development/Learning**
```bash
# Work session start
python3 scripts/resource_manager.py --restart-ecs

# Work session end  
python3 scripts/resource_manager.py --cleanup-1
```
**Monthly cost**: ~$77 instead of $95

### **For Weekend Projects**
```bash
# Weekend start
python3 scripts/resource_manager.py --restart-all

# Weekend end
python3 scripts/resource_manager.py --cleanup-2
```
**Monthly cost**: ~$27 instead of $95

### **For Long Breaks**
```bash
# Going away for a week+
python3 scripts/resource_manager.py --cleanup-3

# Coming back
python3 scripts/resource_manager.py --restart-all
```
**Monthly cost**: ~$1.20 while away

## 🔧 **Troubleshooting**

### **Script Won't Run**
```bash
# Make scripts executable
chmod +x scripts/*.sh
chmod +x scripts/*.py

# Check AWS credentials
aws sts get-caller-identity
```

### **Terraform Errors**
```bash
# Refresh terraform state
cd infrastructure
terraform refresh

# Force unlock if stuck
terraform force-unlock <LOCK_ID>
```

### **ECS Service Won't Stop**
```bash
# Force stop all tasks
aws ecs list-tasks --cluster production-analytics-agent-cluster --region us-west-2
aws ecs stop-task --cluster production-analytics-agent-cluster --task <TASK_ARN> --region us-west-2
```

## 💡 **Pro Tips**

1. **Set up billing alerts** at $50, $75, and $100
2. **Use cleanup-1 daily** when not actively developing
3. **Use cleanup-2 on weekends** for maximum savings
4. **Monitor costs weekly** with the status command
5. **Keep S3 data** - it's only ~$0.50/month

## 🎯 **Cost Optimization Strategy**

### **Aggressive Savings (90% cost reduction)**
- Use cleanup-3 when not using the system
- Only restart when needed
- **Result**: $1.20/month baseline, $95/month when active

### **Balanced Approach (70% cost reduction)**  
- Use cleanup-2 during off-hours
- Keep basic infrastructure running
- **Result**: ~$27/month average

### **Minimal Effort (20% cost reduction)**
- Use cleanup-1 when not actively using GUI
- Keep everything else running
- **Result**: ~$77/month average

**The choice is yours based on how frequently you use the system!**