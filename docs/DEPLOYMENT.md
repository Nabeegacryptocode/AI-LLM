# Deployment Guide - IBM Docs LLM

Complete guide for deploying the IBM Documentation LLM system to production.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Backend Deployment](#backend-deployment)
3. [WordPress Plugin Deployment](#wordpress-plugin-deployment)
4. [Post-Deployment](#post-deployment)
5. [Monitoring & Maintenance](#monitoring--maintenance)
6. [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Services

1. **OpenAI Account**
   - Sign up at https://platform.openai.com
   - Create API key
   - Add payment method
   - Recommended: Tier 1+ for higher rate limits

2. **Pinecone Account**
   - Sign up at https://www.pinecone.io
   - Create project
   - Get API key and environment
   - Free tier: 100k vectors, 1 index

3. **Hosting Platform** (choose one)
   - Railway (recommended for beginners)
   - Render
   - AWS/GCP/Azure
   - DigitalOcean
   - Heroku

4. **WordPress Site**
   - WordPress 6.0+
   - PHP 8.0+
   - HTTPS enabled (required for API calls)

### Local Requirements

- Python 3.11+
- Git
- Text editor
- Terminal/Command line

## Backend Deployment

### Option 1: Railway (Recommended)

Railway offers easy deployment with automatic HTTPS and environment management.

#### Step 1: Prepare Repository

```bash
# Initialize git repository
cd backend
git init
git add .
git commit -m "Initial commit"

# Create .gitignore
cat > .gitignore << EOF
__pycache__/
*.py[cod]
*$py.class
.env
venv/
.pytest_cache/
*.log
EOF
```

#### Step 2: Deploy to Railway

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Initialize project
railway init

# Add environment variables
railway variables set OPENAI_API_KEY=your-openai-api-key-here
railway variables set PINECONE_API_KEY=your-pinecone-api-key-here
railway variables set PINECONE_ENVIRONMENT=us-west1-gcp
railway variables set API_KEY=$(openssl rand -base64 32)

# Deploy
railway up
```

#### Step 3: Get Deployment URL

```bash
# Get your deployment URL
railway domain

# Example output: https://your-app.railway.app
```

### Option 2: Render

#### Step 1: Create render.yaml

```yaml
services:
  - type: web
    name: ibm-docs-llm-api
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: OPENAI_API_KEY
        sync: false
      - key: PINECONE_API_KEY
        sync: false
      - key: PINECONE_ENVIRONMENT
        value: us-west1-gcp
      - key: API_KEY
        generateValue: true
      - key: PYTHON_VERSION
        value: 3.11.0
```

#### Step 2: Deploy

1. Push code to GitHub
2. Go to https://render.com
3. Click "New +" → "Web Service"
4. Connect your repository
5. Configure environment variables
6. Click "Create Web Service"

### Option 3: Docker + Any Platform

#### Step 1: Build Docker Image

```bash
cd backend

# Build image
docker build -t ibm-docs-llm-api .

# Test locally
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=your-key \
  -e PINECONE_API_KEY=your-key \
  -e API_KEY=your-key \
  ibm-docs-llm-api
```

#### Step 2: Deploy to Container Platform

**AWS ECS:**
```bash
# Tag and push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin your-account.dkr.ecr.us-east-1.amazonaws.com
docker tag ibm-docs-llm-api:latest your-account.dkr.ecr.us-east-1.amazonaws.com/ibm-docs-llm-api:latest
docker push your-account.dkr.ecr.us-east-1.amazonaws.com/ibm-docs-llm-api:latest
```

**Google Cloud Run:**
```bash
# Deploy to Cloud Run
gcloud run deploy ibm-docs-llm-api \
  --image gcr.io/your-project/ibm-docs-llm-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Option 4: Traditional VPS (DigitalOcean, Linode, etc.)

#### Step 1: Set Up Server

```bash
# SSH into server
ssh root@your-server-ip

# Update system
apt update && apt upgrade -y

# Install Python 3.11
apt install python3.11 python3.11-venv python3-pip nginx -y

# Create app user
useradd -m -s /bin/bash ibmllm
su - ibmllm
```

#### Step 2: Deploy Application

```bash
# Clone repository
git clone your-repo-url
cd ibm-docs-llm/backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
nano .env  # Edit with your keys
```

#### Step 3: Set Up Systemd Service

```bash
# Create service file (as root)
sudo nano /etc/systemd/system/ibm-docs-llm.service
```

```ini
[Unit]
Description=IBM Docs LLM API
After=network.target

[Service]
Type=simple
User=ibmllm
WorkingDirectory=/home/ibmllm/ibm-docs-llm/backend
Environment="PATH=/home/ibmllm/ibm-docs-llm/backend/venv/bin"
ExecStart=/home/ibmllm/ibm-docs-llm/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable ibm-docs-llm
sudo systemctl start ibm-docs-llm
sudo systemctl status ibm-docs-llm
```

#### Step 4: Configure Nginx

```bash
# Create Nginx config
sudo nano /etc/nginx/sites-available/ibm-docs-llm
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/ibm-docs-llm /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Set up SSL with Let's Encrypt
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

## WordPress Plugin Deployment

### Step 1: Package Plugin

```bash
cd wordpress-plugin
zip -r ibm-docs-llm-v1.0.0.zip ibm-docs-llm/
```

### Step 2: Install in WordPress

**Method 1: WordPress Admin**
1. Go to WordPress Admin → Plugins → Add New
2. Click "Upload Plugin"
3. Choose `ibm-docs-llm-v1.0.0.zip`
4. Click "Install Now"
5. Click "Activate"

**Method 2: FTP/SFTP**
```bash
# Upload via SFTP
sftp user@your-wordpress-site.com
cd wp-content/plugins
put -r ibm-docs-llm
```

Then activate in WordPress Admin → Plugins.

**Method 3: WP-CLI**
```bash
wp plugin install ibm-docs-llm-v1.0.0.zip --activate
```

### Step 3: Configure Plugin

1. Go to Settings → IBM Docs LLM
2. Enter API URL: `https://your-api.railway.app`
3. Enter API Key: (from backend deployment)
4. Configure widget settings
5. Click "Test API Connection"
6. Save settings

### Step 4: Add to Site

**Option A: Floating Widget**
- Enable "Show floating chat widget" in settings

**Option B: Shortcode**
```
[ibm_docs_chat]
```

**Option C: PHP Template**
```php
<?php echo do_shortcode('[ibm_docs_chat]'); ?>
```

## Post-Deployment

### 1. Initialize Pinecone

```bash
# SSH into your backend server or run locally
python scripts/setup_pinecone.py
```

### 2. Ingest Documentation

```bash
# Start with a small section
python scripts/ingest_ibm_docs.py --sections overview --max-pages 20

# Monitor progress
tail -f logs/ingestion.log

# Ingest more sections
python scripts/ingest_ibm_docs.py --sections containers kubernetes vpc --max-pages 50
```

### 3. Test the System

```bash
# Test health endpoint
curl https://your-api.railway.app/api/health

# Test chat endpoint
curl -X POST https://your-api.railway.app/api/chat \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is IBM Cloud?"}'

# Check metrics
curl https://your-api.railway.app/api/metrics/summary \
  -H "Authorization: Bearer YOUR_API_KEY"
```

### 4. Verify WordPress Integration

1. Visit your WordPress site
2. Look for the chat widget (if enabled)
3. Or visit a page with the shortcode
4. Ask a test question
5. Verify response and sources

## Environment Variables Reference

### Required Variables

```env
# OpenAI
OPENAI_API_KEY=sk-...                    # OpenAI API key

# Pinecone
PINECONE_API_KEY=...                     # Pinecone API key
PINECONE_ENVIRONMENT=us-west1-gcp        # Pinecone environment
PINECONE_INDEX_NAME=ibm-docs             # Index name

# API Security
API_KEY=...                              # Secure random key for API auth
```

### Optional Variables

```env
# LLM Settings
LLM_MODEL=gpt-4-turbo-preview           # OpenAI model
LLM_TEMPERATURE=0.7                      # Response creativity
MAX_TOKENS=1000                          # Max response length

# Embedding Settings
EMBEDDING_MODEL=text-embedding-3-small   # Embedding model
EMBEDDING_DIMENSION=1536                 # Vector dimension

# RAG Settings
TOP_K_RESULTS=5                          # Documents to retrieve
CHUNK_SIZE=800                           # Document chunk size
CHUNK_OVERLAP=200                        # Chunk overlap
MIN_RELEVANCE_SCORE=0.7                  # Minimum relevance

# CORS
ALLOWED_ORIGINS=["https://your-site.com"] # Allowed origins

# Logging
LOG_LEVEL=INFO                           # Log level
SENTRY_DSN=                              # Sentry error tracking

# Environment
ENVIRONMENT=production                    # Environment name
```

## Monitoring & Maintenance

### Health Checks

Set up monitoring for:

```bash
# API health
curl https://your-api.railway.app/api/health

# Expected response:
{
  "status": "healthy",
  "version": "1.0.0",
  "services": {
    "openai": "configured",
    "pinecone": "configured"
  }
}
```

### Monitoring Services

**Option 1: UptimeRobot**
1. Sign up at https://uptimerobot.com
2. Add monitor for `/api/health`
3. Set check interval to 5 minutes
4. Configure alerts

**Option 2: Pingdom**
1. Sign up at https://pingdom.com
2. Create uptime check
3. Set up SMS/email alerts

**Option 3: Custom Monitoring**
```bash
# Create monitoring script
cat > monitor.sh << 'EOF'
#!/bin/bash
HEALTH_URL="https://your-api.railway.app/api/health"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" $HEALTH_URL)

if [ $RESPONSE -ne 200 ]; then
    echo "API is down! Status: $RESPONSE"
    # Send alert (email, Slack, etc.)
fi
EOF

# Add to crontab (check every 5 minutes)
crontab -e
*/5 * * * * /path/to/monitor.sh
```

### Log Management

**View Logs:**

Railway:
```bash
railway logs
```

Render:
- View in dashboard

VPS:
```bash
sudo journalctl -u ibm-docs-llm -f
```

**Log Rotation (VPS):**
```bash
# Create logrotate config
sudo nano /etc/logrotate.d/ibm-docs-llm
```

```
/var/log/ibm-docs-llm/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 ibmllm ibmllm
    sharedscripts
    postrotate
        systemctl reload ibm-docs-llm
    endscript
}
```

### Backup Strategy

**1. Database Backup (Pinecone)**
- Pinecone handles backups automatically
- Export vectors periodically for safety:

```python
# Export vectors
python scripts/export_vectors.py --output backup.json
```

**2. Configuration Backup**
```bash
# Backup environment variables
railway variables > env-backup.txt

# Backup WordPress plugin settings
wp option get ibm_docs_llm_settings > wp-settings-backup.json
```

### Updates

**Backend Updates:**
```bash
# Pull latest code
git pull origin main

# Install dependencies
pip install -r requirements.txt

# Restart service
railway restart  # Railway
# or
sudo systemctl restart ibm-docs-llm  # VPS
```

**WordPress Plugin Updates:**
1. Download new version
2. Deactivate old plugin
3. Delete old plugin files
4. Upload new version
5. Activate plugin
6. Verify settings

## Scaling

### Horizontal Scaling

**Railway:**
```bash
# Scale to multiple instances
railway scale --replicas 3
```

**Docker/Kubernetes:**
```yaml
# kubernetes-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ibm-docs-llm-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ibm-docs-llm-api
  template:
    metadata:
      labels:
        app: ibm-docs-llm-api
    spec:
      containers:
      - name: api
        image: your-image:latest
        ports:
        - containerPort: 8000
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-secrets
              key: openai-key
```

### Vertical Scaling

**Increase Resources:**
- Railway: Upgrade plan
- Render: Change instance type
- VPS: Resize droplet

### Caching Layer

Add Redis for caching:

```python
# Install redis
pip install redis

# Add to .env
REDIS_URL=redis://localhost:6379

# Implement caching in services
```

## Troubleshooting

### Common Issues

**1. API Returns 500 Error**
```bash
# Check logs
railway logs  # or journalctl -u ibm-docs-llm

# Common causes:
# - Missing environment variables
# - Invalid API keys
# - Pinecone connection issues
```

**2. WordPress Plugin Can't Connect**
```bash
# Test API from WordPress server
curl https://your-api.railway.app/api/health

# Check CORS settings
# Verify API URL in plugin settings
# Check SSL certificate
```

**3. Slow Response Times**
```bash
# Check metrics
curl https://your-api.railway.app/api/metrics/summary

# Optimize:
# - Reduce TOP_K_RESULTS
# - Add caching
# - Upgrade instance
```

**4. High Costs**
```bash
# Monitor token usage
curl https://your-api.railway.app/api/metrics

# Optimize:
# - Use GPT-3.5 for simple queries
# - Implement aggressive caching
# - Reduce max_tokens
```

## Security Checklist

- [ ] Use HTTPS for all endpoints
- [ ] Rotate API keys regularly
- [ ] Enable rate limiting
- [ ] Set up monitoring alerts
- [ ] Regular security updates
- [ ] Backup configuration
- [ ] Use strong API keys
- [ ] Restrict CORS origins
- [ ] Enable firewall rules
- [ ] Monitor for suspicious activity

## Cost Optimization

### Tips to Reduce Costs

1. **Cache Frequent Queries**
   - Implement Redis caching
   - Cache for 1 hour

2. **Use Cheaper Models**
   - GPT-3.5-turbo for simple queries
   - GPT-4 only for complex questions

3. **Optimize Chunk Size**
   - Larger chunks = fewer embeddings
   - Test 1000-1500 character chunks

4. **Batch Operations**
   - Batch embed documents
   - Reduce API calls

5. **Monitor Usage**
   - Set up cost alerts
   - Review metrics weekly

## Support

For deployment issues:
1. Check logs first
2. Review this documentation
3. Test each component individually
4. Check service status pages
5. Contact support if needed

## Next Steps

After successful deployment:
1. ✅ Monitor system health
2. ✅ Ingest more documentation
3. ✅ Gather user feedback
4. ✅ Optimize performance
5. ✅ Scale as needed

---

**Deployment Complete!** Your IBM Docs LLM system is now live and ready to answer questions.