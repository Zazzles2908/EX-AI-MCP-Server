<#
.SYNOPSIS
    Get Docker logs with proper UTF-8 encoding (fixes null byte issue)

.DESCRIPTION
    PowerShell's default output encoding is UTF-16LE which creates files with null bytes
    between characters, making them unreadable by AI models. This script forces UTF-8 encoding.

.PARAMETER ContainerName
    Docker container name (default: exai-mcp-daemon)

.PARAMETER TailLines
    Number of recent log lines to retrieve (default: 1000)

.PARAMETER OutputFile
    Output file path (default: docker_logs.txt in current directory)

.PARAMETER Follow
    Follow log output (like tail -f)

.EXAMPLE
    .\get_docker_logs.ps1
    Get last 1000 lines from exai-mcp-daemon

.EXAMPLE
    .\get_docker_logs.ps1 -TailLines 500 -OutputFile logs_500.txt
    Get last 500 lines to custom file

.EXAMPLE
    .\get_docker_logs.ps1 -Follow
    Follow logs in real-time (Ctrl+C to stop)

.NOTES
    Created: 2025-11-02
    Issue: PowerShell UTF-16 encoding creates unreadable files with null bytes
    Fix: Force UTF-8 encoding for AI model compatibility
#>

param(
    [Parameter(Mandatory=$false)]
    [string]$ContainerName = "exai-mcp-daemon",
    
    [Parameter(Mandatory=$false)]
    [int]$TailLines = 1000,
    
    [Parameter(Mandatory=$false)]
    [string]$OutputFile = "docker_logs.txt",
    
    [Parameter(Mandatory=$false)]
    [switch]$Follow
)

# Ensure we're in the project directory
$ProjectRoot = "c:\Project\EX-AI-MCP-Server"
if (Test-Path $ProjectRoot) {
    Set-Location $ProjectRoot
}

Write-Host "🐳 Getting Docker logs from container: $ContainerName" -ForegroundColor Cyan

try {
    if ($Follow) {
        # Follow mode - stream logs to console (no file output)
        Write-Host "📡 Following logs (Ctrl+C to stop)..." -ForegroundColor Yellow
        docker logs $ContainerName --follow
    } else {
        # Get logs and save to file with UTF-8 encoding
        Write-Host "📝 Retrieving last $TailLines lines..." -ForegroundColor Yellow
        
        # Use Out-File with explicit UTF-8 encoding (no BOM)
        docker logs $ContainerName --tail $TailLines 2>&1 | Out-File -FilePath $OutputFile -Encoding UTF8
        
        # Verify file was created
        if (Test-Path $OutputFile) {
            $FileSize = (Get-Item $OutputFile).Length
            $FileSizeKB = [math]::Round($FileSize / 1KB, 2)
            
            Write-Host "✅ Logs saved successfully!" -ForegroundColor Green
            Write-Host "   File: $OutputFile" -ForegroundColor White
            Write-Host "   Size: $FileSizeKB KB" -ForegroundColor White
            Write-Host "   Encoding: UTF-8 (AI-readable)" -ForegroundColor Green
            
            # Show first few lines as preview
            Write-Host "`n📄 Preview (first 5 lines):" -ForegroundColor Cyan
            Get-Content $OutputFile -TotalCount 5 | ForEach-Object { Write-Host "   $_" -ForegroundColor Gray }
        } else {
            Write-Host "❌ Failed to create log file" -ForegroundColor Red
            exit 1
        }
    }
} catch {
    Write-Host "❌ Error: $_" -ForegroundColor Red
    Write-Host "   Make sure Docker is running and container exists" -ForegroundColor Yellow
    exit 1
}

