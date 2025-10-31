# Phase 4: Update imports after directory moves
# Updates imports for: systemprompts -> src.prompts, streaming -> src.streaming

Write-Host "Updating imports after Phase 4 directory moves..."

# Define replacements
$replacements = @{
    'from systemprompts\.' = 'from src.prompts.'
    'from systemprompts import' = 'from src.prompts import'
    'import systemprompts\.' = 'import src.prompts.'
    'import systemprompts' = 'import src.prompts'
    'from streaming\.' = 'from src.streaming.'
    'from streaming import' = 'from src.streaming import'
    'import streaming\.' = 'import src.streaming.'
}

# Get all Python files (exclude __pycache__, .venv, archive)
$files = Get-ChildItem -Recurse -Include "*.py" -Exclude "*_BACKUP.py","*archive*" | Where-Object { 
    $_.FullName -notlike "*\archive\*" -and 
    $_.FullName -notlike "*\__pycache__\*" -and
    $_.FullName -notlike "*\.venv\*"
}

$totalFiles = 0
$totalReplacements = 0

foreach ($file in $files) {
    $content = Get-Content $file.FullName -Raw
    $originalContent = $content
    $fileReplacements = 0
    
    foreach ($pattern in $replacements.Keys) {
        $replacement = $replacements[$pattern]
        if ($content -match $pattern) {
            $content = $content -replace $pattern, $replacement
            $fileReplacements++
        }
    }
    
    if ($content -ne $originalContent) {
        Set-Content -Path $file.FullName -Value $content -NoNewline
        $totalFiles++
        $totalReplacements += $fileReplacements
        Write-Host "Updated: $($file.Name) ($fileReplacements replacements)"
    }
}

Write-Host ""
Write-Host "Summary:"
Write-Host "  Files updated: $totalFiles"
Write-Host "  Total replacements: $totalReplacements"
Write-Host ""
Write-Host "Import updates complete!"

