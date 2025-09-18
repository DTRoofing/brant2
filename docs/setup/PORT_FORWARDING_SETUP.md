# Port Forwarding Setup - Fixed ✅

## Current Configuration

### Frontend (Next.js)

- **Port**: 3000
- **URL**: <http://localhost:3000>
- **Status**: ✅ Running (PID: 42896)
- **Process**: `npm run dev`

### Backend (FastAPI)

- **Port**: 3001  
- **URL**: <http://localhost:3001>
- **Status**: ✅ Running (PID: 48132)
- **Process**: `python test_server.py`

## Test URLs

### Frontend Pages

- **Main App**: <http://localhost:3000>
- **Upload Page**: <http://localhost:3000/upload>
- **Dashboard**: <http://localhost:3000/dashboard>
- **Estimate Page**: <http://localhost:3000/estimate>
- **Processing Page**: <http://localhost:3000/processing>

### Backend API Endpoints

- **Health Check**: <http://localhost:3001/api/v1/health>
- **API Docs**: <http://localhost:3001/docs>
- **Upload**: <http://localhost:3001/api/v1/documents/upload>
- **Pipeline Process**: <http://localhost:3001/api/v1/pipeline/process/{document_id}>
- **Pipeline Status**: <http://localhost:3001/api/v1/pipeline/status/{document_id}>
- **Pipeline Results**: <http://localhost:3001/api/v1/pipeline/results/{document_id}>

### Test Files

- **Standalone Test**: <http://localhost:3000/test-upload.html>

## CORS Configuration

The backend is configured to allow requests from:

- `http://localhost:3000` (Frontend)
- All methods and headers allowed
- Credentials enabled

## Verification Commands

```bash
# Check if ports are listening
netstat -ano | findstr :3000
netstat -ano | findstr :3001

# Test frontend
curl http://localhost:3000

# Test backend
curl http://localhost:3001/api/v1/health

# Test API with Python
python -c "import requests; print(requests.get('http://localhost:3001/api/v1/health').json())"
```

## Troubleshooting

If ports are not accessible:

1. **Kill existing processes**:

   ```bash
   taskkill //F //PID <PID_NUMBER>
   ```

2. **Restart servers**:

   ```bash
   # Frontend
   cd frontend_ux && npm run dev
   
   # Backend  
   cd app && python test_server.py
   ```

3. **Check firewall/antivirus** - ensure ports 3000 and 3001 are not blocked

## Status: ✅ WORKING

Both servers are running and accessible. Port forwarding is properly configured.
