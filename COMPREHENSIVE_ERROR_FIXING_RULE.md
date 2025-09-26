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
