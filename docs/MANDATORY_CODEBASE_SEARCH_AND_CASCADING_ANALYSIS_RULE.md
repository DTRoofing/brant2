# 🔍 Mandatory Codebase Search and Cascading Analysis Rule

## **RULE: Comprehensive Error Pattern Search and Cascading Effects Analysis**

### **📋 MANDATORY PROCESS**

**Whenever ANY fix is applied to the codebase, you MUST immediately perform a comprehensive search across the ENTIRE codebase for similar error patterns AND analyze all potential cascading effects of the fix.**

---

## **🎯 RULE SCOPE AND TRIGGER**

This rule is **MANDATORY** and applies **EVERY TIME** any of the following occurs:

### **Trigger Events**
- ✅ **Bug fixes** (any code correction)
- ✅ **Error handling improvements** (adding try/catch, validation, etc.)
- ✅ **Configuration fixes** (environment variables, settings, etc.)
- ✅ **Security patches** (authentication, authorization fixes)
- ✅ **Performance optimizations** (resource usage, memory leaks, etc.)
- ✅ **Dependency updates** (library version changes)
- ✅ **API endpoint modifications** (request/response handling)
- ✅ **Database schema changes** (migration fixes)
- ✅ **Infrastructure fixes** (Docker, Cloud Run, networking)
- ✅ **Documentation corrections** (code examples, config docs)

### **What Constitutes a "Fix"**
Any change that addresses a problem, issue, error, or improvement opportunity qualifies as a fix requiring this analysis.

---

## **📊 PHASE 1: COMPREHENSIVE ERROR PATTERN SEARCH**

### **MANDATORY SEARCH PROCESS**

#### **Step 1: Error Pattern Identification**
When applying a fix, you MUST:

1. **Identify the specific error pattern** being fixed
   ```python
   # Example: Fixing hardcoded localhost URL
   # BEFORE (PROBLEMATIC):
   DATABASE_URL: str = "postgresql://user:password@localhost:5432/brant_roofing"

   # AFTER (FIXED):
   DATABASE_URL: str = Field(..., env="DATABASE_URL")
   ```

2. **Categorize the error type**:
   - **Environment Variables**: Hardcoded values, missing defaults
   - **Code Quality**: Generic exceptions, missing type hints, console.log
   - **Security**: Exposed credentials, missing validation
   - **Performance**: Memory leaks, inefficient queries, blocking I/O
   - **Configuration**: Hardcoded paths, missing environment handling
   - **Dependencies**: Missing imports, incorrect versions, circular dependencies

#### **Step 2: Systematic Codebase Search**
You MUST search the **ENTIRE codebase** using multiple search strategies:

##### **Search Scope Requirements**
- [ ] **All Python files** (`*.py`, `*.pyx`)
- [ ] **All TypeScript/JavaScript files** (`*.ts`, `*.tsx`, `*.js`, `*.jsx`)
- [ ] **All configuration files** (`*.yaml`, `*.yml`, `*.json`, `*.toml`, `*.env*`)
- [ ] **All Docker files** (`Dockerfile*`, `docker-compose*`)
- [ ] **All infrastructure files** (`*.tf`, cloudbuild.yaml)
- [ ] **All documentation** (`*.md`, `*.rst`)
- [ ] **All scripts** (`*.sh`, `*.bat`, `*.ps1`)

##### **Search Commands and Patterns**
```bash
# Environment Variables - Search for hardcoded values
grep -r "localhost" --include="*.py" --include="*.ts" --include="*.js" --include="*.yaml" --include="*.yml" .
grep -r "127\.0\.0\.1" --include="*.py" --include="*.ts" --include="*.js" --include="*.yaml" --include="*.yml" .
grep -r "DATABASE_URL.*=" --include="*.py" --include="*.env*" .

# Code Quality - Generic exception handling
grep -r "except Exception" --include="*.py" .
grep -r "except:" --include="*.py" .

# Console logging in production
grep -r "console\.log" --include="*.ts" --include="*.tsx" --include="*.js" --include="*.jsx" .

# Hardcoded credentials
grep -r "password.*=" --include="*.py" --include="*.ts" --include="*.js" --include="*.env*" .
grep -r "secret.*=" --include="*.py" --include="*.ts" --include="*.js" --include="*.env*" .
grep -r "key.*=" --include="*.py" --include="*.ts" --include="*.js" --include="*.env*" .

# Missing type hints (Python)
grep -rn "def [a-zA-Z_][a-zA-Z0-9_]*(" --include="*.py" . | grep -v "self" | head -20

# Wildcard imports
grep -r "import \*" --include="*.py" .
grep -r "import \* as" --include="*.py" --include="*.ts" --include="*.js" .
```

#### **Step 3: Pattern Analysis and Documentation**
For each search, you MUST document:

1. **Search Query Used**: Exact command or pattern
2. **Files Searched**: Which directories/file types
3. **Results Found**: Number of matches and locations
4. **Severity Assessment**: Critical/High/Medium/Low impact
5. **Fix Required**: Yes/No with justification

##### **Documentation Format**
```markdown
## Search Results: Hardcoded Localhost URLs

**Search Query**: `grep -r "localhost" --include="*.py" --include="*.ts" --include="*.js" --include="*.yaml" --include="*.yml" .`

**Files Searched**: All Python, TypeScript, JavaScript, YAML files

**Results Found**: 23 instances across 8 files

### Critical Issues (Fix Immediately):
1. `app/core/config.py:45` - DATABASE_URL hardcoded
2. `frontend_ux/lib/api.ts:12` - API base URL hardcoded

### Medium Issues (Fix Soon):
3. `docs/setup_instructions.md:156` - Documentation example
4. `docker-compose.yml:23` - Development configuration

### Low Issues (Monitor):
5. `tests/conftest.py:78` - Test configuration (acceptable)
```

---

## **📈 PHASE 2: CASCADING EFFECTS ANALYSIS**

### **MANDATORY CASCADING ANALYSIS PROCESS**

#### **Step 1: Impact Assessment Framework**
You MUST analyze potential cascading effects using this framework:

##### **Dependency Chain Analysis**
1. **Direct Dependencies**: Code that directly imports/uses the fixed component
2. **Indirect Dependencies**: Code that depends on components that depend on the fixed component
3. **Runtime Dependencies**: Services that call the fixed functionality at runtime
4. **Configuration Dependencies**: Settings that might be affected by the fix

##### **Service Integration Analysis**
1. **API Contracts**: Does the fix change request/response formats?
2. **Database Schemas**: Does the fix require schema changes?
3. **External Services**: Does the fix affect integrations (GCP, Anthropic, etc.)?
4. **Frontend Components**: Does the fix require frontend updates?

#### **Step 2: Technology-Specific Cascading Checks**

##### **Python/FastAPI Changes**
- [ ] **API endpoints**: Check all endpoints that might be affected
- [ ] **Pydantic models**: Verify schema compatibility
- [ ] **Database models**: Check ORM relationships
- [ ] **Background tasks**: Verify Celery task signatures
- [ ] **Middleware**: Check authentication/authorization logic
- [ ] **Dependencies**: Verify import statements and usage

##### **Google Cloud Services Changes**
- [ ] **Service accounts**: Check permission requirements
- [ ] **Secret Manager**: Verify secret access patterns
- [ ] **Cloud SQL**: Check database connection handling
- [ ] **Cloud Storage**: Verify file upload/download logic
- [ ] **Document AI/Vision**: Check processing pipeline compatibility
- [ ] **Workload Identity**: Verify authentication setup

##### **Frontend/TypeScript Changes**
- [ ] **API calls**: Check all fetch/axios calls to affected endpoints
- [ ] **State management**: Verify data flow and state updates
- [ ] **Component props**: Check component interfaces
- [ ] **Type definitions**: Verify TypeScript interfaces
- [ ] **Error handling**: Check error boundaries and user feedback

##### **Infrastructure Changes**
- [ ] **Docker images**: Check base image compatibility
- [ ] **Cloud Run services**: Verify resource requirements
- [ ] **Cloud Build**: Check build process dependencies
- [ ] **Networking**: Verify VPC connector and ingress rules
- [ ] **Environment variables**: Check configuration requirements

#### **Step 3: Runtime and Deployment Impact Analysis**

##### **Immediate Runtime Effects**
- [ ] **Service restarts required**: Will services need to restart?
- [ ] **Database migrations needed**: Are schema changes required?
- [ ] **Cache invalidation**: Does the fix require cache clearing?
- [ ] **Session handling**: Will active sessions be affected?
- [ ] **Background jobs**: Will running tasks be interrupted?

##### **Deployment Considerations**
- [ ] **Zero-downtime deployment possible**: Can this be deployed without downtime?
- [ ] **Rolling deployment strategy**: What deployment approach is needed?
- [ ] **Rollback plan**: How can this change be reverted if needed?
- [ ] **Monitoring requirements**: What metrics need monitoring during deployment?
- [ ] **Gradual rollout**: Should this be deployed incrementally?

---

## **🚨 CRITICAL RULES AND REQUIREMENTS**

### **MANDATORY Requirements**
1. **ALWAYS perform the search BEFORE committing** - Never commit a fix without searching
2. **DOCUMENT EVERY SEARCH** - Keep detailed records of what was searched and found
3. **FIX ALL INSTANCES** - Never fix just one occurrence of a pattern
4. **ANALYZE CASCADING EFFECTS** - Never assume a fix is isolated
5. **TEST ACROSS ALL AFFECTED SERVICES** - Verify the fix works end-to-end

### **Prohibited Actions**
- ❌ **"This is just a small fix"** - All fixes require full analysis
- ❌ **"I'll search later"** - Search must be done immediately
- ❌ **"This only affects one file"** - Always check for patterns across the codebase
- ❌ **"The tests pass, so it's fine"** - Testing is necessary but not sufficient
- ❌ **"I'll document it in the PR"** - Documentation must be in the code/commit history

---

## **🔍 SEARCH PATTERNS BY ERROR TYPE**

### **Environment Configuration Errors**
```bash
# Hardcoded localhost/127.0.0.1
grep -r "localhost\|127\.0\.0\.1" --include="*.py" --include="*.ts" --include="*.js" --include="*.yaml" --include="*.yml" --include="*.json" .

# Missing environment variable handling
grep -r "os\.getenv" --include="*.py" . | grep -v "os\.getenv.*,"

# Reserved Cloud Run variables
grep -r "PORT\|K_SERVICE\|K_REVISION" --include="*.py" --include="*.ts" --include="*.js" --include="*.yaml" --include="*.yml" .
```

### **Code Quality Issues**
```bash
# Generic exception handling
grep -r "except Exception\|except:" --include="*.py" .

# Console logging in production code
grep -r "console\.log\|console\.error\|console\.warn" --include="*.ts" --include="*.tsx" --include="*.js" --include="*.jsx" .

# Missing type hints (Python functions)
grep -rn "^def [a-zA-Z_][a-zA-Z0-9_]*(" --include="*.py" . | grep -v "self\|->" | head -20

# Wildcard imports
grep -r "from .* import \*\|import \*" --include="*.py" --include="*.ts" --include="*.js" .
```

### **Security Issues**
```bash
# Potential hardcoded credentials
grep -r "password\|secret\|key\|token" --include="*.py" --include="*.ts" --include="*.js" --include="*.env*" . | grep -i ".*=.*[a-zA-Z0-9]\+" | grep -v "import\|from\|#\|//"

# Insecure configurations
grep -r "debug.*=.*true\|DEBUG.*=.*True" --include="*.py" --include="*.ts" --include="*.js" --include="*.yaml" --include="*.yml" --include="*.json" .
```

### **Performance Issues**
```bash
# Blocking operations in async code
grep -r "requests\.get\|requests\.post" --include="*.py" . | grep -v "aiohttp\|httpx"

# Potential memory leaks
grep -r "global.*=\|\.append.*" --include="*.py" . | grep -A2 -B2 "def\|class"

# Inefficient database queries
grep -r "session\.query\|select" --include="*.py" . | grep -v "\.filter\|\.where\|\.join"
```

---

## **📋 IMPLEMENTATION WORKFLOW**

### **Step-by-Step Process**

#### **1. Fix Identification**
```
🔍 IDENTIFY: What specific error/problem is being fixed?
📝 DOCUMENT: Write down the exact error pattern and fix applied
```

#### **2. Comprehensive Search**
```
🔎 SEARCH: Run all relevant search patterns across the codebase
📊 ANALYZE: Categorize findings by severity and impact
📝 DOCUMENT: Record all search results and locations
```

#### **3. Cascading Analysis**
```
🔗 ANALYZE: Map out all potential cascading effects
⚡ ASSESS: Evaluate runtime and deployment impacts
📝 DOCUMENT: Create detailed impact assessment
```

#### **4. Fix Application**
```
🛠️ FIX: Apply fixes to all identified instances
✅ VERIFY: Ensure all fixes are consistent and correct
🧪 TEST: Test all affected functionality
```

#### **5. Validation and Documentation**
```
📋 VALIDATE: Verify no similar issues remain
📝 DOCUMENT: Update commit messages and PR descriptions
🚀 DEPLOY: Deploy with appropriate monitoring
```

---

## **💡 PRACTICAL EXAMPLES**

### **Example 1: Fixing Hardcoded Database URL**

#### **Fix Applied**
```python
# Fixed in app/core/config.py
DATABASE_URL: str = Field(..., env="DATABASE_URL")
```

#### **Required Search Process**
```bash
# Search for all hardcoded database URLs
grep -r "DATABASE_URL.*=" --include="*.py" --include="*.env*" --include="*.yaml" --include="*.yml" .

# Search for localhost database connections
grep -r "postgresql://.*localhost" --include="*.py" --include="*.env*" .

# Search for database host configurations
grep -r "DB_HOST\|db_host" --include="*.py" --include="*.env*" --include="*.yaml" --include="*.yml" .
```

#### **Cascading Effects Analysis**
- [ ] **Cloud SQL connection**: Verify Cloud Run has proper `--set-cloudsql-instances`
- [ ] **Secret Manager**: Check if password needs to be in secrets
- [ ] **Environment variables**: Ensure all services can access DATABASE_URL
- [ ] **Migration scripts**: Check if any scripts hardcode database URLs
- [ ] **Docker compose**: Verify local development still works

### **Example 2: Adding Type Hints to Function**

#### **Fix Applied**
```python
# Fixed function signature
def process_document(document_id: str, options: Optional[Dict[str, Any]] = None) -> ProcessingResult:
```

#### **Required Search Process**
```bash
# Find all similar functions without type hints
grep -rn "^def [a-zA-Z_][a-zA-Z0-9_]*(" --include="*.py" app/services/ | grep -v "->" | head -10

# Check for inconsistent parameter usage
grep -r "process_document" --include="*.py" . | grep -A2 -B2 "def\|call"
```

#### **Cascading Effects Analysis**
- [ ] **API endpoints**: Check if return types affect OpenAPI schema
- [ ] **Frontend calls**: Verify TypeScript interfaces match
- [ ] **Test files**: Update any test mocks with new signatures
- [ ] **Documentation**: Update API documentation examples

---

## **📊 SUCCESS CRITERIA**

A fix following this rule is successful when:

### **Search Completeness**
- [ ] **All relevant patterns searched** across entire codebase
- [ ] **Multiple search strategies used** (grep, file analysis, dependency checking)
- [ ] **Results documented** with severity assessment
- [ ] **No similar issues remain** unfixed

### **Cascading Analysis**
- [ ] **All dependent code identified** and analyzed
- [ ] **Runtime impacts assessed** and documented
- [ ] **Deployment strategy planned** and executed
- [ ] **Rollback procedures** documented

### **Quality Assurance**
- [ ] **All fixes applied consistently** across similar patterns
- [ ] **Comprehensive testing completed** (unit, integration, end-to-end)
- [ ] **Performance validated** after fixes
- [ ] **Security assessment** completed for security-related fixes

### **Documentation**
- [ ] **Search process documented** in commit messages
- [ ] **Cascading effects documented** in PR description
- [ ] **Future considerations noted** for related issues
- [ ] **Testing evidence provided** for all fixes

---

## **🚨 ENFORCEMENT AND COMPLIANCE**

### **Mandatory Compliance**
- **ALL fixes require this analysis** - no exceptions
- **Search results must be documented** in commit history
- **Cascading effects must be assessed** before deployment
- **Multiple team members should review** complex fixes

### **Audit Trail Requirements**
Every fix must include in the commit message/PR:
```
🔍 CODEBASE SEARCH COMPLETED
- Searched patterns: [list patterns]
- Instances found: [number] across [number] files
- All instances fixed: Yes/No
- Cascading effects analyzed: Yes/No
- Testing completed: Yes/No
```

### **Failure Consequences**
- **Build rejection**: Fixes without proper analysis will fail CI/CD
- **Code review rejection**: PRs missing search documentation will be rejected
- **Rollback required**: Incomplete fixes will be rolled back
- **Process improvement**: Repeated issues trigger process reviews

---

## **🎯 CONCLUSION**

This rule ensures that **EVERY fix is comprehensive, safe, and sustainable**. By requiring systematic codebase searches and cascading effects analysis, we prevent the "whack-a-mole" problem where fixing one instance leaves similar issues elsewhere, and we avoid introducing new problems through unintended side effects.

**Quality is not accidental - it's mandatory. Every fix must be complete and safe.**

---

**Rule Version**: 1.0
**Effective Date**: $(date)
**Review Cycle**: Monthly
**Enforcement**: Mandatory for all fixes
