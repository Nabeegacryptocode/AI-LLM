# 🚀 Deploy to Railway NOW - Quick Start Guide

Follow these steps to deploy your IBM Docs LLM backend to Railway in under 10 minutes!

## Prerequisites Checklist

- ✅ Railway CLI installed (version 4.59.0 detected)
- ✅ Dependencies installed in virtual environment
- ✅ Git repository initialized
- ✅ Railway configuration files created

## Deployment Steps

### Step 1: Login to Railway (Interactive)

Open a **new PowerShell terminal** and run:

```powershell
cd backend
railway login
```

This will open your browser for authentication. Login with your Railway account.

### Step 2: Initialize Railway Project

Choose one option:

**Option A: Create New Project**
```powershell
railway init
```
- Enter a project name (e.g., "ibm-docs-llm")
- Press Enter

**Option B: Link Existing Project**
```powershell
railway link
```
- Select your existing project from the list

### Step 3: Set Environment Variables

Copy and paste these commands one by one:

```powershell
# Required: OpenAI API Key
railway variables set OPENAI_API_KEY="your-openai-api-key-here"

# Required: Pinecone API Key
railway variables set PINECONE_API_KEY="your-pinecone-api-key-here"

# Required: Pinecone Environment
railway variables set PINECONE_ENVIRONMENT="us-west1-gcp"

# Required: Pinecone Index Name
railway variables set PINECONE_INDEX_NAME="ibm-docs"

# Required: Generate API Key for WordPress
# First, generate a secure key:
$apiKey = -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | ForEach-Object {[char]$_})
Write-Host "Your API Key: $apiKey" -ForegroundColor Green
Write-Host "SAVE THIS KEY - You'll need it for WordPress!" -ForegroundColor Red

# Then set it:
railway variables set API_KEY="$apiKey"

# Optional: CORS (allows all origins for now)
railway variables set ALLOWED_ORIGINS='["*"]'

# Optional: Environment
railway variables set ENVIRONMENT="production"

# Optional: Logging
railway variables set LOG_LEVEL="INFO"
```

**IMPORTANT:** Save the generated API Key! You'll need it to configure the WordPress plugin.

### Step 4: Deploy to Railway

```powershell
railway up
```

Wait for the deployment to complete (2-5 minutes). You'll see build logs in real-time.

### Step 5: Generate Public Domain

```powershell
railway domain
```

This will give you a public URL like: `https://your-app-name.railway.app`

**Save this URL!** You'll need it for WordPress configuration.

### Step 6: Verify Deployment

Test the health endpoint:

```powershell
# Replace YOUR-APP-NAME with your actual Railway domain
curl https://YOUR-APP-NAME.railway.app/api/health
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

## Alternative: Deploy via Railway Dashboard

If you prefer a GUI:

1. **Go to Railway Dashboard**: https://railway.app/dashboard
2. **Click "New Project"**
3. **Select "Deploy from GitHub repo"**
4. **Connect your GitHub account** and select your repository
5. **Set Root Directory**: Select `backend` folder
6. **Add Environment Variables**: 
   - Go to "Variables" tab
   - Add all variables from Step 3 above
7. **Deploy**: Railway will automatically build and deploy
8. **Generate Domain**: Go to Settings → Generate Domain

## Post-Deployment Tasks

### 1. Initialize Pinecone Index

Run locally (make sure you're in the backend directory):

```powershell
python scripts/setup_pinecone.py
```

This creates the vector database index in Pinecone.

### 2. Ingest IBM Documentation

Start with a small test:

```powershell
python scripts/ingest_ibm_docs.py --sections overview --max-pages 20
```

Monitor progress:
```powershell
# Check logs
railway logs

# Or view in dashboard
railway open
```

### 3. Test the Chat Endpoint

```powershell
# Replace YOUR-APP-URL and YOUR-API-KEY with your actual values
curl -X POST https://YOUR-APP-URL/api/chat `
  -H "Authorization: Bearer YOUR-API-KEY" `
  -H "Content-Type: application/json" `
  -d '{\"question\": \"What is IBM Cloud?\"}'
```

### 4. Configure WordPress Plugin

1. Go to WordPress Admin → Settings → IBM Docs LLM
2. **API URL**: `https://YOUR-APP-NAME.railway.app`
3. **API Key**: (the key you generated in Step 3)
4. Click "Test API Connection"
5. Save settings

## Monitoring & Management

### View Logs
```powershell
railway logs
```

### View Dashboard
```powershell
railway open
```

### Check Metrics
```powershell
curl https://YOUR-APP-URL/api/metrics/summary `
  -H "Authorization: Bearer YOUR-API-KEY"
```

### Update Deployment
```powershell
# After making code changes
git add .
git commit -m "Update application"
railway up
```

## Troubleshooting

### Build Fails
- Check logs: `railway logs`
- Verify all files are committed: `git status`
- Check requirements.txt is up to date

### API Returns 500 Error
- Verify environment variables are set: `railway variables`
- Check OpenAI and Pinecone keys are valid
- View detailed logs: `railway logs`

### Can't Access from WordPress
- Verify the Railway domain is correct
- Check CORS settings (should be `["*"]` for testing)
- Ensure WordPress site has HTTPS

### High Costs
- Monitor usage in Railway dashboard
- Check OpenAI usage at https://platform.openai.com/usage
- Reduce `MAX_TOKENS` and `TOP_K_RESULTS` if needed

## Cost Estimates

**Railway:**
- Hobby Plan: $5/month (500 hours)
- Pro Plan: $20/month (unlimited)

**OpenAI:**
- GPT-4 Turbo: ~$0.01 per 1K input tokens
- Embeddings: ~$0.0001 per 1K tokens
- Estimated: $10-50/month depending on usage

**Pinecone:**
- Free tier: 100K vectors (good for testing)
- Starter: $70/month (5M vectors)

## Quick Reference

**Your Deployment Info:**
- Railway URL: `https://YOUR-APP-NAME.railway.app`
- API Key: `[SAVE FROM STEP 3]`
- Health Check: `https://YOUR-APP-NAME.railway.app/api/health`

**Important Commands:**
```powershell
railway logs          # View logs
railway open          # Open dashboard
railway up            # Deploy/update
railway domain        # Get/generate domain
railway variables     # List variables
```

## Next Steps

After successful deployment:

1. ✅ Test all API endpoints
2. ✅ Ingest more IBM documentation
3. ✅ Configure WordPress plugin
4. ✅ Test end-to-end with real questions
5. ✅ Set up monitoring alerts
6. ✅ Plan for scaling

---

## Need Help?

- **Railway Docs**: https://docs.railway.app
- **Railway Discord**: https://discord.gg/railway
- **Check Logs**: `railway logs`
- **View Dashboard**: `railway open`

---

**Ready to deploy? Start with Step 1 above!** 🚀

Your application is configured and ready. Just follow the steps in order, and you'll be live in minutes!