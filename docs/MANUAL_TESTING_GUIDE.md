# Manual Testing Guide - Restart and Test Development Server

## Quick Commands

### Windows (PowerShell/CMD)
```bash
# Navigate to project directory
cd "C:\Development\Final Build\brant"

# Run the automated script
restart-and-test-dev.bat

# Or run manually:
docker compose --profile local down
docker compose --profile local up --build -d
docker compose --profile local exec frontend-local npm run build
```

### Linux/Mac (Terminal)
```bash
# Navigate to project directory
cd "/c/Development/Final Build/brant"

# Run the automated script
./restart-and-test-dev.sh

# Or run manually:
docker compose --profile local down
docker compose --profile local up --build -d
docker compose --profile local exec frontend-local npm run build
```

## Step-by-Step Manual Testing

### 1. Stop Current Services
```bash
docker compose --profile local down
```

### 2. Clean Up (Optional)
```bash
docker compose --profile local down --remove-orphans
docker system prune -f  # Remove unused containers/images
```

### 3. Rebuild and Start Services
```bash
docker compose --profile local up --build -d
```

### 4. Check Service Status
```bash
docker compose --profile local ps
```

**Expected Output:**
```
NAME                     IMAGE                    COMMAND                  SERVICE             STATUS
brant-api-local          brant-roofing-system     "uvicorn app.main:app"  api                 Up
brant-frontend-local     brant-roofing-system     "npm run dev"           frontend-local      Up
brant-worker-local       brant-roofing-system     "celery -A app.worker"  worker              Up
brant-postgres-local     postgres:15-alpine       "docker-entrypoint.s…"  postgres            Up
brant-redis-1            redis:7-alpine           "docker-entrypoint.s…"  redis               Up
brant-flower-1           mher/flower              "celery flower"         flower              Up
```

### 5. Test Next.js Build
```bash
docker compose --profile local exec frontend-local npm run build
```

**Expected Output:**
```
> my-v0-project@0.1.0 build
> next build

Creating optimized production build...
✓ Compiled successfully
✓ Linting and checking validity of types
✓ Collecting page data
✓ Generating static pages (0/1)
✓ Finalizing page optimization

Route (app)                              Size     First Load JS
┌ ○ /                                    1.2 kB         87.2 kB
└ ○ /404                                 1.2 kB         87.2 kB
+ First Load JS shared by all           86.0 kB
  ├ chunks/framework-7c8c2cdb55a3f6a7.js    45.4 kB
  ├ chunks/main-app-4b8c8b8b8b8b8b8b.js    41.6 kB
  └ chunks/webpack-8b8b8b8b8b8b8b8b.js     1.0 kB

✓ Build completed successfully
```

### 6. Test API Health
```bash
curl http://localhost:3001/api/v1/health
```

**Expected Output:**
```json
{"status":"healthy","timestamp":"2024-01-01T00:00:00Z"}
```

### 7. Test Frontend Access
```bash
curl -I http://localhost:3000
```

**Expected Output:**
```
HTTP/1.1 200 OK
Content-Type: text/html; charset=utf-8
```

### 8. View Logs (Optional)
```bash
# All services
docker compose --profile local logs -f

# Specific service
docker compose --profile local logs frontend-local -f
docker compose --profile local logs api -f
```

## Troubleshooting

### If Build Fails
1. **Check logs**: `docker compose --profile local logs frontend-local`
2. **Check dependencies**: `docker compose --profile local exec frontend-local npm list`
3. **Clear cache**: `docker compose --profile local exec frontend-local npm run build -- --no-cache`

### If Services Don't Start
1. **Check ports**: Ensure 3000, 3001, 5432, 6379, 5555 are available
2. **Check memory**: Ensure sufficient RAM for all services
3. **Check Docker**: Ensure Docker Desktop is running

### If API/Frontend Not Accessible
1. **Wait longer**: Services may need more time to start
2. **Check container logs**: Look for error messages
3. **Verify network**: Check if containers can communicate

## Expected Results

### ✅ **Success Indicators**
- All containers show "Up" status
- Next.js build completes without errors
- API health endpoint returns 200 OK
- Frontend loads in browser at http://localhost:3000
- No compilation errors in logs

### 🎯 **Access Points**
- **Frontend**: http://localhost:3000
- **API**: http://localhost:3001
- **API Documentation**: http://localhost:3001/docs
- **Celery Monitor**: http://localhost:5555

---

**Ready to test!** 🚀 Choose your preferred method and run the tests.
