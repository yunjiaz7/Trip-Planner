# Deployment Guide

## Overview

This guide covers the deployment process for the Trip Planner system after migration to LangChain framework. The system is now fully in English and ready for English-speaking users.

## Prerequisites

### System Requirements
- Python 3.10+ (required for Pydantic 2.x)
- Node.js 18+ (for frontend)
- `uv` tool installed (for MCP server)
- API keys configured:
  - LLM API Key (OpenAI, DeepSeek, or compatible)
  - Amap API Key (for map services)

### Environment Variables

Create a `.env` file in the `backend` directory:

```env
# LLM Configuration
LLM_API_KEY=your_llm_api_key_here
LLM_BASE_URL=https://api.openai.com/v1  # or your LLM provider URL
LLM_MODEL_ID=gpt-4  # or your model name

# Amap Configuration
AMAP_MAPS_API_KEY=your_amap_api_key_here

# Server Configuration
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO
```

## Step 1: Backend Setup

### 1.1 Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 1.2 Verify Installation

Run the test suite to verify everything is working:

```bash
# Test LLM service
python test_llm_service.py

# Test MCP tools
python test_mcp_tool.py

# Test all agents
python test_all_agents.py

# End-to-end test
python test_e2e.py
```

### 1.3 Install `uv` Tool (Required for MCP Server)

If not already installed:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Reload your shell:
```bash
source ~/.zshrc  # or ~/.bashrc
```

Verify installation:
```bash
uvx --version
```

## Step 2: Frontend Setup

### 2.1 Install Dependencies

```bash
cd frontend
npm install
```

### 2.2 Configure API Base URL

Create a `.env` file in the `frontend` directory:

```env
VITE_API_BASE_URL=http://localhost:8000
```

For production, update this to your backend URL:
```env
VITE_API_BASE_URL=https://api.yourdomain.com
```

### 2.3 Build Frontend

```bash
npm run build
```

The built files will be in `frontend/dist/`.

## Step 3: Running the System

### 3.1 Development Mode

**Backend:**
```bash
cd backend
python run.py
```

Or using uvicorn directly:
```bash
cd backend
uvicorn app.api.main:app --host 0.0.0.0 --port 8000 --reload
```

**Frontend:**
```bash
cd frontend
npm run dev
```

### 3.2 Production Mode

**Backend (using Gunicorn):**

```bash
cd backend
gunicorn app.api.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

**Frontend:**

Serve the built files using a web server (nginx, Apache, etc.) or a static file server.

## Step 4: Deployment Options

### Option 1: Docker Deployment

Create a `Dockerfile` for the backend:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t trip-planner-backend .
docker run -p 8000:8000 --env-file .env trip-planner-backend
```

### Option 2: Cloud Platform Deployment

#### Heroku

1. Create `Procfile`:
```
web: uvicorn app.api.main:app --host 0.0.0.0 --port $PORT
```

2. Deploy:
```bash
heroku create trip-planner
heroku config:set LLM_API_KEY=your_key
heroku config:set AMAP_MAPS_API_KEY=your_key
git push heroku main
```

#### AWS/GCP/Azure

Follow standard Python web application deployment procedures:
- Use a WSGI/ASGI server (Gunicorn with Uvicorn workers)
- Configure environment variables
- Set up reverse proxy (nginx/Apache)
- Configure SSL certificates

## Step 5: Verification

### 5.1 Health Check

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "trip-planner",
  "version": "1.0.0"
}
```

### 5.2 API Documentation

Access the interactive API documentation:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### 5.3 Test Trip Planning

```bash
curl -X POST "http://localhost:8000/api/trip/plan" \
  -H "Content-Type: application/json" \
  -d '{
    "city": "Beijing",
    "start_date": "2025-02-01",
    "end_date": "2025-02-03",
    "travel_days": 2,
    "preferences": ["historical culture"],
    "transportation": "taxi",
    "accommodation": "hotel",
    "budget": 5000
  }'
```

## Step 6: Monitoring and Logging

### 6.1 Application Logs

The application logs to stdout. For production, configure log aggregation:
- Use a logging service (Datadog, Loggly, etc.)
- Or configure log rotation with logrotate
- Or use container logging (Docker logs, Kubernetes logs)

### 6.2 Error Monitoring

Consider integrating error monitoring:
- Sentry
- Rollbar
- AWS CloudWatch

### 6.3 Performance Monitoring

Monitor:
- API response times
- LLM API call latency
- MCP tool call success rate
- Memory usage
- CPU usage

## Step 7: Security Considerations

### 7.1 API Keys

- Never commit API keys to version control
- Use environment variables or secret management services
- Rotate keys regularly
- Use different keys for development and production

### 7.2 CORS Configuration

Update CORS settings in `backend/app/config.py` for production:
```python
CORS_ORIGINS="https://yourdomain.com,https://www.yourdomain.com"
```

### 7.3 Rate Limiting

Consider adding rate limiting for production:
- Use FastAPI middleware
- Or use a reverse proxy (nginx) rate limiting

## Troubleshooting

### Issue: MCP Server Not Starting

**Symptom:** `uvx: command not found`

**Solution:**
1. Install `uv` tool (see Step 1.3)
2. Verify installation: `uvx --version`
3. Check PATH environment variable

### Issue: LLM API Errors

**Symptom:** `LLM API Key not configured`

**Solution:**
1. Check `.env` file exists
2. Verify environment variables are set
3. Check API key is valid
4. Verify base URL is correct

### Issue: Agent Timeout

**Symptom:** Agent execution takes too long

**Solution:**
1. Check LLM API response time
2. Increase timeout in `llm_service.py`
3. Check MCP server performance
4. Consider reducing `max_iterations` in agent executor

### Issue: Frontend Cannot Connect to Backend

**Symptom:** CORS errors or connection refused

**Solution:**
1. Check `VITE_API_BASE_URL` in frontend `.env`
2. Verify backend is running
3. Check CORS configuration
4. Check firewall/network settings

## Migration Checklist

Before deploying, verify:

- [ ] All tests pass (`test_e2e.py`)
- [ ] LLM service is configured and working
- [ ] MCP tools are functional
- [ ] All agents are using LangChain (no HelloAgents dependency)
- [ ] All output is in English
- [ ] API endpoints are working
- [ ] Frontend can connect to backend
- [ ] Environment variables are set
- [ ] `uv` tool is installed
- [ ] API keys are configured
- [ ] CORS is configured for production domains

## Post-Deployment

### Monitor These Metrics

1. **API Response Times**
   - Target: < 30 seconds for trip planning
   - Monitor: Average, P95, P99

2. **Error Rates**
   - Target: < 1% error rate
   - Monitor: 5xx errors, LLM failures, MCP failures

3. **System Resources**
   - CPU usage
   - Memory usage
   - Disk I/O

4. **User Experience**
   - Trip plan generation success rate
   - User satisfaction (if tracking)

### Regular Maintenance

1. **Update Dependencies**
   - Regularly update Python packages
   - Update Node.js packages
   - Monitor security advisories

2. **Monitor LLM Costs**
   - Track API usage
   - Optimize prompts if needed
   - Consider caching strategies

3. **Backup Configuration**
   - Backup `.env` files
   - Document configuration changes
   - Version control configuration templates

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review logs
3. Check API documentation at `/docs`
4. Review migration logs in `backend/MIGRATION_LOG.md`

---

**Last Updated:** 2025-01-XX  
**Version:** 1.0.0  
**Framework:** LangChain (migrated from HelloAgents)
