# Restart App Commands

## Quick Restart (Copy & Paste)

Run these commands in your terminal (PowerShell, CMD, or Git Bash):

```bash
# Navigate to project directory
cd "C:\Development\Final Build\brant"

# Stop all services
docker compose --profile local down

# Rebuild and start all services
docker compose --profile local up --build -d

# Check service status
docker compose --profile local ps

# Test Next.js build
docker compose --profile local exec frontend-local npm run build
```

## Alternative Commands (if docker compose doesn't work)

```bash
# Using docker-compose (v1)
docker-compose --profile local down
docker-compose --profile local up --build -d
docker-compose --profile local ps
docker-compose --profile local exec frontend-local npm run build
```

## What This Does

1. **Stops** all running containers
2. **Rebuilds** all services with latest changes
3. **Starts** all services in detached mode
4. **Tests** the Next.js build to verify the fix

## Expected Results

After running these commands, you should see:

### ✅ **Build Success**
```
[+] Building 0.5s (5/5) FINISHED
✔ brant-api                       Built
✔ brant-frontend-local            Built  
✔ brant-worker                    Built
```

### ✅ **Services Running**
```
NAME                     STATUS
brant-api-local          Up
brant-frontend-local     Up
brant-worker-local       Up
brant-postgres-local     Up
brant-redis-1            Up
brant-flower-1           Up
```

### ✅ **Next.js Build Success**
```
✓ Compiled successfully
✓ Linting and checking validity of types
✓ Collecting page data
✓ Generating static pages
✓ Build completed successfully
```

## Access Points

Once restarted, access the app at:

- **Frontend**: http://localhost:3000
- **API**: http://localhost:3001
- **API Docs**: http://localhost:3001/docs
- **Celery Monitor**: http://localhost:5555

## Troubleshooting

If you encounter issues:

1. **Check Docker**: Ensure Docker Desktop is running
2. **Check Ports**: Ensure ports 3000, 3001, 5432, 6379, 5555 are available
3. **View Logs**: `docker compose --profile local logs -f`
4. **Force Rebuild**: `docker compose --profile local up --build --force-recreate -d`

---

**Ready to restart!** 🚀 Copy and paste the commands above into your terminal.
