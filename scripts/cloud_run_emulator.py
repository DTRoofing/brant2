#!/usr/bin/env python3
"""
Cloud Run Build Process Emulator

This script emulates the exact Cloud Run build and deployment process locally
to identify potential failure points before actual deployment.

Usage:
    python scripts/cloud_run_emulator.py [--service api|worker|frontend|all]
"""

import os
import sys
import subprocess
import docker
import json
import time
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

class ServiceType(Enum):
    API = "api"
    WORKER = "worker" 
    FRONTEND = "frontend"

@dataclass
class CloudRunConfig:
    """Configuration for Cloud Run services."""
    service_name: str
    dockerfile: str
    context_dir: str
    port: int
    env_vars: Dict[str, str]
    build_args: Dict[str, str] = None
    target: Optional[str] = None

class CloudRunEmulator:
    """Emulates Cloud Run build and deployment process."""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.project_root = Path(__file__).parent.parent
        self.docker_client = None
        
        # Cloud Run service configurations
        self.services = {
            ServiceType.API: CloudRunConfig(
                service_name="brant-api",
                dockerfile="backend.Dockerfile",
                context_dir=".",
                port=8080,
                env_vars={
                    "PORT": "8080",
                    "GOOGLE_CLOUD_PROJECT": "test-project",
                    "DATABASE_URL": "postgresql://test:test@localhost:5432/test",
                    "SECRET_KEY": "test-secret-key-for-cloud-run-emulation",
                    "CELERY_BROKER_URL": "redis://localhost:6379/0",
                    "DEBUG": "false"
                }
            ),
            ServiceType.WORKER: CloudRunConfig(
                service_name="brant-worker",
                dockerfile="worker.Dockerfile", 
                context_dir=".",
                port=None,  # Workers don't expose ports
                env_vars={
                    "GOOGLE_CLOUD_PROJECT": "test-project",
                    "DATABASE_URL": "postgresql://test:test@localhost:5432/test",
                    "CELERY_BROKER_URL": "redis://localhost:6379/0",
                    "CELERY_CONCURRENCY": "2"
                }
            ),
            ServiceType.FRONTEND: CloudRunConfig(
                service_name="brant-frontend",
                dockerfile="Dockerfile",
                context_dir="frontend_ux",
                port=3000,
                env_vars={
                    "NODE_ENV": "production",
                    "NEXT_PUBLIC_API_URL": "https://api.example.com"
                },
                build_args={
                    "NEXT_PUBLIC_API_URL": "https://api.example.com"
                },
                target="release"
            )
        }
        
    def setup_docker_client(self) -> bool:
        """Initialize Docker client and verify connectivity."""
        try:
            self.docker_client = docker.from_env()
            self.docker_client.ping()
            self.log("✅ Docker client connected successfully")
            return True
        except Exception as e:
            self.log(f"❌ Failed to connect to Docker: {e}")
            return False
    
    def log(self, message: str):
        """Log message with timestamp."""
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")
        
    def run_command(self, cmd: List[str], cwd: Optional[Path] = None) -> Tuple[int, str, str]:
        """Run command and return exit code, stdout, stderr."""
        if cwd is None:
            cwd = self.project_root
            
        if self.verbose:
            self.log(f"Running: {' '.join(cmd)} in {cwd}")
            
        try:
            result = subprocess.run(
                cmd, cwd=cwd, capture_output=True, text=True, timeout=1800
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return 1, "", "Command timed out"
        except Exception as e:
            return 1, "", str(e)

    def emulate_cloud_build_quality_gate(self) -> bool:
        """Emulate the Cloud Build quality gate step."""
        self.log("🔍 Emulating Cloud Build Quality Gate...")
        
        # Step 1: Update pip and install poetry (like Cloud Build)
        self.log("Installing build dependencies...")
        exit_code, stdout, stderr = self.run_command([
            sys.executable, "-m", "pip", "install", "--upgrade", 
            "pip", "poetry==1.8.2", "pip-audit"
        ])
        
        if exit_code != 0:
            self.log(f"❌ Failed to install build dependencies: {stderr}")
            return False
            
        # Step 2: Poetry lock (like Cloud Build)
        self.log("Checking Poetry lock file...")
        exit_code, stdout, stderr = self.run_command([
            "poetry", "lock", "--no-update"
        ])
        
        if exit_code != 0:
            self.log(f"❌ Poetry lock failed: {stderr}")
            return False
            
        # Step 3: Install dependencies (like Cloud Build)
        self.log("Installing dependencies...")
        exit_code, stdout, stderr = self.run_command([
            "poetry", "install", "--no-interaction", "--no-ansi"
        ])
        
        if exit_code != 0:
            self.log(f"❌ Dependency installation failed: {stderr}")
            return False
            
        # Step 4: Run unit tests (like Cloud Build)
        self.log("Running unit tests...")
        exit_code, stdout, stderr = self.run_command([
            "poetry", "run", "pytest", "-m", "not integration and not e2e", "--tb=short"
        ])
        
        if exit_code != 0:
            self.log(f"❌ Unit tests failed: {stderr}")
            if self.verbose:
                self.log(f"Test output: {stdout}")
            return False
            
        # Step 5: Security scan (like Cloud Build)
        self.log("Running vulnerability scan...")
        exit_code, stdout, stderr = self.run_command(["pip-audit"])
        
        if exit_code != 0:
            self.log(f"⚠️ Vulnerability scan found issues: {stderr}")
            # Don't fail build for vulnerabilities, just warn
            
        self.log("✅ Quality gate passed")
        return True

    def build_docker_image(self, service_type: ServiceType) -> bool:
        """Build Docker image exactly like Cloud Build (using Kaniko simulation)."""
        config = self.services[service_type]
        self.log(f"🐳 Building Docker image for {config.service_name}...")
        
        # Build command like Kaniko
        build_cmd = ["docker", "build"]
        
        # Add context directory
        build_context = self.project_root / config.context_dir
        
        # Add dockerfile
        if config.context_dir == ".":
            build_cmd.extend(["-f", config.dockerfile])
        else:
            build_cmd.extend(["-f", f"{config.context_dir}/{config.dockerfile}"])
            
        # Add build args (like Cloud Build)
        if config.build_args:
            for key, value in config.build_args.items():
                build_cmd.extend(["--build-arg", f"{key}={value}"])
                
        # Add target (like Cloud Build)
        if config.target:
            build_cmd.extend(["--target", config.target])
            
        # Add cache flag (like Kaniko)
        build_cmd.append("--no-cache")  # Simulate fresh build
        
        # Add tag
        build_cmd.extend(["-t", f"{config.service_name}:cloud-run-test"])
        
        # Add context
        build_cmd.append(str(build_context))
        
        # Run build
        exit_code, stdout, stderr = self.run_command(build_cmd)
        
        if exit_code != 0:
            self.log(f"❌ Docker build failed for {config.service_name}")
            if self.verbose:
                self.log(f"Build output: {stdout}")
                self.log(f"Build errors: {stderr}")
            return False
            
        self.log(f"✅ Docker build successful for {config.service_name}")
        return True

    def test_container_startup(self, service_type: ServiceType) -> bool:
        """Test that the container starts successfully."""
        config = self.services[service_type]
        self.log(f"🚀 Testing container startup for {config.service_name}...")
        
        try:
            # Run container with Cloud Run-like environment
            container_name = f"{config.service_name}-test"
            
            # Remove existing container if it exists
            try:
                existing = self.docker_client.containers.get(container_name)
                existing.remove(force=True)
            except docker.errors.NotFound:
                pass
                
            # Prepare environment variables
            env_vars = config.env_vars.copy()
            
            # Run container
            if config.port:
                # Service with port (API, Frontend)
                ports = {f'{config.port}/tcp': config.port}
                container = self.docker_client.containers.run(
                    f"{config.service_name}:cloud-run-test",
                    name=container_name,
                    environment=env_vars,
                    ports=ports,
                    detach=True,
                    remove=True
                )
            else:
                # Worker service (no port)
                container = self.docker_client.containers.run(
                    f"{config.service_name}:cloud-run-test",
                    name=container_name, 
                    environment=env_vars,
                    detach=True,
                    remove=True
                )
            
            # Wait for startup
            time.sleep(10)
            
            # Check container status
            container.reload()
            if container.status != 'running':
                logs = container.logs().decode()
                self.log(f"❌ Container failed to start: {logs}")
                return False
                
            # Test health endpoint for services with ports
            if config.port and service_type == ServiceType.API:
                import requests
                try:
                    response = requests.get(f"http://localhost:{config.port}/api/v1/health", timeout=10)
                    if response.status_code != 200:
                        self.log(f"❌ Health check failed: {response.status_code}")
                        return False
                except requests.exceptions.RequestException as e:
                    self.log(f"❌ Health check request failed: {e}")
                    return False
            
            # Stop container
            container.stop()
            self.log(f"✅ Container startup test passed for {config.service_name}")
            return True
            
        except Exception as e:
            self.log(f"❌ Container startup test failed: {e}")
            return False

    def emulate_cloud_run_deployment(self, service_type: ServiceType) -> bool:
        """Emulate the full Cloud Run deployment process for a service."""
        config = self.services[service_type]
        self.log(f"\n🏗️ Emulating Cloud Run deployment for {config.service_name}")
        
        # Step 1: Build Docker image (like Cloud Build)
        if not self.build_docker_image(service_type):
            return False
            
        # Step 2: Test container startup (like Cloud Run)
        if not self.test_container_startup(service_type):
            return False
            
        self.log(f"✅ Cloud Run deployment emulation successful for {config.service_name}")
        return True

    def run_full_emulation(self, services: List[ServiceType] = None) -> Dict[ServiceType, bool]:
        """Run full Cloud Run build and deployment emulation."""
        if not self.setup_docker_client():
            return {}
            
        if services is None:
            services = list(ServiceType)
            
        self.log("🚀 Starting Cloud Run Build Process Emulation")
        self.log("=" * 60)
        
        # Step 1: Quality gate (common to all services)
        if not self.emulate_cloud_build_quality_gate():
            self.log("❌ Quality gate failed - stopping emulation")
            return {service: False for service in services}
        
        # Step 2: Build and test each service
        results = {}
        for service_type in services:
            success = self.emulate_cloud_run_deployment(service_type)
            results[service_type] = success
            
        # Summary
        self.log("\n📊 EMULATION RESULTS:")
        self.log("=" * 30)
        
        total_services = len(results)
        successful = sum(1 for success in results.values() if success)
        
        for service_type, success in results.items():
            status = "✅ PASS" if success else "❌ FAIL"
            self.log(f"{service_type.value.upper()}: {status}")
            
        self.log(f"\nSUCCESS RATE: {successful}/{total_services} ({successful/total_services*100:.1f}%)")
        
        if successful == total_services:
            self.log("\n🎉 ALL SERVICES READY FOR CLOUD RUN DEPLOYMENT!")
        else:
            self.log(f"\n⚠️ {total_services - successful} SERVICE(S) WOULD FAIL IN CLOUD RUN")
            
        return results

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Cloud Run Build Process Emulator")
    parser.add_argument("--service", choices=["api", "worker", "frontend", "all"], 
                       default="all", help="Service to emulate")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Enable verbose output")
    
    args = parser.parse_args()
    
    emulator = CloudRunEmulator(verbose=args.verbose)
    
    if args.service == "all":
        services = list(ServiceType)
    else:
        services = [ServiceType(args.service)]
    
    results = emulator.run_full_emulation(services)
    
    # Exit with error if any service failed
    failed_count = sum(1 for success in results.values() if not success)
    sys.exit(failed_count)

if __name__ == "__main__":
    main()
