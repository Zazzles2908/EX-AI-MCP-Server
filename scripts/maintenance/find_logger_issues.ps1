# Find all Python files with logger usage issues
# This script identifies files that:
# 1. Use logger.debug/info/warning/error/exception but don't define logger
# 2. Use logging.getLogger(__name__) directly instead of centralized functions

$results = @()

# Directories to check
$directories = @(
    "src\providers",
    "src\daemon",
    "src\utils",
    "src\core",
    "src\bootstrap",
    "tools",
    "tools\workflows",
    "tools\workflow",
    "utils",
    "scripts"
)

foreach ($dir in $directories) {
    if (Test-Path $dir) {
        $files = Get-ChildItem -Path $dir -Filter "*.py" -Recurse -File
        
        foreach ($file in $files) {
            $content = Get-Content $file.FullName -Raw
            
            # Check if file uses logger methods
            $usesLogger = $content -match 'logger\.(debug|info|warning|error|exception|critical)'
            
            # Check if logger is defined
            $hasLoggerDef = $content -match 'logger\s*=\s*(logging\.getLogger|get_logger|get_async_safe_logger|get_unified_logger)'
            
            # Check if uses logging.getLogger directly
            $usesLoggingGetLogger = $content -match 'logger\s*=\s*logging\.getLogger'
            
            if ($usesLogger -and -not $hasLoggerDef) {
                $results += [PSCustomObject]@{
                    File = $file.FullName
                    Issue = "MISSING_LOGGER_DEFINITION"
                    Details = "Uses logger methods but logger is not defined"
                }
            }
            
            if ($usesLoggingGetLogger) {
                $results += [PSCustomObject]@{
                    File = $file.FullName
                    Issue = "USES_LOGGING_GETLOGGER_DIRECTLY"
                    Details = "Uses logging.getLogger() instead of centralized function"
                }
            }
        }
    }
}

# Output results
Write-Host "`n=== LOGGER ISSUES FOUND ===" -ForegroundColor Yellow
Write-Host "Total files with issues: $($results.Count)`n" -ForegroundColor Cyan

$results | Format-Table -AutoSize

# Group by issue type
Write-Host "`n=== SUMMARY BY ISSUE TYPE ===" -ForegroundColor Yellow
$results | Group-Object Issue | ForEach-Object {
    Write-Host "`n$($_.Name): $($_.Count) files" -ForegroundColor Cyan
    $_.Group | ForEach-Object {
        Write-Host "  - $($_.File)" -ForegroundColor Gray
    }
}

