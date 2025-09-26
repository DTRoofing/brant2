#!/bin/bash
"""
Automated Build Fixer Runner
"""
set -e

# Configuration
PROJECT_ID="brant-roofing-system-2025"
REGION="us-central1"
MAX_ATTEMPTS=3

echo "🤖 Automated Build Fixer"
echo "========================="
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo "Max Attempts: $MAX_ATTEMPTS"
echo ""

# Check if gcloud is installed and authenticated
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI not found. Please install Google Cloud SDK."
    exit 1
fi

# Check if user is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "❌ Not authenticated with gcloud. Please run 'gcloud auth login'"
    exit 1
fi

# Check if project exists and user has access
if ! gcloud projects describe $PROJECT_ID &> /dev/null; then
    echo "❌ Project $PROJECT_ID not found or no access"
    exit 1
fi

# Set the project
gcloud config set project $PROJECT_ID

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3."
    exit 1
fi

# Install required Python packages if not already installed
echo "📦 Checking Python dependencies..."
python3 -c "import subprocess, json, re, logging, pathlib, time, dataclasses, enum" 2>/dev/null || {
    echo "Installing required packages..."
    pip3 install --user subprocess-mock
}

# Make sure we're in the right directory
if [ ! -f "cloudbuild.yaml" ]; then
    echo "❌ cloudbuild.yaml not found. Please run from the project root."
    exit 1
fi

# Run the automated fixer
echo "🚀 Starting automated build fixer..."
echo ""

for attempt in $(seq 1 $MAX_ATTEMPTS); do
    echo "🔄 Attempt $attempt/$MAX_ATTEMPTS"
    echo "================================"
    
    if python3 smart_build_fixer.py $PROJECT_ID $REGION; then
        echo ""
        echo "🎉 SUCCESS! Build errors have been automatically resolved."
        echo "✅ The build should now pass without errors."
        exit 0
    else
        echo ""
        echo "⚠️ Attempt $attempt failed. "
        
        if [ $attempt -lt $MAX_ATTEMPTS ]; then
            echo "🔄 Retrying in 30 seconds..."
            sleep 30
        else
            echo "❌ All attempts failed. Manual intervention may be required."
            echo ""
            echo "📋 Check the logs for details:"
            echo "   - smart_build_fixer.log"
            echo "   - Recent build logs in Google Cloud Console"
            echo ""
            echo "🔧 Common manual fixes:"
            echo "   1. Check IAM permissions for Cloud Build service account"
            echo "   2. Verify all required APIs are enabled"
            echo "   3. Check for syntax errors in Python files"
            echo "   4. Ensure all dependencies are properly installed"
            exit 1
        fi
    fi
done
