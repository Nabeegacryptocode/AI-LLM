# Railway Deployment Guide for IBM Docs LLM

This guide will walk you through deploying the IBM Docs LLM backend to Railway.

## Prerequisites

1. **Railway Account**: Sign up at https://railway.app
2. **GitHub Account**: For connecting your repository
3. **API Keys Ready**:
   - OpenAI API Key (already in .railway-env-template)
   - Pinecone API Key (already in .railway-env-template)

## Deployment Steps

### Option 1: Deploy via Railway Dashboard (Recommended)

#### Step 1: Prepare Your Repository

1. **Initialize Git in the backend folder** (if not already done):
   ```bash
   cd backend
   git init
   git add .
   git commit -m "Initial commit for Railway deployment"
   ```

2. **Push to GitHub**:
   ```bash
   # Create a new repository on GitHub first, then:
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
   git branch -M main
   git push -u origin main
   ```

#### Step 2: Deploy to Railway

1. **Go to Railway Dashboard**:
   - Visit https://railway.app
   - Click "New Project"
   - Select "Deploy from GitHub repo"

2. **Connect Your Repository**:
   - Authorize Railway to access your GitHub
   - Select your repository
   - Select the `backend` folder as the root directory

3. **Configure Environment Variables**:
   - Railway will detect the Python app automatically
   - Go to "Variables" tab
   - Add the following variables (from `.railway-env-template`):

   **Required Variables:**
   ```
OPENAI_API_KEY=your-openai-api-key-here
   
PINECONE_API_KEY=your-pinecone-api-key-here
   
   PINECONE_ENVIRONMENT=us-west1-gcp
   
   PINECONE_INDEX_NAME=ibm-docs
   
   API_KEY=<GENERATE_A_SECURE_KEY>
   ```

   **Generate API_KEY** (run this locally):
   ```bash
   # On Windows PowerShell:
   -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | ForEach-Object {[char]$_})
   
   # On Linux/Mac:
   openssl rand -base64 32
   ```

   **Optional Variables** (recommended):
   ```
   ALLOWED_ORIGINS=["*"]
   LLM_MODEL=gpt-4-turbo-preview
   ENVIRONMENT=production
   LOG_LEVEL=INFO
   ```

4. **Deploy**:
   - Railway will automatically build and deploy
   - Wait for deployment to complete (usually 2-5 minutes)

5. **Get Your Deployment URL**:
   - Go to "Settings" tab
   - Click "Generate Domain"
   - Your API will be available at: `https://your-app.railway.app`

### Option 2: Deploy via Railway CLI

#### Step 1: Install Railway CLI

```bash
# Windows (PowerShell as Administrator):
iwr https://railway.app/install.ps1 | iex

# Mac/Linux:
curl -fsSL https://railway.app/install.sh | sh
```

#### Step 2: Login and Initialize

```bash
cd backend

# Login to Railway
railway login

# Initialize project
railway init

# Link to existing project or create new one
railway link
```

#### Step 3: Set Environment Variables

```bash
# Set required variables
railway variables set OPENAI_API_KEY="your-openai-api-key-here"

railway variables set PINECONE_API_KEY="your-pinecone-api-key-here"

railway variables set PINECONE_ENVIRONMENT="us-west1-gcp"

railway variables set PINECONE_INDEX_NAME="ibm-docs"

# Generate and set API key
railway variables set API_KEY="$(openssl rand -base64 32)"

# Optional variables
railway variables set ALLOWED_ORIGINS='["*"]'
railway variables set ENVIRONMENT="production"
```

#### Step 4: Deploy

```bash
# Deploy to Railway
railway up

# Get deployment URL
railway domain
```

## Post-Deployment Steps

### 1. Verify Deployment

Test the health endpoint:
```bash
curl https://your-app.railway.app/api/health
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

### 2. Initialize Pinecone Index

You need to create the Pinecone index before ingesting documents:

```bash
# Run locally with your Pinecone credentials
cd backend
python scripts/setup_pinecone.py
```

### 3. Test the Chat Endpoint

```bash
# Replace YOUR_API_KEY with the API_KEY you set in Railway
curl -X POST https://your-app.railway.app/api/chat \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is IBM Cloud?"}'
```

### 4. Ingest Documentation

```bash
# Run locally to ingest IBM documentation
cd backend
python scripts/ingest_ibm_docs.py --sections overview --max-pages 20
```

### 5. Configure WordPress Plugin

1. Go to your WordPress Admin → Settings → IBM Docs LLM
2. Enter API URL: `https://your-app.railway.app`
3. Enter API Key: (the API_KEY you generated)
4. Click "Test API Connection"
5. Save settings

## Monitoring

### View Logs

**Via Dashboard:**
- Go to Railway Dashboard
- Select your project
- Click "Deployments" tab
- View real-time logs

**Via CLI:**
```bash
railway logs
```

### Check Metrics

```bash
curl https://your-app.railway.app/api/metrics/summary \
  -H "Authorization: Bearer YOUR_API_KEY"
```

## Updating Your Deployment

### Via Git Push (Automatic)

```bash
cd backend
git add .
git commit -m "Update application"
git push origin main
```

Railway will automatically redeploy on push.

### Via CLI

```bash
cd backend
railway up
```

## Troubleshooting

### Build Fails

1. **Check logs**: `railway logs`
2. **Verify requirements.txt**: Ensure all dependencies are listed
3. **Check Python version**: Railway uses Python 3.11 by default

### API Returns 500 Error

1. **Check environment variables**: Ensure all required variables are set
2. **Verify API keys**: Test OpenAI and Pinecone keys locally
3. **Check logs**: `railway logs` for detailed error messages

### Can't Connect from WordPress

1. **Verify URL**: Ensure you're using the correct Railway domain
2. **Check CORS**: Set `ALLOWED_ORIGINS` to include your WordPress site
3. **Test endpoint**: Use curl to verify API is accessible

### High Costs

1. **Monitor usage**: Check Railway dashboard for resource usage
2. **Optimize queries**: Reduce `TOP_K_RESULTS` and `MAX_TOKENS`
3. **Add caching**: Implement Redis for frequently asked questions

## Cost Estimation

**Railway Costs:**
- Hobby Plan: $5/month (500 hours)
- Pro Plan: $20/month (unlimited)

**OpenAI Costs:**
- GPT-4 Turbo: ~$0.01 per 1K input tokens, ~$0.03 per 1K output tokens
- Embeddings: ~$0.0001 per 1K tokens

**Pinecone Costs:**
- Free tier: 100K vectors (sufficient for testing)
- Starter: $70/month (5M vectors)

## Security Best Practices

1. **Rotate API Keys**: Change keys every 90 days
2. **Use Strong API_KEY**: Generate with `openssl rand -base64 32`
3. **Restrict CORS**: Set specific origins instead of `["*"]`
4. **Enable Rate Limiting**: Monitor and limit requests
5. **Monitor Logs**: Check for suspicious activity

## Support

- **Railway Docs**: https://docs.railway.app
- **Railway Discord**: https://discord.gg/railway
- **Project Issues**: Check logs and error messages first

## Next Steps

After successful deployment:

1. ✅ Test all API endpoints
2. ✅ Ingest IBM documentation
3. ✅ Configure WordPress plugin
4. ✅ Test end-to-end functionality
5. ✅ Set up monitoring alerts
6. ✅ Plan for scaling

---

**Your IBM Docs LLM API is now live on Railway!** 🚀

Save your deployment URL and API key for WordPress plugin configuration.