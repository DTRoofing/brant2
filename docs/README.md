---
title: "Brant Roofing System - Documentation Index"
version: "1.1.0"
last_updated: "2025-01-15"
owner: "Development Team"
audience: "All Users"
status: "Active"
type: "Documentation Index"
tags: ["documentation", "index", "navigation"]
---

# Brant Roofing System - Documentation Index

Welcome to the comprehensive documentation for the Brant Roofing System. This index provides organized access to all project documentation.

## 📋 Quick Navigation

### 🚀 Getting Started
- [Main Project README](../README.md) - Project overview and quick start
- [Setup Instructions](setup_instructions.md) - Complete installation guide
- [Deployment Guide](DEPLOYMENT.md) - Production deployment procedures

### 🔧 Development
- [Frontend Development](../frontend_ux/README.md) - Frontend-specific documentation
- [API Documentation](sharepoint/04-api-documentation.md) - Complete API reference
- [Markdown Style Guide](MARKDOWN_STYLE_GUIDE.md) - Documentation standards

### 🧪 Testing & Quality
- [Test Documentation](../TEST_README.md) - Automated test suite overview
- [Integration Testing Strategy](INTEGRATION_TESTING_STRATEGY.md) - Integration test approach
- [Test Reports](reports/) - Recent test execution reports

### 🌐 Deployment & Operations
- [Deployment Guide](DEPLOYMENT.md) - Production deployment procedures
- [GCP Deployment](GCP_DEPLOYMENT.md) - Google Cloud specific instructions
- [Monitoring Guide](sharepoint/08-monitoring-guide.md) - System monitoring setup

### 📊 Reports & Analysis
- [Changelog](CHANGELOG.md) - Version history and updates
- [Final Implementation Report](FINAL_IMPLEMENTATION_REPORT.md) - Project completion summary
- [Security Audit Report](SECURITY_AUDIT_COMPLETE.md) - Security compliance status

## 📚 Documentation Categories

### API Reference
- **[Complete API Documentation](sharepoint/04-api-documentation.md)** - Comprehensive API reference
- **[Endpoint Reference](sharepoint/)** - Individual endpoint documentation
- **[Authentication Guide](sharepoint/14-security-compliance.md)** - Security and auth procedures

### User Guides
- **[System Overview](sharepoint/01-system-overview.md)** - High-level system description  
- **[User Guide](sharepoint/10-user-guide.md)** - End-user instructions
- **[Admin Guide](sharepoint/11-admin-guide.md)** - Administrative procedures

### Technical Documentation
- **[Architecture Documentation](sharepoint/02-architecture-diagram.md)** - System architecture
- **[Database Schema](sharepoint/05-database-schema.md)** - Data model documentation
- **[Integration Guide](sharepoint/06-integration-guide.md)** - Third-party integrations

### Operations
- **[Troubleshooting Guide](sharepoint/09-troubleshooting-guide.md)** - Common issues and solutions
- **[Monitoring Guide](sharepoint/08-monitoring-guide.md)** - System monitoring procedures
- **[Security Compliance](sharepoint/14-security-compliance.md)** - Security measures and compliance

## 🔍 Quick Reference

### Essential Endpoints
- **API Health**: http://localhost:3001/api/v1/health
- **API Documentation**: http://localhost:3001/docs  
- **Upload Endpoint**: POST http://localhost:3001/api/v1/documents/upload

### Development Services
- **Frontend**: http://localhost:3000
- **API**: http://localhost:3001
- **Flower (Task Monitor)**: http://localhost:5555
- **Database**: localhost:5432

### Key Components
- **Backend**: FastAPI + SQLAlchemy + Celery
- **Frontend**: Next.js + TypeScript + Tailwind CSS
- **Database**: PostgreSQL + Redis
- **AI Services**: Google Document AI + Anthropic Claude

## 📖 Documentation Standards

This documentation follows the [Markdown Style Guide](MARKDOWN_STYLE_GUIDE.md) for consistent formatting and structure. All contributors should review the style guide before creating or modifying documentation.

### Contributing to Documentation

1. Follow the [Markdown Style Guide](MARKDOWN_STYLE_GUIDE.md)
2. Include proper YAML front matter
3. Update this index when adding new documents
4. Ensure all links are valid and up-to-date

## 📞 Support

For questions about this documentation:

- **Development Team**: Technical questions and API documentation
- **DevOps Team**: Deployment and infrastructure questions  
- **Product Team**: User experience and feature documentation

---

**Last Updated**: January 15, 2025  
**Document Maintainer**: Development Team  
**Next Review**: April 15, 2025