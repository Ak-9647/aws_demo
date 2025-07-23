#!/bin/bash
# Test Modern GUI Deployment

echo "🧪 Testing Modern GUI Deployment"
echo "================================"

GUI_URL="http://analytics-gui-alb-1184070249.us-west-2.elb.amazonaws.com"

echo "GUI URL: $GUI_URL"
echo ""

# Test 1: Health check
echo "1. Health Check:"
if curl -s -f "$GUI_URL/healthz" > /dev/null; then
    echo "   ✅ GUI is responding"
else
    echo "   ❌ GUI health check failed"
fi

# Test 2: Main page
echo ""
echo "2. Main Page Content:"
CONTENT=$(curl -s "$GUI_URL" 2>/dev/null)

if echo "$CONTENT" | grep -q "Production Analytics Agent"; then
    echo "   ✅ Production Analytics Agent title found"
else
    echo "   ⚠️  Title not found"
fi

if echo "$CONTENT" | grep -q "v4.1"; then
    echo "   ✅ Version v4.1 found"
else
    echo "   ⚠️  Version v4.1 not found"
fi

if echo "$CONTENT" | grep -q "AgentCore"; then
    echo "   ✅ AgentCore references found"
else
    echo "   ⚠️  AgentCore references not found"
fi

if echo "$CONTENT" | grep -q "LangGraph"; then
    echo "   ✅ LangGraph references found"
else
    echo "   ⚠️  LangGraph references not found"
fi

# Test 3: Modern styling
echo ""
echo "3. Modern Styling:"
if echo "$CONTENT" | grep -q "main-header\|metric-card\|feature-badge"; then
    echo "   ✅ Modern CSS classes found"
else
    echo "   ⚠️  Modern CSS classes not found"
fi

# Test 4: Account information
echo ""
echo "4. Account Information:"
if echo "$CONTENT" | grep -q "280383026847"; then
    echo "   ✅ Account ID found"
else
    echo "   ⚠️  Account ID not found"
fi

if echo "$CONTENT" | grep -q "us-west-2"; then
    echo "   ✅ Region found"
else
    echo "   ⚠️  Region not found"
fi

echo ""
echo "🌐 Access your modern GUI at: $GUI_URL"
echo "🎯 The enhanced GUI should now have:"
echo "   - Modern styling with gradients and cards"
echo "   - Updated version information (v4.1)"
echo "   - Correct account and region details"
echo "   - Enhanced connection management"
echo "   - Better performance metrics display"