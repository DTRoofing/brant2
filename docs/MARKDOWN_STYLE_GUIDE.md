---
title: "Markdown Style Guide - Brant Roofing System"
version: "1.0.0"
last_updated: "2025-01-15"
owner: "Development Team"
audience: "All Contributors"
status: "Active"
type: "Style Guide"
---

# Markdown Style Guide - Brant Roofing System

This comprehensive style guide establishes consistent markdown standards for all documentation in the Brant Roofing System project.

## 📋 Table of Contents

- [Document Structure](#document-structure)
- [Front Matter Standards](#front-matter-standards)
- [Heading Conventions](#heading-conventions)
- [Content Formatting](#content-formatting)
- [Code Blocks](#code-blocks)
- [Links and URLs](#links-and-urls)
- [Tables](#tables)
- [File Naming](#file-naming)
- [Project Terminology](#project-terminology)
- [Examples](#examples)

## Document Structure

### Required Front Matter

All markdown files **MUST** include YAML front matter with these required fields:

```yaml
---
title: "Document Title"
version: "1.0.0"
last_updated: "YYYY-MM-DD"
owner: "Team/Individual Name"
audience: "Target Audience"
status: "Active|Draft|Deprecated"
type: "Document Type"
---
```

### Document Organization

1. **Front matter** (required)
2. **Main heading** (H1) - matches front matter title
3. **Table of contents** (for docs > 3 sections)
4. **Content sections** with proper heading hierarchy
5. **Footer** with metadata (optional)

## Front Matter Standards

### Required Fields

| Field | Description | Valid Values | Example |
|-------|-------------|--------------|---------|
| `title` | Document title in quotes | String | "API Documentation" |
| `version` | Semantic version | x.y.z format | "1.2.0" |
| `last_updated` | ISO date format | YYYY-MM-DD | "2025-01-15" |
| `owner` | Responsible team/person | String | "Development Team" |
| `audience` | Target readers | String | "Developers" |
| `status` | Document lifecycle | Active/Draft/Deprecated | "Active" |
| `type` | Document category | See types below | "API Reference" |

### Document Types

| Type | Usage | Examples |
|------|-------|----------|
| `Setup Guide` | Installation/configuration | Setup instructions |
| `API Reference` | API documentation | Endpoint documentation |
| `User Guide` | End-user instructions | How-to guides |
| `Test Report` | Testing documentation | Test results, strategies |
| `Style Guide` | Standards documentation | This document |
| `Implementation Report` | Feature documentation | Feature specs |
| `Troubleshooting` | Problem resolution | Error guides |
| `Architecture` | System design | Technical diagrams |

### Optional Fields

```yaml
tags: ["api", "setup", "testing"]     # Topic tags
related_docs: ["setup.md", "api.md"] # Related files
review_date: "2025-04-15"            # Next review
priority: "High"                     # Document priority
```

## Heading Conventions

### Hierarchy Rules

1. **One H1 per document** - matches front matter title
2. **Sequential hierarchy** - don't skip levels (H1 → H2 → H3)
3. **Descriptive headings** - clearly indicate section content

### Emoji Usage Standards

**Consistent emoji usage** for common section types:

| Section Type | Emoji | Example |
|--------------|-------|---------|
| Table of Contents | 📋 | `## 📋 Table of Contents` |
| Getting Started | 🚀 | `## 🚀 Getting Started` |
| Installation | 🔧 | `## 🔧 Installation` |
| Configuration | ⚙️ | `## ⚙️ Configuration` |
| API Reference | 🔗 | `## 🔗 API Reference` |
| Examples | 💡 | `## 💡 Examples` |
| Testing | 🧪 | `## 🧪 Testing` |
| Troubleshooting | 🚨 | `## 🚨 Troubleshooting` |
| Security | 🔒 | `## 🔒 Security` |
| Performance | ⚡ | `## ⚡ Performance` |
| Deployment | 🌐 | `## 🌐 Deployment` |
| Monitoring | 📊 | `## 📊 Monitoring` |

### Capitalization

**Use Title Case** for all headings:
- ✅ `## API Integration Guide`
- ✅ `### Database Configuration`
- ❌ `## api integration guide`
- ❌ `### Database configuration`

## Content Formatting

### Lists

**Unordered Lists:**
```markdown
- First item
- Second item
  - Nested item
  - Another nested item
- Third item
```

**Ordered Lists:**
```markdown
1. First step
2. Second step
   - Sub-requirement
   - Another sub-requirement
3. Third step
```

### Emphasis

| Style | Markdown | Usage |
|-------|----------|-------|
| **Bold** | `**text**` | Important terms, UI elements |
| *Italic* | `*text*` | Emphasis, first mention of terms |
| `Code` | `\`code\`` | File names, commands, variables |

### Project Terminology

**Always use consistent project naming:**

| ✅ Correct | ❌ Incorrect |
|------------|-------------|
| Brant Roofing System | DT Commercial Roofing |
| Brant Roofing System | DT Roofing Agent |
| API endpoints | api endpoints |
| Google Cloud Storage | GCS |
| PostgreSQL | postgres |

## Code Blocks

### Language Specification

**Always specify language** for syntax highlighting:

```markdown
\`\`\`bash
docker-compose up --build
\`\`\`

\`\`\`python
def process_document(doc_id):
    return {"status": "processed"}
\`\`\`

\`\`\`yaml
version: "3.8"
services:
  api:
    build: .
\`\`\`
```

### Common Languages

| Language | Use For | Example |
|----------|---------|---------|
| `bash` | Shell commands | `docker logs api` |
| `python` | Python code | Function definitions |
| `yaml` | Configuration files | docker-compose.yml |
| `json` | API responses | JSON payloads |
| `javascript` | JS/TS code | React components |
| `sql` | Database queries | SELECT statements |
| `dockerfile` | Docker files | FROM python:3.11 |
| `text` | Plain text output | Log messages |

### Command Examples

**Include expected output** for commands:

```bash
# Check API health
curl http://localhost:3001/api/v1/health

# Expected response:
{
  "status": "healthy",
  "timestamp": "2025-01-15T10:30:00Z"
}
```

## Links and URLs

### URL Formats

**Use plain text format** for URLs in documentation:

| ✅ Correct | ❌ Incorrect |
|------------|-------------|
| `http://localhost:3001` | `<http://localhost:3001>` |
| `https://api.example.com` | `[https://api.example.com](https://api.example.com)` |

### Internal Links

**Use relative paths** for internal documentation:

```markdown
- See [API Documentation](api-documentation.md)
- Refer to [Setup Guide](../setup/installation.md)
```

### External Links

**Use descriptive link text**:

```markdown
- [Google Cloud Documentation](https://cloud.google.com/docs)
- [Docker Compose Reference](https://docs.docker.com/compose/)
```

## Tables

### Standard Format

**Use proper alignment** and spacing:

```markdown
| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Value 1  | Value 2  | Value 3  |
| Data A   | Data B   | Data C   |
```

### Service Tables

**Standard format for service listings**:

```markdown
| Service | URL | Description |
|---------|-----|-------------|
| **API** | http://localhost:3001 | Main application API |
| **Docs** | http://localhost:3001/docs | Interactive API documentation |
```

## File Naming

### Conventions

**Use clear, descriptive names** with consistent patterns:

| File Type | Pattern | Examples |
|-----------|---------|----------|
| Setup guides | `{topic}-setup.md` | `database-setup.md` |
| API docs | `api-{service}.md` | `api-documents.md` |
| Test reports | `{type}-test-report.md` | `integration-test-report.md` |
| User guides | `{feature}-guide.md` | `user-guide.md` |
| Style guides | `{type}-style-guide.md` | `markdown-style-guide.md` |

### Directory Organization

```text
docs/
├── api/                 # API documentation
├── setup/              # Installation guides
├── testing/            # Test documentation
├── guides/             # User guides
├── reports/            # Status reports
└── architecture/       # System design
```

## Examples

### Complete Document Template

```markdown
---
title: "Example API Documentation"
version: "1.0.0"
last_updated: "2025-01-15"
owner: "Development Team"
audience: "Developers"
status: "Active"
type: "API Reference"
tags: ["api", "rest", "endpoints"]
---

# Example API Documentation

This document provides comprehensive API documentation for the Example service.

## 📋 Table of Contents

- [Getting Started](#getting-started)
- [Authentication](#authentication)
- [Endpoints](#endpoints)
- [Examples](#examples)

## 🚀 Getting Started

### Prerequisites

- Node.js 18+
- Docker and Docker Compose
- Valid API key

### Installation

\`\`\`bash
git clone repository-url
cd project-directory
npm install
\`\`\`

## 🔒 Authentication

All API requests require authentication:

\`\`\`bash
curl -H "Authorization: Bearer your-token" \\
  http://localhost:3001/api/v1/endpoint
\`\`\`

## 🔗 Endpoints

### Health Check

\`\`\`http
GET /api/v1/health
\`\`\`

**Response:**

\`\`\`json
{
  "status": "healthy",
  "timestamp": "2025-01-15T10:30:00Z"
}
\`\`\`
```

## Compliance Checklist

Use this checklist to ensure documentation follows the style guide:

### Document Structure
- [ ] Includes required front matter
- [ ] Has single H1 heading matching title
- [ ] Uses proper heading hierarchy
- [ ] Includes table of contents (if >3 sections)

### Content Quality
- [ ] Uses consistent project terminology
- [ ] All code blocks specify language
- [ ] URLs use plain text format
- [ ] Tables are properly formatted
- [ ] Links use descriptive text

### Metadata
- [ ] All required front matter fields present
- [ ] Version follows semantic versioning
- [ ] Last updated is current
- [ ] Owner and audience are specified

## Enforcement

### Automated Checks

Consider implementing these automated checks:

1. **Front matter validation** - Ensure required fields
2. **Link checking** - Validate internal/external links
3. **Language specification** - Verify code block languages
4. **Terminology consistency** - Check project naming

### Review Process

1. **Self-review** using compliance checklist
2. **Peer review** for style guide adherence
3. **Technical review** for accuracy
4. **Final approval** by document owner

---

**Style Guide Version**: 1.0.0  
**Last Updated**: January 15, 2025  
**Next Review**: April 15, 2025  
**Maintainer**: Development Team