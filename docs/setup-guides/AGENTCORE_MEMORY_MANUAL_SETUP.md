# AgentCore Memory Manual Setup Guide

## Overview

Since AgentCore Memory is in preview and not yet available in Terraform, we'll create the memory resources manually through the AWS Console. This guide provides step-by-step instructions based on the actual console interface for setting up memory resources for the Production Analytics Agent.

## Prerequisites

- AWS Console access to Amazon Bedrock
- AgentCore permissions in us-west-2 region
- Agent ID: `hosted_agent_jqgjl-fJiyIV95k9`

## Memory Resources to Create

Based on our architecture and the console interface, we need to create the following memory resources:

### 1. Conversation Memory
- **Purpose**: Store conversation history and context
- **Memory Name**: `production-analytics-agent-conversation-memory`
- **Short-term Expiration**: 7 days
- **Long-term Strategy**: Summarization with custom namespace

### 2. User Preferences Memory
- **Purpose**: Store user preferences and learning patterns
- **Memory Name**: `production-analytics-agent-user-preferences`
- **Short-term Expiration**: 30 days
- **Long-term Strategy**: Semantic memory

### 3. Session Context Memory
- **Purpose**: Store session-specific context and state
- **Memory Name**: `production-analytics-agent-session-context`
- **Short-term Expiration**: 1 day
- **Long-term Strategy**: None (short-term only)

### 4. Analytics Context Memory
- **Purpose**: Store analytics query patterns and insights
- **Memory Name**: `production-analytics-agent-analytics-context`
- **Short-term Expiration**: 14 days
- **Long-term Strategy**: Summarization with analytics namespace

## Step-by-Step Setup Instructions

### Step 1: Create Conversation Memory

1. **Navigate to AgentCore Memory Console**
   - Go to: https://us-west-2.console.aws.amazon.com/bedrock/home?region=us-west-2#/agentcore/memory
   - Click the orange "Create memory" button

2. **Memory Detail Configuration**
   - **Memory name**: `production-analytics-agent-conversation-memory`
   - **Short-term memory (raw event) expiration**: `7` days
   - Note: Valid duration is between 1 and 365 days

3. **Long-term Memory Extraction Strategies (Optional)**
   - ✅ Check "Built-in strategies"
   - Select "Summarization" checkbox
   - This will summarize interactions to preserve critical context and key insights

4. **Additional Configurations (Optional)**
   - Click the dropdown arrow to expand if you want to add custom strategies
   - For now, we'll use the built-in summarization strategy

5. **Click "Create memory"**

### Step 2: Create User Preferences Memory

1. **Click "Create memory" again**

2. **Memory Detail Configuration**
   - **Memory name**: `production-analytics-agent-user-preferences`
   - **Short-term memory expiration**: `30` days

3. **Long-term Memory Extraction Strategies**
   - Check "Built-in strategies"
   - Select "Semantic memory"
   - **Strategy name**: `user_preferences_semantic_v1`
   - **Strategy type**: Semantic memory
   - **Namespace**: `/strategies/memory/users/{userId}/preferences`

4. **Click "Create memory"**

### Step 3: Create Session Context Memory

1. **Click "Create memory" again**

2. **Memory Detail Configuration**
   - **Memory name**: `production-analytics-agent-session-context`
   - **Short-term memory expiration**: `1` days

3. **Long-term Memory Extraction Strategies**
   - Leave unchecked (short-term only)

4. **Click "Create memory"**

### Step 4: Create Analytics Context Memory

1. **Click "Create memory" again**

2. **Memory Detail Configuration**
   - **Memory name**: `production-analytics-agent-analytics-context`
   - **Short-term memory expiration**: `14` days

3. **Long-term Memory Extraction Strategies**
   - Check "Built-in strategies"
   - Select "Summarization"
   - **Strategy name**: `analytics_summarization_v1`
   - **Strategy type**: Summarization
   - **Namespace**: `/strategies/memory/analytics/{userId}/patterns`

4. **Click "Create memory"**

## Post-Creation Configuration

### Step 5: Record Memory IDs

After creating each memory resource, record the Memory IDs for configuration:

1. Go to the Memory list page
2. Copy each Memory ID
3. Update your environment variables or configuration:

```bash
# Environment Variables
export CONVERSATION_MEMORY_ID="memory-id-from-console"
export USER_PREFERENCES_MEMORY_ID="memory-id-from-console"
export SESSION_CONTEXT_MEMORY_ID="memory-id-from-console"
export ANALYTICS_CONTEXT_MEMORY_ID="memory-id-from-console"
```

### Step 6: Update Agent Configuration

Update your agent code to use the new memory IDs:

```python
# In your agent configuration
MEMORY_CONFIG = {
    'conversation': os.environ.get('CONVERSATION_MEMORY_ID'),
    'user_preferences': os.environ.get('USER_PREFERENCES_MEMORY_ID'),
    'session_context': os.environ.get('SESSION_CONTEXT_MEMORY_ID'),
    'analytics_context': os.environ.get('ANALYTICS_CONTEXT_MEMORY_ID')
}
```

### Step 7: Test Memory Integration

Use the AgentCore Memory integration module to test the setup:

```python
from agentcore_memory_integration import get_agentcore_memory

# Test the memory integration
memory = get_agentcore_memory()
health_check = memory.health_check()
print(f"Memory health check: {health_check}")
```

## Memory Strategy Details

### Conversation Memory Strategy
```yaml
Strategy Type: Summarization
Purpose: Preserve critical context and key insights from conversations
Retention: 
  - Raw events: 7 days
  - Summaries: 90 days
Namespace Pattern: /strategies/memory/conversation/sessions/{sessionId}
```

### User Preferences Strategy
```yaml
Strategy Type: Semantic Memory
Purpose: Learn and adapt to user preferences and patterns
Retention:
  - Raw events: 30 days
  - Semantic patterns: 365 days
Namespace Pattern: /strategies/memory/users/{userId}/preferences
```

### Analytics Context Strategy
```yaml
Strategy Type: Summarization
Purpose: Capture analytics query patterns and insights
Retention:
  - Raw events: 14 days
  - Summaries: 180 days
Namespace Pattern: /strategies/memory/analytics/{userId}/patterns
```

## Integration with Existing Infrastructure

### IAM Permissions Required

Add these permissions to your agent's IAM role:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:GetMemory",
                "bedrock:PutMemory",
                "bedrock:DeleteMemory",
                "bedrock:ListMemories",
                "bedrock:UpdateMemory"
            ],
            "Resource": [
                "arn:aws:bedrock:us-west-2:*:memory/production-analytics-agent-*"
            ]
        }
    ]
}
```

### Environment Variables

Set these environment variables in your ECS task definition or Lambda function:

```bash
CONVERSATION_MEMORY_ID=your-conversation-memory-id
USER_PREFERENCES_MEMORY_ID=your-user-preferences-memory-id
SESSION_CONTEXT_MEMORY_ID=your-session-context-memory-id
ANALYTICS_CONTEXT_MEMORY_ID=your-analytics-context-memory-id
```

## Monitoring and Observability

### CloudWatch Metrics

Monitor these key metrics:
- Memory usage per resource
- Query response times
- Error rates
- Memory extraction success rates

### Logging

Enable detailed logging for memory operations:
- Memory read/write operations
- Strategy execution results
- Error conditions and fallbacks

## Troubleshooting

### Common Issues

1. **Memory ID Not Found**
   - Verify the memory ID is correct
   - Check the region (must be us-west-2)
   - Ensure proper IAM permissions

2. **Permission Denied**
   - Check IAM role has bedrock:GetMemory permissions
   - Verify resource ARN patterns match

3. **Memory Extraction Failures**
   - Check strategy configuration
   - Verify namespace patterns
   - Monitor CloudWatch logs

### Testing Commands

```bash
# Test memory health
aws bedrock-agent get-memory --memory-id your-memory-id --region us-west-2

# List all memories
aws bedrock-agent list-memories --region us-west-2
```

## Next Steps

1. **Create Memory Resources**: Follow the step-by-step instructions above
2. **Update Agent Code**: Integrate the memory IDs into your agent configuration
3. **Test Integration**: Use the provided test scripts to verify functionality
4. **Monitor Performance**: Set up CloudWatch monitoring and alerting
5. **Optimize Strategies**: Fine-tune memory extraction strategies based on usage patterns

## Benefits of AgentCore Memory

### Over Traditional Memory (DynamoDB + Redis)
- **Intelligent Summarization**: Automatic extraction of key insights
- **Semantic Understanding**: Better context preservation
- **Managed Service**: No infrastructure to maintain
- **Built-in Strategies**: Pre-configured memory management patterns
- **Cost Optimization**: Pay only for what you use

### Enhanced Agent Capabilities
- **Better Context Retention**: Long-term memory with intelligent summarization
- **User Adaptation**: Learning from user interaction patterns
- **Session Continuity**: Seamless context across sessions
- **Analytics Insights**: Pattern recognition in query behavior

---

**Status**: Ready for Manual Setup  
**Estimated Setup Time**: 15-20 minutes  
**Prerequisites**: AWS Console access with Bedrock permissions  
**Next Phase**: Agent Integration and Testing