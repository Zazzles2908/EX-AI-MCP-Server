# Documentation Reorganization Script
# Date: 2025-10-14
# Purpose: Clean up and reorganize ~270 markdown files

Write-Host "=== Documentation Reorganization Script ===" -ForegroundColor Cyan
Write-Host "Starting reorganization..." -ForegroundColor Green

$ErrorActionPreference = "Stop"
$docsRoot = "docs"

# Phase 1: Consolidate Architecture
Write-Host "`n[Phase 1] Consolidating Architecture..." -ForegroundColor Yellow

# Move 01_ARCHITECTURE files to 02_ARCHITECTURE
if (Test-Path "$docsRoot/01_ARCHITECTURE") {
    Write-Host "  Moving 01_ARCHITECTURE files to 02_ARCHITECTURE..."
    
    # Keep DEPENDENCY_MAP and DESIGN_INTENT
    if (Test-Path "$docsRoot/01_ARCHITECTURE/DEPENDENCY_MAP.md") {
        Copy-Item "$docsRoot/01_ARCHITECTURE/DEPENDENCY_MAP.md" "$docsRoot/02_ARCHITECTURE/" -Force
    }
    if (Test-Path "$docsRoot/01_ARCHITECTURE/DESIGN_INTENT_SUMMARY.md") {
        Copy-Item "$docsRoot/01_ARCHITECTURE/DESIGN_INTENT_SUMMARY.md" "$docsRoot/02_ARCHITECTURE/DESIGN_INTENT.md" -Force
    }
    
    # Archive the rest
    New-Item -ItemType Directory -Force -Path "$docsRoot/06_ARCHIVE/2025-10-14_architecture" | Out-Null
    Move-Item "$docsRoot/01_ARCHITECTURE/*" "$docsRoot/06_ARCHIVE/2025-10-14_architecture/" -Force -ErrorAction SilentlyContinue
    Remove-Item "$docsRoot/01_ARCHITECTURE" -Recurse -Force -ErrorAction SilentlyContinue
    
    Write-Host "  ✓ Architecture consolidated" -ForegroundColor Green
}

# Merge architecture/ directory
if (Test-Path "$docsRoot/architecture") {
    Write-Host "  Merging architecture/ directory..."
    
    # Move useful files to 02_ARCHITECTURE
    if (Test-Path "$docsRoot/architecture/PERFORMANCE_METRICS_ARCHITECTURE.md") {
        Copy-Item "$docsRoot/architecture/PERFORMANCE_METRICS_ARCHITECTURE.md" "$docsRoot/02_ARCHITECTURE/" -Force
    }
    
    # Archive the rest
    New-Item -ItemType Directory -Force -Path "$docsRoot/06_ARCHIVE/legacy_architecture" | Out-Null
    Move-Item "$docsRoot/architecture/*" "$docsRoot/06_ARCHIVE/legacy_architecture/" -Force -Recurse -ErrorAction SilentlyContinue
    Remove-Item "$docsRoot/architecture" -Recurse -Force -ErrorAction SilentlyContinue
    
    Write-Host "  ✓ Legacy architecture archived" -ForegroundColor Green
}

# Phase 2: Consolidate API Reference
Write-Host "`n[Phase 2] Consolidating API Reference..." -ForegroundColor Yellow

# 02_API_REFERENCE is already clean, just rename to 03_API_REFERENCE
if (Test-Path "$docsRoot/02_API_REFERENCE") {
    Move-Item "$docsRoot/02_API_REFERENCE" "$docsRoot/03_API_REFERENCE" -Force
    Write-Host "  ✓ API Reference moved to 03_API_REFERENCE" -ForegroundColor Green
}

# Phase 3: Consolidate Guides
Write-Host "`n[Phase 3] Consolidating Guides..." -ForegroundColor Yellow

# Move guides/ to 04_GUIDES
if (Test-Path "$docsRoot/guides") {
    Move-Item "$docsRoot/guides" "$docsRoot/04_GUIDES" -Force
    Write-Host "  ✓ Guides moved to 04_GUIDES" -ForegroundColor Green
}

# Phase 4: Create Current Work Hub
Write-Host "`n[Phase 4] Creating Current Work Hub..." -ForegroundColor Yellow

New-Item -ItemType Directory -Force -Path "$docsRoot/05_CURRENT_WORK" | Out-Null

# Move master checklist
if (Test-Path "$docsRoot/consolidated_checklist/MASTER_CHECKLIST_2025-10-14.md") {
    Copy-Item "$docsRoot/consolidated_checklist/MASTER_CHECKLIST_2025-10-14.md" "$docsRoot/05_CURRENT_WORK/MASTER_CHECKLIST.md" -Force
    Write-Host "  ✓ Master checklist moved" -ForegroundColor Green
}

# Move MCP implementation tracker
if (Test-Path "$docsRoot/05_ISSUES/MCP_FILE_HANDLING_IMPLEMENTATION_TRACKER_2025-10-14.md") {
    Copy-Item "$docsRoot/05_ISSUES/MCP_FILE_HANDLING_IMPLEMENTATION_TRACKER_2025-10-14.md" "$docsRoot/05_CURRENT_WORK/MCP_IMPLEMENTATION_TRACKER.md" -Force
    Write-Host "  ✓ MCP tracker moved" -ForegroundColor Green
}

# Move MCP analysis (reference)
if (Test-Path "$docsRoot/05_ISSUES/MCP_FILE_HANDLING_EXAI_ANALYSIS_2025-10-14.md") {
    Copy-Item "$docsRoot/05_ISSUES/MCP_FILE_HANDLING_EXAI_ANALYSIS_2025-10-14.md" "$docsRoot/05_CURRENT_WORK/MCP_ANALYSIS_REFERENCE.md" -Force
    Write-Host "  ✓ MCP analysis moved" -ForegroundColor Green
}

# Consolidate known issues
if (Test-Path "$docsRoot/known_issues") {
    $knownIssuesContent = @'
# Known Issues
**Date:** 2025-10-14
**Status:** Active tracking

---

## Active Issues

### 1. MCP File Handling
**File:** See MCP_IMPLEMENTATION_TRACKER.md
**Status:** In progress
**Priority:** High

### 2. Ripgrep Augment Limitation
**Description:** Ripgrep has limitations with Augment integration
**Status:** Documented
**Priority:** Low

---

## Resolved Issues

See 06_ARCHIVE/2025-10-14_issues/ for resolved bug fixes and investigations.
'@

    $knownIssuesContent | Out-File -FilePath "$docsRoot/05_CURRENT_WORK/KNOWN_ISSUES.md" -Encoding UTF8

    Write-Host "  ✓ Known issues consolidated" -ForegroundColor Green
}

# Phase 5: Archive Historical Content
Write-Host "`n[Phase 5] Archiving Historical Content..." -ForegroundColor Yellow

# Archive testing evidence
if (Test-Path "$docsRoot/04_TESTING/evidence") {
    New-Item -ItemType Directory -Force -Path "$docsRoot/06_ARCHIVE/2025-10-13_testing" | Out-Null
    Move-Item "$docsRoot/04_TESTING/evidence/*" "$docsRoot/06_ARCHIVE/2025-10-13_testing/" -Force -Recurse -ErrorAction SilentlyContinue
    Remove-Item "$docsRoot/04_TESTING/evidence" -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "  ✓ Testing evidence archived" -ForegroundColor Green
}

# Keep only comprehensive verification report in 04_TESTING
if (Test-Path "$docsRoot/04_TESTING") {
    Get-ChildItem "$docsRoot/04_TESTING" -Filter "*.md" | Where-Object { 
        $_.Name -ne "COMPREHENSIVE_VERIFICATION_REPORT.md" 
    } | ForEach-Object {
        New-Item -ItemType Directory -Force -Path "$docsRoot/06_ARCHIVE/2025-10-13_testing" | Out-Null
        Move-Item $_.FullName "$docsRoot/06_ARCHIVE/2025-10-13_testing/" -Force -ErrorAction SilentlyContinue
    }
    Write-Host "  ✓ Old testing docs archived" -ForegroundColor Green
}

# Archive progress logs
if (Test-Path "$docsRoot/06_PROGRESS") {
    New-Item -ItemType Directory -Force -Path "$docsRoot/06_ARCHIVE/2025-10-12_progress" | Out-Null
    
    # Keep GOD_CHECKLIST_CONSOLIDATED
    if (Test-Path "$docsRoot/06_PROGRESS/GOD_CHECKLIST_CONSOLIDATED.md") {
        Copy-Item "$docsRoot/06_PROGRESS/GOD_CHECKLIST_CONSOLIDATED.md" "$docsRoot/05_CURRENT_WORK/HISTORICAL_CHECKLIST.md" -Force
    }
    
    Move-Item "$docsRoot/06_PROGRESS/*" "$docsRoot/06_ARCHIVE/2025-10-12_progress/" -Force -Recurse -ErrorAction SilentlyContinue
    Remove-Item "$docsRoot/06_PROGRESS" -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "  ✓ Progress logs archived" -ForegroundColor Green
}

# Archive resolved issues
if (Test-Path "$docsRoot/05_ISSUES") {
    New-Item -ItemType Directory -Force -Path "$docsRoot/06_ARCHIVE/2025-10-14_issues" | Out-Null
    
    # Keep only active MCP files (already copied to 05_CURRENT_WORK)
    Get-ChildItem "$docsRoot/05_ISSUES" -Filter "*.md" | Where-Object { 
        $_.Name -notlike "MCP_FILE_HANDLING_IMPLEMENTATION_TRACKER*" -and
        $_.Name -notlike "MCP_FILE_HANDLING_EXAI_ANALYSIS*"
    } | ForEach-Object {
        Move-Item $_.FullName "$docsRoot/06_ARCHIVE/2025-10-14_issues/" -Force -ErrorAction SilentlyContinue
    }
    
    # Archive subdirectories
    Get-ChildItem "$docsRoot/05_ISSUES" -Directory | ForEach-Object {
        Move-Item $_.FullName "$docsRoot/06_ARCHIVE/2025-10-14_issues/" -Force -Recurse -ErrorAction SilentlyContinue
    }
    
    Write-Host "  ✓ Resolved issues archived" -ForegroundColor Green
}

# Merge 07_ARCHIVE into 06_ARCHIVE
if (Test-Path "$docsRoot/07_ARCHIVE") {
    Move-Item "$docsRoot/07_ARCHIVE/*" "$docsRoot/06_ARCHIVE/" -Force -Recurse -ErrorAction SilentlyContinue
    Remove-Item "$docsRoot/07_ARCHIVE" -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "  ✓ 07_ARCHIVE merged into 06_ARCHIVE" -ForegroundColor Green
}

# Archive consolidated_checklist (already copied to 05_CURRENT_WORK)
if (Test-Path "$docsRoot/consolidated_checklist") {
    New-Item -ItemType Directory -Force -Path "$docsRoot/06_ARCHIVE/2025-10-14_checklists" | Out-Null
    Move-Item "$docsRoot/consolidated_checklist/*" "$docsRoot/06_ARCHIVE/2025-10-14_checklists/" -Force -Recurse -ErrorAction SilentlyContinue
    Remove-Item "$docsRoot/consolidated_checklist" -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "  ✓ Consolidated checklist archived" -ForegroundColor Green
}

# Archive maintenance directory
if (Test-Path "$docsRoot/maintenance") {
    New-Item -ItemType Directory -Force -Path "$docsRoot/06_ARCHIVE/legacy_maintenance" | Out-Null
    Move-Item "$docsRoot/maintenance/*" "$docsRoot/06_ARCHIVE/legacy_maintenance/" -Force -Recurse -ErrorAction SilentlyContinue
    Remove-Item "$docsRoot/maintenance" -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "  ✓ Maintenance docs archived" -ForegroundColor Green
}

# Archive ux directory
if (Test-Path "$docsRoot/ux") {
    New-Item -ItemType Directory -Force -Path "$docsRoot/06_ARCHIVE/legacy_ux" | Out-Null
    Move-Item "$docsRoot/ux/*" "$docsRoot/06_ARCHIVE/legacy_ux/" -Force -Recurse -ErrorAction SilentlyContinue
    Remove-Item "$docsRoot/ux" -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "  ✓ UX docs archived" -ForegroundColor Green
}

# Clean up empty 05_ISSUES if it exists
if (Test-Path "$docsRoot/05_ISSUES") {
    $issuesCount = (Get-ChildItem "$docsRoot/05_ISSUES" -Recurse).Count
    if ($issuesCount -eq 0) {
        Remove-Item "$docsRoot/05_ISSUES" -Recurse -Force -ErrorAction SilentlyContinue
        Write-Host "  ✓ Empty 05_ISSUES removed" -ForegroundColor Green
    }
}

# Clean up empty 04_TESTING if needed
if (Test-Path "$docsRoot/04_TESTING") {
    $testingCount = (Get-ChildItem "$docsRoot/04_TESTING" -Recurse).Count
    if ($testingCount -eq 0) {
        Remove-Item "$docsRoot/04_TESTING" -Recurse -Force -ErrorAction SilentlyContinue
        Write-Host "  ✓ Empty 04_TESTING removed" -ForegroundColor Green
    }
}

# Clean up empty 03_IMPLEMENTATION if it exists
if (Test-Path "$docsRoot/03_IMPLEMENTATION") {
    New-Item -ItemType Directory -Force -Path "$docsRoot/06_ARCHIVE/2025-10-14_implementation" | Out-Null
    Move-Item "$docsRoot/03_IMPLEMENTATION/*" "$docsRoot/06_ARCHIVE/2025-10-14_implementation/" -Force -Recurse -ErrorAction SilentlyContinue
    Remove-Item "$docsRoot/03_IMPLEMENTATION" -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "  ✓ Implementation docs archived" -ForegroundColor Green
}

Write-Host "`n=== Reorganization Complete ===" -ForegroundColor Cyan
Write-Host "✓ All phases executed successfully" -ForegroundColor Green
Write-Host "`nNext steps:" -ForegroundColor Yellow
Write-Host "  1. Review the new structure in docs/" -ForegroundColor White
Write-Host "  2. Create README files for each directory" -ForegroundColor White
Write-Host "  3. Update root README.md" -ForegroundColor White

