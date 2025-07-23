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

## ✅ RESOLVED CRITICAL ISSUES

### **AgentCore Gateway Successfully Created** ✅ **RESOLVED**
**Problem**: AgentCore Gateways needed manual creation through AWS Console.

**Resolution Status**: 
- ✅ Database Gateway Created: `production-analytics-agent-database-gateway-wni9bfjx64`
- ✅ Lambda Target Working: `database-target` with minimal schema `{}`
- ✅ Authentication Configured: Cognito with JWT tokens
- ✅ Lambda Function Responding: Health checks passing
- ✅ AgentCore Runtime Active: `arn:aws:bedrock-agentcore:us-west-2:280383026847:runtime/hosted_agent_jqgjl-fJiyIV95k9`

**Current Operational Status**:
- ✅ Gateway connectivity established
- ✅ Lambda function processing requests
- ✅ Authentication flow working
- ✅ Infrastructure fully deployed
- ✅ GUI accessible at: http://analytics-gui-alb-1184070249.us-west-2.elb.amazonaws.com

**Key Learnings**:
- AgentCore Gateways require minimal inline schemas (`{}`) for Lambda targets
- Complex OpenAPI schemas cause validation errors
- Cognito authentication works well with AgentCore
- Lambda functions need proper error handling for AgentCore integration

## 🚀 CURRENT STATUS

**✅ FULLY OPERATIONAL**: Production Analytics Agent v4.1 is deployed and working
**✅ GATEWAY ACTIVE**: Database gateway with working Lambda target
**✅ AGENTCORE RUNTIME**: Agent endpoint available for invocation
**✅ INFRASTRUCTURE**: Complete AWS deployment with all components healthy
**✅ EVALUATION READY**: Comprehensive evaluation suite implemented

**🎯 CURRENT PHASE**: System evaluation and performance optimization

## 📊 EVALUATION FRAMEWORK IMPLEMENTED

### **Comprehensive Evaluation Strategy** ✅ **COMPLETED**
**Implementation**: 
- ✅ Evaluation Strategy Document: `docs/EVALUATION_STRATEGY.md`
- ✅ Automated Test Suite: `scripts/evaluation_suite.py`
- ✅ Test Runner Script: `scripts/run_evaluation.sh`
- ✅ Performance Benchmarks: Response time, throughput, scalability
- ✅ Security Validation: Authentication, authorization, encryption
- ✅ Integration Testing: Gateway connectivity, database access
- ✅ Functional Testing: Analytics accuracy, visualization quality

**Test Categories**:
1. **Infrastructure Tests**: Health checks for all AWS components
2. **Functional Tests**: Core analytics capabilities and accuracy
3. **Performance Tests**: Response time, throughput, concurrent users
4. **Security Tests**: Authentication, authorization, data protection
5. **Integration Tests**: Gateway connectivity, external systems

**Success Criteria**:
- Success Rate Target: >90% for production readiness
- Response Time: <5 seconds (95th percentile)
- Throughput: >25 requests/second
- Availability: >99.5% uptime
- Security: Zero critical vulnerabilities

**Usage**:
```bash
# Run complete evaluation
./scripts/run_evaluation.sh

# View results
cat evaluation_reports/evaluation_report_*.json
```