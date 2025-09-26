# Run Local App - Instructions

## Quick Start Commands

Since Docker is not available in the current shell environment, please run these commands in your preferred terminal:

### Option 1: Using Docker Desktop (Recommended)
```bash
# Navigate to the project directory
cd "C:\Development\Final Build\brant"

# Start all services
docker compose --profile local up --build -d

# Check service status
docker compose --profile local ps

# View logs
docker compose --profile local logs -f
```

### Option 2: Using Docker Compose v1
```bash
# Navigate to the project directory
cd "C:\Development\Final Build\brant"

# Start all services
docker-compose --profile local up --build -d

# Check service status
docker-compose --profile local ps

# View logs
docker-compose --profile local logs -f
```

### Option 3: Using the Test Script
```bash
# Navigate to the project directory
cd "C:\Development\Final Build\brant"

# Run the automated test script
test-docker-compose-fix.bat
```

## Expected Results

After running the commands, you should see:

### ✅ **Build Success**
```
[+] Building 0.5s (5/5) FINISHED
✔ brant-api                       Built
✔ brant-frontend-local            Built  
✔ brant-worker                    Built
```

### ✅ **Services Running**
```
✔ Container brant-redis-1         Healthy
✔ Container brant-postgres-local  Healthy
✔ Container brant-api-local       Started
✔ Container brant-flower-1        Started
✔ Container brant-worker-local    Started
✔ Container brant-frontend-local  Started
```

## Access Points

Once running, access the application at:

- **Frontend**: http://localhost:3000
- **API**: http://localhost:3001
- **API Documentation**: http://localhost:3001/docs
- **Celery Monitor**: http://localhost:5555

## Troubleshooting

### If Docker is not found:
1. **Start Docker Desktop** - Ensure Docker Desktop is running
2. **Check PATH** - Ensure Docker is in your system PATH
3. **Restart Terminal** - Close and reopen your terminal

### If services fail to start:
1. **Check ports** - Ensure ports 3000, 3001, 5432, 6379, 5555 are available
2. **Check logs** - Run `docker compose --profile local logs`
3. **Rebuild** - Run `docker compose --profile local up --build --force-recreate`

### If you see "Dockerfile not found" error:
- This should be fixed now with our recent changes
- The frontend service now has proper context and dockerfile specifications

## Stop the Application

To stop all services:
```bash
docker compose --profile local down
```

## Development Mode

The application runs in development mode with:
- **Hot Reloading**: Frontend changes are automatically reflected
- **Volume Mounts**: Code changes are immediately available in containers
- **Debug Logging**: Enhanced logging for development

---

**Ready to run!** 🚀 Choose one of the options above and start your local development environment.
