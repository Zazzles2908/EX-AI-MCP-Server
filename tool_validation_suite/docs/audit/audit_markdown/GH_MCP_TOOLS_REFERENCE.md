# GH-MCP TOOLS COMPLETE REFERENCE
## All Available GitHub MCP Tools and Their Usage

**Date:** 2025-10-07  
**Purpose:** Complete documentation of gh-mcp tools for proper usage

---

## AVAILABLE GH-MCP TOOLS

### 1. **gh_api_gh-mcp**
**Purpose:** Call GitHub API directly  
**Parameters:**
- `path` (required): API endpoint path
- `method`: HTTP method (GET, POST, etc.)
- `body`: Request body
- `query`: Query parameters
- `headers`: Custom headers

**Example:**
```json
{
  "path": "/repos/Zazzles2908/EX-AI-MCP-Server/branches",
  "method": "GET"
}
```

---

### 2. **gh_branch_checkout_gh-mcp**
**Purpose:** Create or switch to a branch  
**Parameters:**
- `branch` (required): Branch name
- `base`: Base branch (default: main)
- `createIfMissing`: Create if doesn't exist (default: true)
- `path`: Repository path
- `trackRemote`: Track remote branch

**Example:**
```json
{
  "branch": "feature/new-feature",
  "base": "main",
  "path": "c:\\Project\\EX-AI-MCP-Server"
}
```

---

### 3. **gh_branch_delete_gh-mcp**
**Purpose:** Delete a branch locally and optionally remotely  
**Parameters:**
- `branch` (required): Branch name to delete
- `deleteRemote`: Also delete from remote (default: false)
- `force`: Force delete (default: false)
- `remote`: Remote name (default: origin)
- `path`: Repository path

**Example:**
```json
{
  "branch": "feature/old-feature",
  "deleteRemote": true,
  "force": false,
  "path": "c:\\Project\\EX-AI-MCP-Server"
}
```

**⚠️ CRITICAL:** This is the tool I should use for branch deletion!

---

### 4. **gh_branch_rebase_onto_main_gh-mcp**
**Purpose:** Rebase a branch on top of main  
**Parameters:**
- `branch`: Branch to rebase (default: current)
- `mainBranch`: Main branch name (default: main)
- `abort`: Abort in-progress rebase
- `path`: Repository path

**Example:**
```json
{
  "branch": "feature/my-feature",
  "path": "c:\\Project\\EX-AI-MCP-Server"
}
```

---

### 5. **gh_auth_status_gh-mcp**
**Purpose:** Check GitHub authentication status  
**Parameters:** None

**Example:**
```json
{}
```

**Output:** Authentication status text

---

### 6. **gh_user_gh-mcp**
**Purpose:** Get current GitHub user identity  
**Parameters:** None

**Example:**
```json
{}
```

**Output:** `{"login": "Zazzles2908", "id": 202350989}`

---

### 7. **gh_branch_status_gh-mcp**
**Purpose:** Report current branch, SHAs, local/remote branches  
**Parameters:**
- `fetch`: Fetch from remote first (default: false)
- `path`: Repository path

**Example:**
```json
{
  "fetch": true,
  "path": "c:\\Project\\EX-AI-MCP-Server"
}
```

**Output:** Current branch, ahead/behind counts, dirty state, branch lists

---

### 8. **gh_branch_pull_gh-mcp**
**Purpose:** Checkout main and fast-forward pull from remote  
**Parameters:**
- `branch`: Branch to pull (default: main)
- `remote`: Remote name (default: origin)
- `path`: Repository path

**Example:**
```json
{
  "branch": "main",
  "path": "c:\\Project\\EX-AI-MCP-Server"
}
```

---

### 9. **gh_branch_push_gh-mcp**
**Purpose:** Stage, commit, push, and verify SHAs  
**Parameters:**
- `message`: Commit message (optional, will commit if provided)
- `branch`: Branch to push (default: current)
- `remote`: Remote name (default: origin)
- `path`: Repository path

**Example:**
```json
{
  "message": "feat: Add new feature",
  "path": "c:\\Project\\EX-AI-MCP-Server"
}
```

**✅ USED:** This is what I used for commits

---

### 10. **gh_branch_sync_local_gh-mcp**
**Purpose:** Fetch, stash if dirty, pull, reapply stash  
**Parameters:**
- `remote`: Remote name (default: origin)
- `path`: Repository path

**Example:**
```json
{
  "path": "c:\\Project\\EX-AI-MCP-Server"
}
```

---

### 11. **gh_branch_merge_to_main_gh-mcp**
**Purpose:** Switch to main, pull, merge branch, push, optionally delete  
**Parameters:**
- `branch` (required): Branch to merge
- `deleteBranch`: Delete after merge (default: false)
- `dryRun`: Test without executing (default: false)
- `remote`: Remote name (default: origin)
- `path`: Repository path

**Example:**
```json
{
  "branch": "fix/test-suite-and-production-issues",
  "deleteBranch": false,
  "dryRun": true,
  "path": "c:\\Project\\EX-AI-MCP-Server"
}
```

**⚠️ CRITICAL:** This is the tool I should use for merging to main!

---

### 12. **gh_workflow_complete_gh-mcp**
**Purpose:** Auto-sync local, push current branch, merge to main  
**Parameters:**
- `branch`: Branch to complete (default: current)
- `deleteBranch`: Delete after merge (default: false)
- `dryRun`: Test without executing (default: false)
- `path`: Repository path

**Example:**
```json
{
  "deleteBranch": true,
  "dryRun": true,
  "path": "c:\\Project\\EX-AI-MCP-Server"
}
```

---

### 13. **gh_repo_list_gh-mcp**
**Purpose:** List repositories for current user or owner  
**Parameters:**
- `owner`: Owner name (optional)
- `type`: Repository type (all, owner, member)
- `page`: Page number
- `per_page`: Results per page

**Example:**
```json
{
  "owner": "Zazzles2908",
  "type": "owner"
}
```

---

### 14. **gh_pr_list_gh-mcp**
**Purpose:** List pull requests for a repository  
**Parameters:**
- `owner` (required): Repository owner
- `repo` (required): Repository name
- `state`: PR state (open, closed, all)
- `page`: Page number
- `per_page`: Results per page

**Example:**
```json
{
  "owner": "Zazzles2908",
  "repo": "EX-AI-MCP-Server",
  "state": "open"
}
```

---

### 15. **gh_issue_list_gh-mcp**
**Purpose:** List issues for a repository  
**Parameters:**
- `owner` (required): Repository owner
- `repo` (required): Repository name
- `state`: Issue state (open, closed, all)
- `labels`: Filter by labels
- `page`: Page number
- `per_page`: Results per page

**Example:**
```json
{
  "owner": "Zazzles2908",
  "repo": "EX-AI-MCP-Server",
  "state": "open"
}
```

---

### 16. **gh_repo_ensure_gh-mcp**
**Purpose:** Idempotently create/connect repo to GitHub and push  
**Parameters:**
- `owner` (required): Repository owner
- `repo` (required): Repository name
- `visibility`: public or private
- `autoInit`: Auto-initialize (default: false)
- `path`: Repository path

---

### 17. **gh_pre_push_check_gh-mcp**
**Purpose:** Pre-push safety check for secret files  
**Parameters:**
- `path`: Repository path

---

### 18. **gh_repo_protect_gh-mcp**
**Purpose:** Apply branch protection to repository  
**Parameters:**
- `owner` (required): Repository owner
- `repo` (required): Repository name
- `branch`: Branch to protect (default: main)
- `requireApprovals`: Number of approvals required
- `enforceAdmins`: Enforce for admins

---

## TOOLS I SHOULD HAVE USED

### For Branch Investigation
❌ **Should use:** `gh_api_gh-mcp` to get branch details  
❌ **Should use:** `gh_branch_status_gh-mcp` with fetch=true

### For Branch Deletion
❌ **Should use:** `gh_branch_delete_gh-mcp` instead of raw git commands

### For Merging to Main
❌ **Should use:** `gh_branch_merge_to_main_gh-mcp` with dryRun=true first

### For Branch Comparison
❌ **Should use:** `gh_api_gh-mcp` to compare branches via API

---

## CORRECTED WORKFLOW

### Phase 0.1: Branch Investigation (Using gh-mcp)

```json
// 1. Get branch status
{
  "tool": "gh_branch_status_gh-mcp",
  "params": {
    "fetch": true,
    "path": "c:\\Project\\EX-AI-MCP-Server"
  }
}

// 2. For each branch, get details via API
{
  "tool": "gh_api_gh-mcp",
  "params": {
    "path": "/repos/Zazzles2908/EX-AI-MCP-Server/branches/feature/cleanup-and-reorganization",
    "method": "GET"
  }
}

// 3. Compare branch with main
{
  "tool": "gh_api_gh-mcp",
  "params": {
    "path": "/repos/Zazzles2908/EX-AI-MCP-Server/compare/main...feature/cleanup-and-reorganization",
    "method": "GET"
  }
}
```

### Phase 0.4: Test Merge (Using gh-mcp)

```json
// Test merge with dry run
{
  "tool": "gh_branch_merge_to_main_gh-mcp",
  "params": {
    "branch": "fix/test-suite-and-production-issues",
    "dryRun": true,
    "deleteBranch": false,
    "path": "c:\\Project\\EX-AI-MCP-Server"
  }
}
```

---

**Status:** Complete reference documented  
**Next Action:** Use these tools for Phase 0 investigation  
**Confidence:** HIGH - Now understand all available tools

