# Troubleshooting Guide - IBM Docs LLM

Common issues and solutions for the IBM Documentation LLM system.

## Table of Contents

1. [Installation Issues](#installation-issues)
2. [Runtime Errors](#runtime-errors)
3. [API Issues](#api-issues)
4. [Database Issues](#database-issues)
5. [WordPress Plugin Issues](#wordpress-plugin-issues)
6. [Performance Issues](#performance-issues)

## Installation Issues

### Error: "No module named 'fastapi'"

**Problem**: Dependencies not installed

**Solution**:
```bash
# Install dependencies
cd backend
pip install -r requirements.txt

# Or use the setup script
python scripts/setup_environment.py
```

### Error: "No module named 'uvicorn'"

**Problem**: Web server not installed

**Solution**:
```bash
pip install uvicorn[standard]
```

### Error: "pip: command not found"

**Problem**: pip not in PATH or Python not installed correctly

**Solution**:
```bash
# Windows
python -m pip install --upgrade pip

# Linux/Mac
python3 -m pip install --upgrade pip
```

### Error: "Permission denied" during installation

**Problem**: Insufficient permissions

**Solution**:
```bash
# Use --user flag
pip install --user -r requirements.txt

# Or use virtual environment (recommended)
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
pip install -r requirements.txt
```

## Runtime Errors

### Error: "ModuleNotFoundError: No module named 'app'"

**Problem**: Running from wrong directory or PYTHONPATH not set

**Solution**:
```bash
# Make sure you're in the backend directory
cd backend

# Run with proper module path
python -m uvicorn app.main:app --reload

# Or set PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"  # Linux/Mac
$env:PYTHONPATH="$env:PYTHONPATH;$(pwd)"  # Windows PowerShell
```

### Error: "pydantic.error_wrappers.ValidationError"

**Problem**: Missing or invalid environment variables

**Solution**:
```bash
# Copy example env file
cp .env.example .env

# Edit .env and add required values:
# - OPENAI_API_KEY
# - PINECONE_API_KEY
# - PINECONE_ENVIRONMENT
# - API_KEY
```

### Error: "openai.error.AuthenticationError"

**Problem**: Invalid OpenAI API key

**Solution**:
1. Check your OpenAI API key at https://platform.openai.com/api-keys
2. Update `.env` file with correct key
3. Ensure no extra spaces or quotes around the key
4. Restart the application

### Error: "pinecone.core.client.exceptions.UnauthorizedException"

**Problem**: Invalid Pinecone credentials

**Solution**:
1. Check your Pinecone API key at https://app.pinecone.io
2. Verify the environment name (e.g., "us-west1-gcp")
3. Update `.env` file
4. Restart the application

### Error: "Index 'ibm-docs' not found"

**Problem**: Pinecone index not created

**Solution**:
```bash
# Create the index
python scripts/setup_pinecone.py

# Verify it was created
python scripts/test_vector_db.py
```

## API Issues

### Error: 401 Unauthorized

**Problem**: Missing or invalid API key

**Solution**:
```bash
# Check your API_KEY in .env
# Make sure to include it in requests:
curl -H "Authorization: Bearer YOUR_API_KEY" http://localhost:8000/api/health
```

### Error: 422 Unprocessable Entity

**Problem**: Invalid request body

**Solution**:
```bash
# Ensure request has required fields
# For chat endpoint:
{
  "question": "Your question here"  # Required
}

# Check API documentation for required fields
```

### Error: 500 Internal Server Error

**Problem**: Server-side error

**Solution**:
1. Check server logs for detailed error
2. Verify all environment variables are set
3. Check OpenAI/Pinecone service status
4. Review recent code changes

### Error: CORS Error in Browser

**Problem**: CORS not configured for your domain

**Solution**:
```python
# In backend/app/main.py, update CORS origins:
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-wordpress-site.com"],  # Add your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Database Issues

### Error: "Connection timeout" to Pinecone

**Problem**: Network issues or wrong environment

**Solution**:
1. Check internet connection
2. Verify PINECONE_ENVIRONMENT in .env
3. Check Pinecone service status
4. Try different network (VPN might block)

### Error: "Quota exceeded"

**Problem**: Pinecone free tier limit reached

**Solution**:
1. Check your Pinecone dashboard for usage
2. Delete old vectors: `python scripts/cleanup_vectors.py`
3. Upgrade to paid plan if needed

### Error: "Vector dimension mismatch"

**Problem**: Embedding dimension doesn't match index

**Solution**:
```bash
# Delete and recreate index
python scripts/setup_pinecone.py --recreate

# Or update EMBEDDING_DIMENSION in .env to match index
```

## WordPress Plugin Issues

### Plugin Not Appearing

**Problem**: Plugin not activated or files not uploaded correctly

**Solution**:
1. Check wp-content/plugins/ibm-docs-llm/ exists
2. Activate in WordPress Admin → Plugins
3. Check file permissions (755 for directories, 644 for files)

### Chat Widget Not Showing

**Problem**: Widget not enabled or JavaScript error

**Solution**:
1. Go to Settings → IBM Docs LLM
2. Enable "Show floating chat widget"
3. Check browser console for JavaScript errors
4. Clear browser cache

### API Connection Failed

**Problem**: Wrong API URL or CORS issue

**Solution**:
1. Verify API URL in plugin settings
2. Test API: `curl https://your-api-url/api/health`
3. Check CORS configuration in backend
4. Ensure HTTPS is used (not HTTP)

### Error: "Failed to load resource"

**Problem**: JavaScript/CSS files not loading

**Solution**:
1. Check file paths in plugin
2. Clear WordPress cache
3. Regenerate permalinks (Settings → Permalinks → Save)
4. Check .htaccess file

## Performance Issues

### Slow Response Times

**Problem**: Various causes

**Solutions**:
```bash
# 1. Check metrics
curl -H "Authorization: Bearer YOUR_KEY" \
  http://localhost:8000/api/metrics/summary

# 2. Reduce TOP_K_RESULTS in .env
TOP_K_RESULTS=3

# 3. Use faster model
LLM_MODEL=gpt-3.5-turbo

# 4. Enable caching (if implemented)

# 5. Scale horizontally (add more instances)
```

### High Memory Usage

**Problem**: Large document processing or memory leaks

**Solutions**:
1. Process documents in smaller batches
2. Reduce CHUNK_SIZE in .env
3. Restart application periodically
4. Monitor with: `python scripts/monitor_resources.py`

### Rate Limiting Errors

**Problem**: Too many requests

**Solutions**:
1. Implement request queuing
2. Add caching layer
3. Upgrade OpenAI tier
4. Distribute load across multiple API keys

## Common Setup Issues

### Issue: Application won't start

**Checklist**:
- [ ] All dependencies installed (`pip list`)
- [ ] .env file exists and configured
- [ ] Python 3.11+ installed (`python --version`)
- [ ] No port conflicts (8000 not in use)
- [ ] Virtual environment activated (if using)

### Issue: Tests failing

**Checklist**:
- [ ] Test dependencies installed (`pip install -r requirements-test.txt`)
- [ ] pytest installed (`pytest --version`)
- [ ] Running from correct directory
- [ ] Environment variables set for tests

### Issue: Can't connect to services

**Checklist**:
- [ ] Internet connection working
- [ ] API keys valid and not expired
- [ ] Service status pages checked
- [ ] Firewall not blocking connections
- [ ] VPN not interfering

## Debug Mode

Enable debug logging:

```python
# In backend/app/config.py
LOG_LEVEL = "DEBUG"
```

Or set environment variable:
```bash
export LOG_LEVEL=DEBUG  # Linux/Mac
$env:LOG_LEVEL="DEBUG"  # Windows PowerShell
```

## Getting Help

### Check Logs

```bash
# Application logs
tail -f logs/app.log

# Uvicorn logs
uvicorn app.main:app --log-level debug

# System logs (Linux)
journalctl -u ibm-docs-llm -f
```

### Collect Debug Information

```bash
# System info
python --version
pip list
env | grep -E "(OPENAI|PINECONE|API_KEY)"

# Test connectivity
curl https://api.openai.com/v1/models
curl https://controller.us-west1-gcp.pinecone.io/databases

# Check application
curl http://localhost:8000/api/health
```

### Report Issues

When reporting issues, include:
1. Error message (full traceback)
2. Steps to reproduce
3. Environment details (OS, Python version)
4. Configuration (sanitized .env)
5. Logs (relevant portions)

## Quick Fixes

### Reset Everything

```bash
# Stop application
# Delete virtual environment
rm -rf venv

# Recreate environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Reinstall dependencies
pip install -r requirements.txt

# Reconfigure
cp .env.example .env
# Edit .env with your keys

# Recreate database
python scripts/setup_pinecone.py --recreate

# Restart application
uvicorn app.main:app --reload
```

### Clear Cache

```bash
# Python cache
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type f -name "*.pyc" -delete

# Logs
rm -rf logs/*.log

# Restart
```

## Prevention

### Best Practices

1. **Use Virtual Environments**: Always use venv or conda
2. **Version Control**: Keep .env.example updated
3. **Monitor Logs**: Regular log review
4. **Test Changes**: Run tests before deploying
5. **Backup Configuration**: Keep .env backed up securely
6. **Update Dependencies**: Regular security updates
7. **Monitor Metrics**: Track performance over time

### Health Checks

Set up automated health checks:

```bash
# Cron job (Linux)
*/5 * * * * curl -f http://localhost:8000/api/health || systemctl restart ibm-docs-llm

# Windows Task Scheduler
# Create task to run health check script every 5 minutes
```

---

**Still having issues?** Check the main documentation or create an issue with detailed information.