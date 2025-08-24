# KRNL Onboarding System - Troubleshooting Guide

## Common Issues and Solutions

### "Failed to fetch" / "API request fail" Errors

These errors typically occur when the frontend cannot connect to the backend API. Here are the most common causes and solutions:

#### 1. Backend Service Not Running

**Symptoms:**
- "Failed to fetch" error in browser console
- "Network error - unable to connect to server" notification
- API calls timeout

**Solution:**
```bash
# Check if services are running
docker-compose ps

# If not running, start them
docker-compose up -d

# Check logs for any startup errors
docker-compose logs backend
```

#### 2. CORS (Cross-Origin Resource Sharing) Issues

**Symptoms:**
- CORS errors in browser console
- Preflight request failures
- "Access-Control-Allow-Origin" errors

**Solution:**
The backend has been updated with proper CORS configuration. Restart the services:
```bash
docker-compose down
docker-compose up --build -d
```

#### 3. Network Configuration Issues

**Symptoms:**
- Services running but still can't connect
- Different behavior between localhost and 127.0.0.1

**Solution:**
1. Try accessing the API directly: http://localhost:8000/health
2. If that fails, check Docker networking:
```bash
docker network ls
docker network inspect simple_krnl-network
```

#### 4. Port Conflicts

**Symptoms:**
- Services fail to start
- Port already in use errors

**Solution:**
```bash
# Check what's using the ports
netstat -an | findstr :8000
netstat -an | findstr :3000

# Kill processes using these ports or change ports in docker-compose.yml
```

### Bulk Upload Issues

#### "Bulk upload failed: Failed to fetch"

**Causes and Solutions:**

1. **File too large**
   - Solution: Reduce CSV file size or increase timeout
   - Check file size limit in nginx configuration

2. **Invalid CSV format**
   - Ensure CSV has required headers: name, email, role, department, start_date
   - Check for special characters or encoding issues
   - Validate date format (YYYY-MM-DD)

3. **Backend timeout**
   - Increase timeout in nginx configuration
   - Process smaller batches

### Quick Diagnostic Steps

1. **Check API Health**
   ```bash
   curl http://localhost:8000/health
   ```
   Expected response:
   ```json
   {
     "status": "healthy",
     "timestamp": "2025-01-XX...",
     "service": "krnl-onboarding-api"
   }
   ```

2. **Check Frontend Access**
   ```bash
   curl http://localhost:3000
   ```

3. **Check Docker Services**
   ```bash
   docker-compose ps
   docker-compose logs --tail=50
   ```

4. **Check Network Connectivity**
   - Open browser developer tools (F12)
   - Go to Network tab
   - Refresh the page and check for failed requests
   - Look for specific error messages

### Environment Configuration

Ensure your `.env` file exists with proper configuration:

```bash
# Check if .env exists
ls -la .env

# If missing, copy from the example
cp .env.example .env  # or run start.bat/start.sh
```

### Service Dependencies

The services have dependencies:
1. PostgreSQL database must start first
2. Redis must start before backend
3. Backend must be healthy before frontend can work properly

### Browser-Specific Issues

1. **Clear Browser Cache**
   - Hard refresh: Ctrl+F5 (Windows) / Cmd+Shift+R (Mac)
   - Clear browser cache and cookies

2. **Disable Browser Extensions**
   - Ad blockers might interfere with API calls
   - CORS extensions might cause conflicts

3. **Check Browser Console**
   - Press F12 to open developer tools
   - Look for error messages in Console tab
   - Check Network tab for failed requests

### Getting Help

If issues persist:

1. **Collect Diagnostic Information**
   ```bash
   docker-compose ps > system_status.txt
   docker-compose logs > system_logs.txt
   curl -v http://localhost:8000/health >> system_status.txt
   ```

2. **Check Service Logs**
   ```bash
   # Backend logs
   docker-compose logs backend

   # Frontend/Nginx logs
   docker-compose logs frontend

   # Database logs
   docker-compose logs postgres
   ```

3. **Common Error Patterns**
   - `Connection refused`: Backend not running
   - `CORS error`: Browser security issue
   - `404 Not Found`: Wrong API endpoint
   - `500 Internal Server Error`: Backend application error
   - `timeout`: Service taking too long to respond

### Production Deployment Notes

For production deployments:

1. **Update CORS Origins**
   - Change `allow_origins=["*"]` to specific domains
   - Update `API_BASE_URL` in frontend

2. **Use Environment-Specific Configuration**
   - Create separate .env files for different environments
   - Use proper SSL certificates

3. **Monitor Service Health**
   - Implement proper health checks
   - Set up monitoring and alerting