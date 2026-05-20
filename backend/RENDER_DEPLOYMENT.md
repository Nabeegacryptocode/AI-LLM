# Render Deployment Guide

## Quick Start

Follow these steps to deploy the IBM Docs LLM API to Render:

### Prerequisites

1. **GitHub Account** - Your code must be in a GitHub repository
2. **Render Account** - Sign up at https://render.com (free tier available)
3. **API Keys Ready**:
   - OpenAI API Key (from https://platform.openai.com)
   - Pinecone API Key (from https://www.pinecone.io)

### Step 1: Push Code to GitHub

```bash
cd backend

# Initialize git if not already done
git init

# Add all files
git add .

# Commit
git commit -m "Prepare for Render deployment"

# Add remote (replace with your repo URL)
git remote add origin https://github.com/yourusername/your-repo.git

# Push to GitHub
git push -u origin main
```

### Step 2: Create Web Service on Render

1. Go to https://dashboard.render.com
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Select the repository containing your backend code
5. Configure the service:
   - **Name**: `ibm-docs-llm-api` (or your preferred name)
   - **Region**: Choose closest to your users
   - **Branch**: `main`
   - **Root Directory**: `backend` (if backend is in a subdirectory)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install --upgrade pip && pip install -r requirements.txt`
   - **Start Command**: `python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT}`

### Step 3: Configure Environment Variables

In the Render dashboard, add these environment variables:

#### Required Variables

| Variable | Value | Notes |
|----------|-------|-------|
| `OPENAI_API_KEY` | `sk-proj-...` | Your OpenAI API key |
| `PINECONE_API_KEY` | `pcsk_...` | Your Pinecone API key |
| `PINECONE_ENVIRONMENT` | `us-west1-gcp` | Your Pinecone environment |
| `PINECONE_INDEX_NAME` | `ibm-docs` | Your Pinecone index name |
| `API_KEY` | Click "Generate" | Secure random key for API auth |

#### Optional Variables (with defaults)

| Variable | Default Value | Description |
|----------|---------------|-------------|
| `LLM_MODEL` | `gpt-4-turbo-preview` | OpenAI model to use |
| `LLM_TEMPERATURE` | `0.7` | Response creativity (0-1) |
| `MAX_TOKENS` | `1000` | Max response length |
| `EMBEDDING_MODEL` | `text-embedding-3-small` | Embedding model |
| `TOP_K_RESULTS` | `5` | Documents to retrieve |
| `ALLOWED_ORIGINS` | `["*"]` | CORS origins (JSON array) |
| `LOG_LEVEL` | `INFO` | Logging level |
| `ENVIRONMENT` | `production` | Environment name |

### Step 4: Deploy

1. Click **"Create Web Service"**
2. Render will automatically:
   - Clone your repository
   - Install dependencies
   - Start your application
3. Monitor the deployment logs in real-time
4. Wait for "Your service is live 🎉" message

### Step 5: Get Your API URL

After successful deployment:
1. Copy your service URL (e.g., `https://ibm-docs-llm-api.onrender.com`)
2. Test the health endpoint:

```bash
curl https://your-service.onrender.com/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "services": {
    "openai": "configured",
    "pinecone": "configured"
  }
}
```

### Step 6: Initialize Pinecone Index

Before using the API, initialize your Pinecone index:

```bash
# Install dependencies locally
pip install -r requirements.txt

# Set environment variables
export PINECONE_API_KEY="your-key"
export PINECONE_ENVIRONMENT="us-west1-gcp"

# Run setup script
python scripts/setup_pinecone.py
```

### Step 7: Test the API

```bash
# Test chat endpoint
curl -X POST https://your-service.onrender.com/api/chat \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is IBM Cloud?",
    "conversation_id": "test-123"
  }'
```

## Common Issues & Solutions

### Issue 1: Build Fails

**Error**: `Could not find a version that satisfies the requirement...`

**Solution**: 
- Check `requirements.txt` for version conflicts
- Ensure `runtime.txt` specifies Python 3.11.0
- Try pinning specific versions

### Issue 2: Service Fails to Start

**Error**: `Application failed to respond`

**Solution**:
1. Check environment variables are set correctly
2. Verify `OPENAI_API_KEY` and `PINECONE_API_KEY` are valid
3. Check logs for specific error messages
4. Ensure `PORT` environment variable is used correctly

### Issue 3: Health Check Fails

**Error**: `Health check failed`

**Solution**:
- Verify `/api/health` endpoint is accessible
- Check if service is listening on `0.0.0.0:${PORT}`
- Review startup logs for errors

### Issue 4: CORS Errors

**Error**: `Access-Control-Allow-Origin` errors

**Solution**:
- Update `ALLOWED_ORIGINS` environment variable
- Format as JSON array: `["https://your-site.com"]`
- Use `["*"]` for testing (not recommended for production)

### Issue 5: Slow Cold Starts

**Issue**: First request after inactivity is slow

**Solution**:
- Upgrade to paid plan (keeps service always running)
- Or implement a cron job to ping your service every 10 minutes:

```bash
# Use a service like cron-job.org or UptimeRobot
# Ping: https://your-service.onrender.com/api/health
```

## Monitoring

### View Logs

1. Go to Render dashboard
2. Select your service
3. Click "Logs" tab
4. View real-time logs

### Set Up Alerts

1. Go to service settings
2. Add notification email
3. Configure alerts for:
   - Deploy failures
   - Service crashes
   - High memory usage

### Metrics

Check API metrics:
```bash
curl https://your-service.onrender.com/api/metrics/summary \
  -H "Authorization: Bearer YOUR_API_KEY"
```

## Updating Your Deployment

### Automatic Deploys

Render automatically deploys when you push to your connected branch:

```bash
git add .
git commit -m "Update feature"
git push origin main
```

### Manual Deploy

1. Go to Render dashboard
2. Select your service
3. Click "Manual Deploy" → "Deploy latest commit"

### Rollback

If something goes wrong:
1. Go to "Events" tab
2. Find previous successful deploy
3. Click "Rollback to this version"

## Scaling

### Vertical Scaling (More Resources)

1. Go to service settings
2. Change instance type:
   - **Starter**: 512 MB RAM, 0.5 CPU
   - **Standard**: 2 GB RAM, 1 CPU
   - **Pro**: 4 GB RAM, 2 CPU

### Horizontal Scaling (More Instances)

Available on paid plans:
1. Go to service settings
2. Increase "Number of instances"
3. Render handles load balancing automatically

## Cost Optimization

### Free Tier Limitations

- Service spins down after 15 minutes of inactivity
- 750 hours/month free
- Slower cold starts

### Paid Plans

- **Starter**: $7/month - Always running, faster
- **Standard**: $25/month - More resources
- **Pro**: $85/month - High performance

### Tips to Reduce Costs

1. Use GPT-3.5-turbo for simple queries
2. Implement caching with Redis
3. Optimize chunk sizes
4. Monitor token usage
5. Set up rate limiting

## Security Best Practices

1. **Rotate API Keys**: Change keys every 90 days
2. **Use Secrets**: Never commit keys to git
3. **Enable HTTPS**: Render provides free SSL
4. **Restrict CORS**: Limit to your domains
5. **Monitor Logs**: Check for suspicious activity
6. **Rate Limiting**: Prevent abuse
7. **Update Dependencies**: Keep packages current

## Next Steps

After successful deployment:

1. ✅ Configure WordPress plugin with your API URL
2. ✅ Ingest IBM documentation
3. ✅ Test end-to-end functionality
4. ✅ Set up monitoring alerts
5. ✅ Configure custom domain (optional)

## Support

- **Render Docs**: https://render.com/docs
- **Render Community**: https://community.render.com
- **Status Page**: https://status.render.com

## Alternative: Using render.yaml

For infrastructure-as-code deployment:

1. Ensure `render.yaml` is in your repository root or backend directory
2. Go to Render dashboard
3. Click "New +" → "Blueprint"
4. Connect repository
5. Render will automatically detect and use `render.yaml`
6. Add environment variables in dashboard
7. Click "Apply"

This method is recommended for:
- Team deployments
- Multiple environments
- Reproducible infrastructure

---

**Deployment Complete!** Your API is now live on Render.

For WordPress integration, use your Render URL in the plugin settings:
- API URL: `https://your-service.onrender.com`
- API Key: (from Render environment variables)
