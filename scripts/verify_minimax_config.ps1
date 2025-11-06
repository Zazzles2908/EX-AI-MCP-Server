# MiniMax M2 Configuration Verification Script
# Created: 2025-11-04
# Purpose: Verify Claude Code is properly configured to use MiniMax M2

param(
    [switch]$Verbose
)

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "MiniMax M2 Configuration Verification" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$ErrorCount = 0
$WarningCount = 0
$ProjectRoot = "C:\Project\EX-AI-MCP-Server"

# Function to write colored output
function Write-Status {
    param(
        [string]$Message,
        [string]$Status,
        [string]$Color = "White"
    )
    
    $StatusColor = switch ($Status) {
        "PASS" { "Green" }
        "FAIL" { "Red" }
        "WARN" { "Yellow" }
        "INFO" { "Cyan" }
        default { "White" }
    }
    
    Write-Host "[$Status] " -ForegroundColor $StatusColor -NoNewline
    Write-Host $Message -ForegroundColor $Color
}

# Check 1: Verify .claude/settings.local.json exists
Write-Host "`n1. Checking configuration file..." -ForegroundColor Yellow
$SettingsPath = Join-Path $ProjectRoot ".claude\settings.local.json"

if (Test-Path $SettingsPath) {
    Write-Status "Configuration file exists: $SettingsPath" "PASS"
} else {
    Write-Status "Configuration file NOT found: $SettingsPath" "FAIL" "Red"
    $ErrorCount++
}

# Check 2: Verify JSON is valid
Write-Host "`n2. Validating JSON syntax..." -ForegroundColor Yellow
try {
    $Config = Get-Content $SettingsPath -Raw | ConvertFrom-Json
    Write-Status "JSON syntax is valid" "PASS"
} catch {
    Write-Status "JSON syntax error: $($_.Exception.Message)" "FAIL" "Red"
    $ErrorCount++
    exit 1
}

# Check 3: Verify modelConfig section exists
Write-Host "`n3. Checking modelConfig section..." -ForegroundColor Yellow
if ($Config.modelConfig) {
    Write-Status "modelConfig section found" "PASS"
    
    # Check primary model
    if ($Config.modelConfig.primaryModel -eq "MiniMax-M2") {
        Write-Status "Primary model: MiniMax-M2" "PASS" "Green"
    } else {
        Write-Status "Primary model: $($Config.modelConfig.primaryModel) (Expected: MiniMax-M2)" "FAIL" "Red"
        $ErrorCount++
    }
    
    # Check fallback model
    if ($Config.modelConfig.fallbackModel -eq "MiniMax-M2") {
        Write-Status "Fallback model: MiniMax-M2" "PASS" "Green"
    } else {
        Write-Status "Fallback model: $($Config.modelConfig.fallbackModel) (Expected: MiniMax-M2)" "FAIL" "Red"
        $ErrorCount++
    }
    
    # Check model identifier
    if ($Config.modelConfig.model -eq "minimax-m2") {
        Write-Status "Model identifier: minimax-m2" "PASS" "Green"
    } else {
        Write-Status "Model identifier: $($Config.modelConfig.model) (Expected: minimax-m2)" "WARN" "Yellow"
        $WarningCount++
    }
} else {
    Write-Status "modelConfig section NOT found" "FAIL" "Red"
    $ErrorCount++
}

# Check 4: Verify environment variables configuration
Write-Host "`n4. Checking environment variables configuration..." -ForegroundColor Yellow
if ($Config.modelConfig.env) {
    Write-Status "Environment variables section found" "PASS"
    
    # Check ANTHROPIC_BASE_URL
    if ($Config.modelConfig.env.ANTHROPIC_BASE_URL -eq "https://api.minimax.io/anthropic") {
        Write-Status "ANTHROPIC_BASE_URL: https://api.minimax.io/anthropic" "PASS" "Green"
    } else {
        Write-Status "ANTHROPIC_BASE_URL: $($Config.modelConfig.env.ANTHROPIC_BASE_URL)" "WARN" "Yellow"
        $WarningCount++
    }
    
    # Check ANTHROPIC_AUTH_TOKEN
    if ($Config.modelConfig.env.ANTHROPIC_AUTH_TOKEN) {
        Write-Status "ANTHROPIC_AUTH_TOKEN: Configured" "PASS" "Green"
    } else {
        Write-Status "ANTHROPIC_AUTH_TOKEN: NOT configured" "FAIL" "Red"
        $ErrorCount++
    }
    
    # Check ANTHROPIC_MODEL
    if ($Config.modelConfig.env.ANTHROPIC_MODEL -eq "MiniMax-M2") {
        Write-Status "ANTHROPIC_MODEL: MiniMax-M2" "PASS" "Green"
    } else {
        Write-Status "ANTHROPIC_MODEL: $($Config.modelConfig.env.ANTHROPIC_MODEL)" "WARN" "Yellow"
        $WarningCount++
    }
} else {
    Write-Status "Environment variables section NOT found" "FAIL" "Red"
    $ErrorCount++
}

# Check 5: Verify model overrides
Write-Host "`n5. Checking model overrides..." -ForegroundColor Yellow
if ($Config.modelConfig.modelOverrides) {
    Write-Status "Model overrides section found" "PASS"
    
    $ExpectedOverrides = @{
        "claude-3-5-haiku-20241022" = "minimax-m2"
        "claude-3-5-sonnet-20241022" = "minimax-m2"
        "claude-3-opus-20240229" = "minimax-m2"
    }
    
    foreach ($key in $ExpectedOverrides.Keys) {
        if ($Config.modelConfig.modelOverrides.$key -eq $ExpectedOverrides[$key]) {
            Write-Status "$key -> $($ExpectedOverrides[$key])" "PASS" "Green"
        } else {
            Write-Status "$key -> $($Config.modelConfig.modelOverrides.$key) (Expected: $($ExpectedOverrides[$key]))" "WARN" "Yellow"
            $WarningCount++
        }
    }
} else {
    Write-Status "Model overrides section NOT found" "WARN" "Yellow"
    $WarningCount++
}

# Check 6: Verify environment variable is set
Write-Host "`n6. Checking runtime environment variables..." -ForegroundColor Yellow
if ($env:MINIMAX_API_KEY) {
    Write-Status "MINIMAX_API_KEY is set" "PASS" "Green"
    if ($Verbose) {
        Write-Status "Value: $($env:MINIMAX_API_KEY.Substring(0, [Math]::Min(10, $env:MINIMAX_API_KEY.Length)))..." "INFO" "Cyan"
    }
} else {
    Write-Status "MINIMAX_API_KEY is NOT set" "WARN" "Yellow"
    Write-Host "  Set with: `$env:MINIMAX_API_KEY = 'your-api-key-here'" -ForegroundColor Gray
    $WarningCount++
}

# Check 7: Verify .vscode/settings.json (optional)
Write-Host "`n7. Checking VS Code settings (optional)..." -ForegroundColor Yellow
$VSCodeSettingsPath = Join-Path $ProjectRoot ".vscode\settings.json"

if (Test-Path $VSCodeSettingsPath) {
    try {
        $VSCodeConfig = Get-Content $VSCodeSettingsPath -Raw | ConvertFrom-Json
        
        if ($VSCodeConfig.'claudeCode.selectedModel' -eq "MiniMax-M2") {
            Write-Status "VS Code selectedModel: MiniMax-M2" "PASS" "Green"
        } else {
            Write-Status "VS Code selectedModel: $($VSCodeConfig.'claudeCode.selectedModel')" "INFO" "Cyan"
        }
    } catch {
        Write-Status "Could not parse .vscode/settings.json" "WARN" "Yellow"
        $WarningCount++
    }
} else {
    Write-Status ".vscode/settings.json not found (optional)" "INFO" "Cyan"
}

# Summary
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Verification Summary" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

if ($ErrorCount -eq 0 -and $WarningCount -eq 0) {
    Write-Host "✅ All checks passed!" -ForegroundColor Green
    Write-Host "`nMiniMax M2 is properly configured." -ForegroundColor Green
    Write-Host "`nNext steps:" -ForegroundColor Cyan
    Write-Host "  1. Restart VS Code" -ForegroundColor White
    Write-Host "  2. Open integrated terminal (Ctrl + ``)" -ForegroundColor White
    Write-Host "  3. Test with: claudecode 'Hello, what model are you?'" -ForegroundColor White
} elseif ($ErrorCount -eq 0) {
    Write-Host "⚠️  Configuration complete with $WarningCount warning(s)" -ForegroundColor Yellow
    Write-Host "`nMiniMax M2 should work, but some optional settings are missing." -ForegroundColor Yellow
    Write-Host "`nRecommendation: Review warnings above and update configuration if needed." -ForegroundColor Cyan
} else {
    Write-Host "❌ Configuration has $ErrorCount error(s) and $WarningCount warning(s)" -ForegroundColor Red
    Write-Host "`nMiniMax M2 may NOT work correctly." -ForegroundColor Red
    Write-Host "`nAction required: Fix errors above before using MiniMax M2." -ForegroundColor Cyan
}

Write-Host "`n========================================`n" -ForegroundColor Cyan

# Exit with appropriate code
if ($ErrorCount -gt 0) {
    exit 1
} else {
    exit 0
}

