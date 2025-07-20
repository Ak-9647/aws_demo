# Issues Faced During Development

## 🚨 CRITICAL ISSUES RESOLVED

### 1. **AgentCore 404 Errors** ⚠️
**Problem**: AgentCore was returning 404 errors when trying to reach our container
**Root Cause**: Multiple issues with container format and runtime expectations
**Solutions Applied**:
- ❌ **Attempt 1**: Lambda runtime approach - AgentCore couldn't find handler
- ❌ **Attempt 2**: Lambda with runtime API - Still getting 404s
- ✅ **Final Solution**: HTTP server approach with proper endpoints

**Key Learnings**:
- AgentCore expects HTTP endpoints, not Lambda handlers
- Container must expose port 8080 and handle POST requests
- Health check endpoint `/health` is important for container health

### 2. **IAM Trust Policy Issues** 🔐
**Problem**: Invalid service principals in IAM trust policies
**Error**: `Invalid principal in policy: "SERVICE:bedrock-agentcore.amazonaws.com"`
**Root Cause**: Incorrect service principal format for Bedrock AgentCore
**Solution**: Updated trust policies with correct AWS service principals

**Fixed In**: `infrastructure/iam.tf`
```hcl
# Before (broken)
"SERVICE:bedrock-agentcore.amazonaws.com"

# After (working)  
"bedrock.amazonaws.com"
```

### 3. **Container URI Validation** 📦
**Problem**: Container URI failed AgentCore validation regex
**Error**: `Member must satisfy regular expression pattern: \d{12}.dkr.ecr.([a-z0-9-]+).amazonaws.com/...`
**Root Cause**: Missing explicit tag in container URI
**Solution**: Added explicit version tag instead of using `:latest`

**Fixed Format**:
```
# Before (failed validation)
280383026847.dkr.ecr.us-west-2.amazonaws.com/production-analytics-agent-agent:latest

# After (passed validation)
280383026847.dkr.ecr.us-west-2.amazonaws.com/production-analytics-agent-agent:v1.0
```

### 4. **Docker Build Context Issues** 🐳
**Problem**: Docker build failing with "file not found" errors
**Root Cause**: `.dockerignore` was excluding necessary files
**Solution**: Updated `.dockerignore` to include required files

**Fixed In**: `agent/.dockerignore`
```
# Before (too restrictive)
*
!server.py
!requirements.txt

# After (includes needed files)
*
!main.py
!app.py
!requirements.txt
```

## ⚠️ MODERATE ISSUES RESOLVED

### 5. **Incomplete Code Files** 📝
**Problem**: `agent/app.py` was truncated mid-function
**Root Cause**: File editing error during development
**Solution**: Completed the lambda_handler function with proper error handling

### 6. **Unnecessary Dependencies** 📚
**Problem**: Flask dependency included but not used
**Root Cause**: Copy-paste from different implementation approach
**Solution**: Removed Flask, using built-in HTTP server instead

### 7. **Account ID Mismatches** 🏢
**Problem**: Using wrong AWS account ID in ECR URLs
**Root Cause**: Copy-paste from documentation with different account
**Solution**: Used `aws sts get-caller-identity` to get correct account ID

## 🔍 DEBUGGING TECHNIQUES USED

### CloudWatch Logs Analysis
- Used `aws logs tail` to monitor real-time container logs
- Identified that containers were starting but not receiving requests
- Found cron job patterns indicating Lambda runtime issues

### Local Container Testing
- Used `docker run -p 8080:8080` to test containers locally
- Verified HTTP endpoints work before pushing to ECR
- Used `curl` commands to test POST requests and health checks

### Terraform State Management
- Used `terraform plan` and `terraform output` to verify infrastructure
- Checked ECR repository URLs and IAM role ARNs
- Ensured infrastructure was properly deployed before container testing

## 📚 LESSONS LEARNED

### 1. **AgentCore Expectations**
- AgentCore expects HTTP servers, not Lambda functions
- Port 8080 is the standard for AgentCore containers
- Health checks are important for container lifecycle management

### 2. **Container Development Best Practices**
- Always test containers locally before pushing to ECR
- Use explicit tags instead of `:latest` for production
- Keep `.dockerignore` minimal but effective

### 3. **AWS Service Integration**
- IAM trust policies must use exact service principal formats
- ECR URIs must include explicit tags for validation
- CloudWatch logs are essential for debugging container issues

### 4. **Development Workflow**
- Infrastructure first, then application code
- Test each component independently before integration
- Use Terraform outputs to get correct resource identifiers

## 🚀 CURRENT STATUS

**✅ RESOLVED**: All critical blocking issues are fixed
**✅ WORKING**: Basic HTTP server container responding to requests
**✅ DEPLOYED**: Container pushed to ECR with proper tagging
**✅ TESTED**: Local testing confirms functionality

**🎯 READY FOR**: Next phase of development (analytics logic or GUI implementation)