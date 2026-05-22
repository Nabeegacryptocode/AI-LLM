# Google Cloud Run Deployment Guide

Complete guide for deploying the IBM Docs LLM API to Google Cloud Run.

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Initial Setup](#initial-setup)
4. [Deployment Methods](#deployment-methods)
5. [Configuration](#configuration)
6. [Post-Deployment](#post-deployment)
7. [Monitoring & Logging](#monitoring--logging)
8. [Scaling & Performance](#scaling--performance)
9. [Cost Optimization](#cost-optimization)
10. [Troubleshooting](#troubleshooting)

## Overview

Google Cloud Run is a fully managed serverless platform that automatically scales your containerized applications. Benefits include:

- **Serverless**: No infrastructure management
- **Auto-scaling**: Scales to zero when not in use
- **Pay-per-use**: Only pay for actual usage
- **HTTPS**: Automatic SSL certificates
- **Global**: Deploy to multiple regions
- **Fast**: Cold start times under 1 second

### Architecture

```
User Request → Cloud Run Service → FastAPI App
                     ↓
              ┌──────┴──────┐
              ↓             ↓
         Pinecone      OpenAI API
         (Vectors)     (LLM)
              ↓
         Redis Cloud
         (Cache)
```

## Prerequisites

### Required Accounts

1. **Google Cloud Platform Account**
   - Sign up at https://cloud.google.com
   - Enable billing (free tier available)
   - $300 free credit for new users

2. **OpenAI Account**
   - API key from https://platform.openai.com
   - Billing enabled

3. **Pinecone Account**
   - API key from https://www.pinecone.io
   - Free tier: 100k vectors

4. **Redis Cloud** (Optional but recommended)
   - Free tier at https://redis.com/try-free

### Local Requirements

- Google Cloud SDK (gcloud CLI)
- Docker Desktop
- Git
- Python 3.11+

## Initial Setup

### Step 1: Install Google Cloud SDK

**Windows:**
```powershell
# Download and run installer
# https://cloud.google.com/sdk/docs/install

# Or use Chocolatey
choco install gcloudsdk
```

**macOS:**
```bash
# Using Homebrew
brew install --cask google-cloud-sdk
```

**Linux:**
```bash
# Add Cloud SDK repo
echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list

# Import Google Cloud public key
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key --keyring /usr/share/keyrings/cloud.google.gpg add -

# Install
sudo apt-get update && sudo apt-get install google-cloud-sdk
```

### Step 2: Initialize gcloud

```bash
# Initialize gcloud
gcloud init

# Login to your Google account
gcloud auth login

# Set your project (or create new one)
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

### Step 3: Create Google Cloud Project

```bash
# Create new project
gcloud projects create ibm-docs-llm --name="IBM Docs LLM"

# Set as active project
gcloud config set project ibm-docs-llm

# Link billing account (required for Cloud Run)
gcloud billing accounts list
gcloud billing projects link ibm-docs-llm --billing-account=BILLING_ACCOUNT_ID
```

### Step 4: Configure Docker for Google Cloud

```bash
# Configure Docker to use gcloud as credential helper
gcloud auth configure-docker

# Or for Artifact Registry (recommended)
gcloud auth configure-docker us-central1-docker.pkg.dev
```

## Deployment Methods

### Method 1: Direct Deployment (Recommended for Quick Start)

This method builds and deploys directly from source code.

```bash
# Navigate to backend directory
cd backend

# Deploy to Cloud Run
gcloud run deploy ibm-docs-llm-api \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --max-instances 10 \
  --min-instances 0 \
  --port 8000 \
  --set-env-vars "ENVIRONMENT=production"

# Follow prompts to set environment variables
```

### Method 2: Container Registry Deployment

Build Docker image locally and push to Google Container Registry.

```bash
# Navigate to backend directory
cd backend

# Set variables
PROJECT_ID=$(gcloud config get-value project)
IMAGE_NAME="ibm-docs-llm-api"
IMAGE_TAG="latest"

# Build Docker image
docker build -t gcr.io/${PROJECT_ID}/${IMAGE_NAME}:${IMAGE_TAG} .

# Push to Container Registry
docker push gcr.io/${PROJECT_ID}/${IMAGE_NAME}:${IMAGE_TAG}

# Deploy to Cloud Run
gcloud run deploy ibm-docs-llm-api \
  --image gcr.io/${PROJECT_ID}/${IMAGE_NAME}:${IMAGE_TAG} \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --max-instances 10 \
  --min-instances 0 \
  --port 8000
```

### Method 3: Artifact Registry Deployment (Recommended for Production)

Use Artifact Registry for better security and features.

```bash
# Create Artifact Registry repository
gcloud artifacts repositories create ibm-docs-llm \
  --repository-format=docker \
  --location=us-central1 \
  --description="IBM Docs LLM API container images"

# Set variables
PROJECT_ID=$(gcloud config get-value project)
REGION="us-central1"
REPO_NAME="ibm-docs-llm"
IMAGE_NAME="api"
IMAGE_TAG="v1.0.0"

# Build and tag image
docker build -t ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/${IMAGE_NAME}:${IMAGE_TAG} .

# Push to Artifact Registry
docker push ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/${IMAGE_NAME}:${IMAGE_TAG}

# Deploy to Cloud Run
gcloud run deploy ibm-docs-llm-api \
  --image ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/${IMAGE_NAME}:${IMAGE_TAG} \
  --platform managed \
  --region ${REGION} \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --max-instances 10 \
  --min-instances 0 \
  --port 8000
```

### Method 4: Cloud Build Deployment (CI/CD)

Automate deployments with Cloud Build.

**Create `cloudbuild.yaml`:**

```yaml
steps:
  # Build the container image
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/ibm-docs-llm-api:$COMMIT_SHA', '.']
    dir: 'backend'
  
  # Push the container image to Container Registry
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/ibm-docs-llm-api:$COMMIT_SHA']
  
  # Deploy to Cloud Run
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
      - 'run'
      - 'deploy'
      - 'ibm-docs-llm-api'
      - '--image'
      - 'gcr.io/$PROJECT_ID/ibm-docs-llm-api:$COMMIT_SHA'
      - '--region'
      - 'us-central1'
      - '--platform'
      - 'managed'
      - '--allow-unauthenticated'
      - '--memory'
      - '2Gi'
      - '--cpu'
      - '2'

images:
  - 'gcr.io/$PROJECT_ID/ibm-docs-llm-api:$COMMIT_SHA'

options:
  logging: CLOUD_LOGGING_ONLY
```

**Deploy using Cloud Build:**

```bash
# Submit build
gcloud builds submit --config cloudbuild.yaml

# Or trigger from GitHub
gcloud builds triggers create github \
  --repo-name=ibm-docs-llm \
  --repo-owner=YOUR_GITHUB_USERNAME \
  --branch-pattern="^main$" \
  --build-config=cloudbuild.yaml
```

## Configuration

### Environment Variables

Set environment variables using Secret Manager (recommended) or directly.

#### Option 1: Using Secret Manager (Recommended)

```bash
# Enable Secret Manager API
gcloud services enable secretmanager.googleapis.com

# Create secrets
echo -n "your-openai-api-key" | gcloud secrets create openai-api-key --data-file=-
echo -n "your-pinecone-api-key" | gcloud secrets create pinecone-api-key --data-file=-
echo -n "your-api-key" | gcloud secrets create api-key --data-file=-

# Grant Cloud Run access to secrets
PROJECT_NUMBER=$(gcloud projects describe $(gcloud config get-value project) --format="value(projectNumber)")
gcloud secrets add-iam-policy-binding openai-api-key \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding pinecone-api-key \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding api-key \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

# Deploy with secrets
gcloud run deploy ibm-docs-llm-api \
  --image gcr.io/${PROJECT_ID}/ibm-docs-llm-api:latest \
  --region us-central1 \
  --set-secrets="OPENAI_API_KEY=openai-api-key:latest,PINECONE_API_KEY=pinecone-api-key:latest,API_KEY=api-key:latest" \
  --set-env-vars="PINECONE_ENVIRONMENT=us-west1-gcp,PINECONE_INDEX_NAME=ibm-docs,ENVIRONMENT=production"
```

#### Option 2: Direct Environment Variables

```bash
# Deploy with environment variables
gcloud run deploy ibm-docs-llm-api \
  --image gcr.io/${PROJECT_ID}/ibm-docs-llm-api:latest \
  --region us-central1 \
  --set-env-vars="OPENAI_API_KEY=sk-...,PINECONE_API_KEY=...,API_KEY=...,PINECONE_ENVIRONMENT=us-west1-gcp,PINECONE_INDEX_NAME=ibm-docs,ENVIRONMENT=production,LLM_MODEL=gpt-4o-mini,LLM_TEMPERATURE=0.7,MAX_TOKENS=1000,TOP_K_RESULTS=5"
```

#### Option 3: Using .env.yaml File

Create `env.yaml`:

```yaml
OPENAI_API_KEY: "sk-..."
PINECONE_API_KEY: "..."
API_KEY: "..."
PINECONE_ENVIRONMENT: "us-west1-gcp"
PINECONE_INDEX_NAME: "ibm-docs"
ENVIRONMENT: "production"
LLM_MODEL: "gpt-4o-mini"
LLM_TEMPERATURE: "0.7"
MAX_TOKENS: "1000"
EMBEDDING_MODEL: "text-embedding-3-small"
EMBEDDING_DIMENSION: "1536"
TOP_K_RESULTS: "5"
CHUNK_SIZE: "800"
CHUNK_OVERLAP: "200"
MIN_RELEVANCE_SCORE: "0.3"
LOG_LEVEL: "INFO"
REDIS_ENABLED: "true"
REDIS_URL: "redis://..."
CACHE_TTL: "3600"
WEB_SEARCH_ENABLED: "true"
USE_DISCOVERY_ENGINE: "true"
GOOGLE_PROJECT_ID: "ibm-docs-llm"
GOOGLE_DISCOVERY_ENGINE_ID: "..."
```

Deploy with env file:

```bash
gcloud run deploy ibm-docs-llm-api \
  --image gcr.io/${PROJECT_ID}/ibm-docs-llm-api:latest \
  --region us-central1 \
  --env-vars-file env.yaml
```

### Custom Domain

Map a custom domain to your Cloud Run service.

```bash
# Add domain mapping
gcloud run domain-mappings create \
  --service ibm-docs-llm-api \
  --domain api.yourdomain.com \
  --region us-central1

# Follow instructions to update DNS records
# Add CNAME record: api.yourdomain.com → ghs.googlehosted.com
```

### Service Account (Optional)

Create a dedicated service account for better security.

```bash
# Create service account
gcloud iam service-accounts create ibm-docs-llm-sa \
  --display-name="IBM Docs LLM Service Account"

# Grant necessary permissions
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member="serviceAccount:ibm-docs-llm-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

# Deploy with service account
gcloud run deploy ibm-docs-llm-api \
  --image gcr.io/${PROJECT_ID}/ibm-docs-llm-api:latest \
  --region us-central1 \
  --service-account=ibm-docs-llm-sa@${PROJECT_ID}.iam.gserviceaccount.com
```

## Post-Deployment

### Get Service URL

```bash
# Get the service URL
gcloud run services describe ibm-docs-llm-api \
  --region us-central1 \
  --format="value(status.url)"

# Example output: https://ibm-docs-llm-api-abc123-uc.a.run.app
```

### Test Deployment

```bash
# Set service URL
SERVICE_URL=$(gcloud run services describe ibm-docs-llm-api --region us-central1 --format="value(status.url)")

# Test health endpoint
curl ${SERVICE_URL}/api/health

# Test chat endpoint
curl -X POST ${SERVICE_URL}/api/chat \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is IBM Cloud?",
    "conversation_id": "test-123"
  }'

# Test metrics
curl ${SERVICE_URL}/api/metrics/summary \
  -H "Authorization: Bearer YOUR_API_KEY"
```

### Initialize Vector Database

```bash
# Run setup script locally (pointing to production)
export PINECONE_API_KEY="your-key"
export PINECONE_ENVIRONMENT="us-west1-gcp"
python scripts/setup_pinecone.py

# Or use Cloud Run Jobs (if available)
gcloud run jobs create setup-pinecone \
  --image gcr.io/${PROJECT_ID}/ibm-docs-llm-api:latest \
  --region us-central1 \
  --command="python" \
  --args="scripts/setup_pinecone.py" \
  --set-env-vars="PINECONE_API_KEY=...,PINECONE_ENVIRONMENT=us-west1-gcp"

gcloud run jobs execute setup-pinecone --region us-central1
```

### Ingest Documentation

```bash
# Ingest sample data
python scripts/ingest_sample_data.py --api-url ${SERVICE_URL} --api-key YOUR_API_KEY

# Ingest IBM documentation
python scripts/ingest_ibm_docs.py --api-url ${SERVICE_URL} --api-key YOUR_API_KEY --max-pages 100
```

## Monitoring & Logging

### View Logs

```bash
# View recent logs
gcloud run services logs read ibm-docs-llm-api \
  --region us-central1 \
  --limit 50

# Stream logs in real-time
gcloud run services logs tail ibm-docs-llm-api \
  --region us-central1

# Filter logs
gcloud run services logs read ibm-docs-llm-api \
  --region us-central1 \
  --filter="severity>=ERROR"
```

### Cloud Monitoring

Access metrics in Google Cloud Console:

1. Go to Cloud Run → Select your service
2. Click "Metrics" tab
3. View:
   - Request count
   - Request latency
   - Container CPU utilization
   - Container memory utilization
   - Billable container time

### Set Up Alerts

```bash
# Create alert policy for high error rate
gcloud alpha monitoring policies create \
  --notification-channels=CHANNEL_ID \
  --display-name="High Error Rate" \
  --condition-display-name="Error rate > 5%" \
  --condition-threshold-value=0.05 \
  --condition-threshold-duration=300s
```

### Cloud Trace

Enable request tracing:

```bash
# Deploy with Cloud Trace enabled
gcloud run deploy ibm-docs-llm-api \
  --image gcr.io/${PROJECT_ID}/ibm-docs-llm-api:latest \
  --region us-central1 \
  --set-env-vars="GOOGLE_CLOUD_PROJECT=${PROJECT_ID}"
```

## Scaling & Performance

### Configure Autoscaling

```bash
# Update service with scaling configuration
gcloud run services update ibm-docs-llm-api \
  --region us-central1 \
  --min-instances 1 \
  --max-instances 100 \
  --concurrency 80 \
  --cpu-throttling \
  --no-cpu-boost
```

### Scaling Parameters

- **min-instances**: Minimum number of instances (0 for scale-to-zero)
- **max-instances**: Maximum number of instances
- **concurrency**: Max concurrent requests per instance (default: 80)
- **cpu-throttling**: Throttle CPU when not processing requests
- **cpu-boost**: Allocate extra CPU during startup

### Performance Optimization

**1. Enable CPU Boost for Faster Cold Starts:**

```bash
gcloud run services update ibm-docs-llm-api \
  --region us-central1 \
  --cpu-boost
```

**2. Keep Minimum Instances Warm:**

```bash
# Keep 1 instance always running
gcloud run services update ibm-docs-llm-api \
  --region us-central1 \
  --min-instances 1
```

**3. Increase Resources:**

```bash
gcloud run services update ibm-docs-llm-api \
  --region us-central1 \
  --memory 4Gi \
  --cpu 4
```

**4. Optimize Docker Image:**

```dockerfile
# Use multi-stage build
FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Multi-Region Deployment

Deploy to multiple regions for better global performance:

```bash
# Deploy to multiple regions
REGIONS=("us-central1" "europe-west1" "asia-northeast1")

for REGION in "${REGIONS[@]}"; do
  gcloud run deploy ibm-docs-llm-api-${REGION} \
    --image gcr.io/${PROJECT_ID}/ibm-docs-llm-api:latest \
    --region ${REGION} \
    --platform managed \
    --allow-unauthenticated
done

# Set up global load balancer
gcloud compute backend-services create ibm-docs-llm-backend \
  --global \
  --load-balancing-scheme=EXTERNAL_MANAGED
```

## Cost Optimization

### Pricing Overview

Cloud Run pricing (as of 2024):
- **CPU**: $0.00002400 per vCPU-second
- **Memory**: $0.00000250 per GiB-second
- **Requests**: $0.40 per million requests
- **Free tier**: 2 million requests/month, 360,000 GiB-seconds, 180,000 vCPU-seconds

### Cost Optimization Tips

**1. Scale to Zero When Idle:**

```bash
gcloud run services update ibm-docs-llm-api \
  --region us-central1 \
  --min-instances 0
```

**2. Right-Size Resources:**

```bash
# Start with smaller resources
gcloud run services update ibm-docs-llm-api \
  --region us-central1 \
  --memory 1Gi \
  --cpu 1
```

**3. Enable CPU Throttling:**

```bash
gcloud run services update ibm-docs-llm-api \
  --region us-central1 \
  --cpu-throttling
```

**4. Use Caching:**

Enable Redis caching to reduce OpenAI API calls and improve response times.

**5. Monitor Costs:**

```bash
# View cost breakdown
gcloud billing accounts list
gcloud billing projects describe ${PROJECT_ID}

# Set up budget alerts in Cloud Console
```

### Estimated Monthly Costs

**Low Traffic (1,000 requests/day):**
- Cloud Run: ~$5/month
- OpenAI API: ~$10-20/month
- Pinecone: Free tier
- **Total: ~$15-25/month**

**Medium Traffic (10,000 requests/day):**
- Cloud Run: ~$30/month
- OpenAI API: ~$100-200/month
- Pinecone: Free tier or ~$70/month
- **Total: ~$130-300/month**

**High Traffic (100,000 requests/day):**
- Cloud Run: ~$200/month
- OpenAI API: ~$1,000-2,000/month
- Pinecone: ~$70-200/month
- **Total: ~$1,270-2,400/month**

## Troubleshooting

### Common Issues

**1. Deployment Fails**

```bash
# Check build logs
gcloud builds list --limit 5
gcloud builds log BUILD_ID

# Check service status
gcloud run services describe ibm-docs-llm-api --region us-central1

# Common fixes:
# - Verify Dockerfile syntax
# - Check requirements.txt
# - Ensure port 8000 is exposed
# - Verify environment variables
```

**2. Service Returns 500 Errors**

```bash
# Check logs
gcloud run services logs read ibm-docs-llm-api \
  --region us-central1 \
  --filter="severity>=ERROR" \
  --limit 50

# Common causes:
# - Missing environment variables
# - Invalid API keys
# - Pinecone connection issues
# - OpenAI API rate limits
```

**3. Cold Start Latency**

```bash
# Enable minimum instances
gcloud run services update ibm-docs-llm-api \
  --region us-central1 \
  --min-instances 1

# Enable CPU boost
gcloud run services update ibm-docs-llm-api \
  --region us-central1 \
  --cpu-boost
```

**4. Memory Issues**

```bash
# Increase memory
gcloud run services update ibm-docs-llm-api \
  --region us-central1 \
  --memory 4Gi

# Check memory usage in logs
gcloud run services logs read ibm-docs-llm-api \
  --region us-central1 \
  --filter="memory"
```

**5. Timeout Issues**

```bash
# Increase timeout (max 3600s)
gcloud run services update ibm-docs-llm-api \
  --region us-central1 \
  --timeout 600
```

### Debug Mode

Enable debug logging:

```bash
gcloud run services update ibm-docs-llm-api \
  --region us-central1 \
  --set-env-vars="LOG_LEVEL=DEBUG"
```

### Health Check

```bash
# Test health endpoint
SERVICE_URL=$(gcloud run services describe ibm-docs-llm-api --region us-central1 --format="value(status.url)")
curl ${SERVICE_URL}/api/health

# Expected response:
# {
#   "status": "healthy",
#   "version": "1.0.0",
#   "services": {
#     "openai": "configured",
#     "pinecone": "configured"
#   }
# }
```

## Advanced Configuration

### VPC Connector (Private Networking)

Connect to private resources:

```bash
# Create VPC connector
gcloud compute networks vpc-access connectors create ibm-docs-connector \
  --region us-central1 \
  --network default \
  --range 10.8.0.0/28

# Deploy with VPC connector
gcloud run deploy ibm-docs-llm-api \
  --image gcr.io/${PROJECT_ID}/ibm-docs-llm-api:latest \
  --region us-central1 \
  --vpc-connector ibm-docs-connector \
  --vpc-egress all-traffic
```

### Cloud SQL Integration

Connect to Cloud SQL database:

```bash
# Create Cloud SQL instance
gcloud sql instances create ibm-docs-db \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=us-central1

# Deploy with Cloud SQL connection
gcloud run deploy ibm-docs-llm-api \
  --image gcr.io/${PROJECT_ID}/ibm-docs-llm-api:latest \
  --region us-central1 \
  --add-cloudsql-instances=${PROJECT_ID}:us-central1:ibm-docs-db \
  --set-env-vars="DATABASE_URL=postgresql://user:pass@/dbname?host=/cloudsql/${PROJECT_ID}:us-central1:ibm-docs-db"
```

### CI/CD with GitHub Actions

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Cloud Run

on:
  push:
    branches:
      - main

env:
  PROJECT_ID: ibm-docs-llm
  SERVICE_NAME: ibm-docs-llm-api
  REGION: us-central1

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v3
    
    - name: Setup Cloud SDK
      uses: google-github-actions/setup-gcloud@v1
      with:
        service_account_key: ${{ secrets.GCP_SA_KEY }}
        project_id: ${{ env.PROJECT_ID }}
    
    - name: Configure Docker
      run: gcloud auth configure-docker
    
    - name: Build and Push
      run: |
        docker build -t gcr.io/$PROJECT_ID/$SERVICE_NAME:$GITHUB_SHA ./backend
        docker push gcr.io/$PROJECT_ID/$SERVICE_NAME:$GITHUB_SHA
    
    - name: Deploy to Cloud Run
      run: |
        gcloud run deploy $SERVICE_NAME \
          --image gcr.io/$PROJECT_ID/$SERVICE_NAME:$GITHUB_SHA \
          --region $REGION \
          --platform managed \
          --allow-unauthenticated
```

## Security Best Practices

1. **Use Secret Manager** for sensitive data
2. **Enable Cloud Armor** for DDoS protection
3. **Implement rate limiting** in application
4. **Use service accounts** with minimal permissions
5. **Enable Cloud Audit Logs**
6. **Regular security updates** of dependencies
7. **Use HTTPS only** (automatic with Cloud Run)
8. **Implement authentication** for sensitive endpoints

## Maintenance

### Update Service

```bash
# Build new image
docker build -t gcr.io/${PROJECT_ID}/ibm-docs-llm-api:v2.0.0 ./backend
docker push gcr.io/${PROJECT_ID}/ibm-docs-llm-api:v2.0.0

# Deploy new version
gcloud run deploy ibm-docs-llm-api \
  --image gcr.io/${PROJECT_ID}/ibm-docs-llm-api:v2.0.0 \
  --region us-central1

# Rollback if needed
gcloud run services update-traffic ibm-docs-llm-api \
  --region us-central1 \
  --to-revisions=PREVIOUS_REVISION=100
```

### Backup Configuration

```bash
# Export service configuration
gcloud run services describe ibm-docs-llm-api \
  --region us-central1 \
  --format yaml > service-backup.yaml

# Export environment variables
gcloud run services describe ibm-docs-llm-api \
  --region us-central1 \
  --format="value(spec.template.spec.containers[0].env)" > env-backup.txt
```

## Support & Resources

- **Cloud Run Documentation**: https://cloud.google.com/run/docs
- **Pricing Calculator**: https://cloud.google.com/products/calculator
- **Status Dashboard**: https://status.cloud.google.com
- **Support**: https://cloud.google.com/support

## Quick Reference

### Essential Commands

```bash
# Deploy
gcloud run deploy SERVICE_NAME --source .

# View logs
gcloud run services logs tail SERVICE_NAME

# Update environment variables
gcloud run services update SERVICE_NAME --set-env-vars KEY=VALUE

# Scale
gcloud run services update SERVICE_NAME --min-instances 1 --max-instances 10

# Get URL
gcloud run services describe SERVICE_NAME --format="value(status.url)"

# Delete service
gcloud run services delete SERVICE_NAME
```

---

**Deployment Complete!** Your IBM Docs LLM API is now running on Google Cloud Run with automatic scaling, monitoring, and global availability.