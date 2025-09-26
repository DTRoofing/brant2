# 🔍 Comprehensive Error Fixing Rule

## **RULE: Always Search for Similar Errors When Fixing Issues**

### **📋 MANDATORY PROCESS**

When fixing any error, you MUST:

1. **Identify the error pattern** (e.g., `PORT=8080`, `console.log`, `except:`)
2. **Search the entire codebase** for similar patterns
3. **Fix ALL instances** found, not just the one reported
4. **Document the search scope** and results
5. **Verify no similar issues remain**

### **🔍 SEARCH STRATEGIES**

#### **For Environment Variables:**
```bash
# Search for hardcoded values
grep -r "VARIABLE_NAME=value" .
grep -r "VARIABLE_NAME.*=.*value" .

# Search for reserved variables
grep -r "PORT.*=" .
grep -r "K_SERVICE.*=" .
grep -r "K_REVISION.*=" .
```

#### **For Code Patterns:**
```bash
# Search for specific patterns
grep -r "pattern" .
grep -r "anti-pattern" .
grep -r "problematic_code" .
```

#### **For Configuration Files:**
```bash
# Search all config files
find . -name "*.yaml" -o -name "*.yml" -o -name "*.json" | xargs grep -l "pattern"
find . -name "Dockerfile*" | xargs grep -l "pattern"
find . -name "docker-compose*" | xargs grep -l "pattern"
```

### **📊 SEARCH SCOPE CHECKLIST**

When fixing an error, search these areas:

- [ ] **Configuration Files**: `*.yaml`, `*.yml`, `*.json`, `*.toml`
- [ ] **Docker Files**: `Dockerfile*`, `docker-compose*`
- [ ] **Application Code**: `app/`, `frontend_ux/`, `tests/`
- [ ] **Scripts**: `*.py`, `*.sh`, `*.bat`, `*.ps1`
- [ ] **Documentation**: `docs/`, `*.md`
- [ ] **Deployment**: `deployment/`, `cloudbuild.yaml`

### **🎯 COMMON ERROR PATTERNS TO SEARCH**

#### **Environment Variables:**
- `PORT=8080` → Search for all hardcoded ports
- `localhost` → Search for all localhost references
- `127.0.0.1` → Search for all IP references
- Reserved Cloud Run variables: `PORT`, `K_SERVICE`, `K_REVISION`

#### **Code Quality:**
- `console.log` → Search for all console statements
- `except:` → Search for all empty exception handlers
- `except Exception as e:` → Search for all generic exception handling
- `import *` → Search for all wildcard imports

#### **Security Issues:**
- `password=password` → Search for hardcoded credentials
- `secret=secret` → Search for hardcoded secrets
- `key=key` → Search for hardcoded keys

### **📝 DOCUMENTATION REQUIREMENTS**

For each error fix, document:

1. **Error Pattern**: What was the specific error?
2. **Search Query**: What search terms were used?
3. **Files Searched**: Which directories/file types were checked?
4. **Instances Found**: How many similar issues were found?
5. **Fixes Applied**: What fixes were applied to each instance?
6. **Verification**: How was the fix verified?

### **🚨 CRITICAL RULES**

1. **NEVER fix just one instance** - always search for similar patterns
2. **ALWAYS document the search process** - show your work
3. **VERIFY the fix is complete** - ensure no similar issues remain
4. **USE multiple search strategies** - don't rely on just one search method
5. **CHECK all file types** - errors can appear in any file type

### **💡 EXAMPLES**

#### **Example 1: Fixing PORT Environment Variable**
```bash
# 1. Identify the error
ERROR: reserved env names were provided: PORT

# 2. Search for all PORT settings
grep -r "PORT.*=" .
grep -r "--set-env-vars.*PORT" .

# 3. Check all config files
find . -name "*.yaml" -o -name "*.yml" | xargs grep -l "PORT"

# 4. Fix all instances found
# 5. Document the search and fixes
```

#### **Example 2: Fixing Console Logging**
```bash
# 1. Identify the error
console.log statements in production code

# 2. Search for all console statements
grep -r "console\." frontend_ux/
grep -r "console\." app/

# 3. Check all JavaScript/TypeScript files
find . -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.jsx" | xargs grep -l "console\."

# 4. Fix all instances found
# 5. Document the search and fixes
```

### **✅ SUCCESS CRITERIA**

A comprehensive error fix is successful when:

- [ ] **All similar patterns found** and fixed
- [ ] **Search process documented** with queries and results
- [ ] **No similar issues remain** in the codebase
- [ ] **Fix verified** through testing or additional searches
- [ ] **Documentation updated** to reflect the changes

### **🔄 IMPLEMENTATION**

This rule is now **MANDATORY** for all error fixes. Every time an error is fixed, the assistant must:

1. **Acknowledge the rule** ("Following comprehensive error fixing rule...")
2. **Perform the search** using multiple strategies
3. **Document the process** with search queries and results
4. **Fix all instances** found
5. **Verify completeness** of the fix

This ensures that similar errors don't persist elsewhere in the codebase and prevents the "whack-a-mole" problem of fixing the same error multiple times.

---

## **🔄 CASCADING EFFECTS ANALYSIS RULE**

### **RULE: Always Analyze Cascading Effects of Any Fix**

When fixing any error, you MUST also analyze and address potential cascading effects:

### **📋 MANDATORY CASCADING ANALYSIS**

#### **1. Dependency & Service Analysis**
- **Check for existing implementations** under different names
- **Verify naming conventions** follow project standards
- **Ensure architectural consistency** with existing patterns
- **Validate import/export patterns** match project structure

#### **2. Reference Tracking**
- **Find all references** to the fixed component
- **Check for hardcoded references** that might break
- **Verify configuration updates** are complete
- **Ensure documentation** reflects changes

#### **3. Technology Best Practices**
- **Validate against framework conventions** (FastAPI, Next.js, etc.)
- **Check security implications** of the fix
- **Ensure performance considerations** are addressed
- **Verify compatibility** with existing dependencies

### **🔍 CASCADING ANALYSIS CHECKLIST**

#### **For Missing Dependencies/Services:**
- [ ] **Search for similar functionality** under different names
- [ ] **Check if functionality exists** in a different module
- [ ] **Verify naming follows** project conventions
- [ ] **Ensure proper imports/exports** are in place
- [ ] **Check configuration files** for references
- [ ] **Validate against framework patterns**

#### **For Code Changes:**
- [ ] **Find all callers** of modified functions/classes
- [ ] **Check for hardcoded references** that might break
- [ ] **Verify interface compatibility** is maintained
- [ ] **Ensure error handling** is consistent
- [ ] **Check tests** that might need updates

#### **For Configuration Changes:**
- [ ] **Find all references** to changed config values
- [ ] **Check environment files** for consistency
- [ ] **Verify deployment scripts** are updated
- [ ] **Ensure documentation** reflects changes
- [ ] **Check for hardcoded values** elsewhere

### **🎯 COMMON CASCADING PATTERNS**

#### **Dependency Issues:**
```bash
# When fixing missing dependency, check:
grep -r "similar_function_name" .
grep -r "import.*dependency" .
grep -r "from.*dependency" .
find . -name "*.py" | xargs grep -l "dependency"
```

#### **Service/Module Issues:**
```bash
# When fixing missing service, check:
grep -r "service_name" .
grep -r "ServiceName" .
grep -r "SERVICE_NAME" .
find . -name "*.py" | xargs grep -l "service"
```

#### **Configuration Issues:**
```bash
# When fixing config, check:
grep -r "CONFIG_NAME" .
grep -r "config_name" .
find . -name "*.env*" | xargs grep -l "config"
find . -name "*.yaml" -o -name "*.yml" | xargs grep -l "config"
```

### **📊 TECHNOLOGY-SPECIFIC CHECKS**

#### **Python/FastAPI:**
- [ ] **Import statements** follow PEP 8 conventions
- [ ] **Module structure** follows FastAPI patterns
- [ ] **Dependency injection** is properly configured
- [ ] **Error handling** uses FastAPI exceptions
- [ ] **Type hints** are consistent

#### **TypeScript/Next.js:**
- [ ] **Import/export** follows ES6 modules
- [ ] **Component structure** follows React patterns
- [ ] **API routes** follow Next.js conventions
- [ ] **Type definitions** are consistent
- [ ] **Environment variables** use NEXT_PUBLIC_ prefix

#### **Docker/Deployment:**
- [ ] **Dockerfile** follows multi-stage build patterns
- [ ] **Environment variables** are properly set
- [ ] **Health checks** are configured
- [ ] **Security** best practices are followed
- [ ] **Resource limits** are appropriate

### **🚨 CRITICAL CASCADING RULES**

1. **NEVER assume** a fix is isolated - always check for cascading effects
2. **ALWAYS search** for existing similar functionality before creating new
3. **VERIFY naming conventions** match project standards
4. **CHECK all references** to modified components
5. **ENSURE architectural consistency** with existing patterns
6. **VALIDATE against technology best practices**

### **💡 CASCADING ANALYSIS EXAMPLES**

#### **Example 1: Fixing Missing Service**
```bash
# 1. Fix the missing service
# 2. Search for existing similar services
grep -r "Service" app/services/
grep -r "service" app/
find app/ -name "*service*" -type f

# 3. Check for references
grep -r "MissingService" .
grep -r "missing_service" .

# 4. Verify naming conventions
# 5. Check configuration files
# 6. Ensure proper imports/exports
```

#### **Example 2: Fixing Missing Dependency**
```bash
# 1. Fix the missing dependency
# 2. Search for existing similar dependencies
grep -r "dependency" .
find . -name "*dependency*" -type f

# 3. Check import statements
grep -r "import.*dependency" .
grep -r "from.*dependency" .

# 4. Verify configuration
grep -r "DEPENDENCY" .
find . -name "*.env*" | xargs grep -l "dependency"
```

### **✅ CASCADING ANALYSIS SUCCESS CRITERIA**

A cascading analysis is successful when:

- [ ] **All existing similar functionality identified** and evaluated
- [ ] **Naming conventions verified** against project standards
- [ ] **All references found** and updated if necessary
- [ ] **Architectural consistency maintained** with existing patterns
- [ ] **Technology best practices followed** for the framework
- [ ] **Configuration files updated** to reflect changes
- [ ] **Documentation updated** to reflect new patterns
- [ ] **No breaking changes introduced** to existing functionality

### **🔄 UPDATED IMPLEMENTATION**

The comprehensive error fixing process now includes:

1. **Acknowledge the rule** ("Following comprehensive error fixing rule...")
2. **Perform comprehensive search** for similar patterns
3. **Analyze cascading effects** of the fix
4. **Check for existing similar functionality** under different names
5. **Verify naming conventions** and architectural consistency
6. **Document the process** with search queries and results
7. **Fix ALL instances** found
8. **Verify completeness** of the fix and cascading effects

This ensures that fixes are not only complete but also architecturally sound and don't introduce cascading failures.
