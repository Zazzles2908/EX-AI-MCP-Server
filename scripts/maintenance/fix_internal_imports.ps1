# Fix internal imports within reorganized utils folders
# This script updates relative imports within moved files

Write-Output "Fixing internal imports in reorganized utils folders..."

# Define internal import replacements
$internalReplacements = @{
    # utils/file/ internal imports
    '\.file_utils_security' = '.security'
    '\.file_utils_reading' = '.reading'
    '\.file_utils_helpers' = '.helpers'
    '\.file_utils_json' = '.json'
    '\.file_utils_expansion' = '.expansion'
    '\.file_utils_tokens' = '.tokens'
    '\.file_cache' = '.cache'
    '\.file_types' = '.types'

    # Cross-folder imports (file -> config)
    '\.security_config' = 'utils.config.security'
    '\.config_helpers' = 'utils.config.helpers'

    # Cross-folder imports (file -> model)
    '\.token_utils' = 'utils.model.token_utils'

    # utils/conversation/ internal imports
    '\.conversation_memory' = '.memory'
    '\.conversation_history' = '.history'
    '\.conversation_models' = '.models'
    '\.conversation_threads' = '.threads'

    # utils/model/ internal imports
    '\.model_context' = '.context'
    '\.model_restrictions' = '.restrictions'
    '\.token_estimator' = '.token_estimator'
}

# Get all Python files in utils subfolders
$folders = @('utils/file', 'utils/conversation', 'utils/model', 'utils/config', 'utils/progress', 'utils/infrastructure')
$totalFiles = 0
$totalReplacements = 0

foreach ($folder in $folders) {
    $files = Get-ChildItem -Path $folder -Include "*.py" -Recurse -Exclude "__init__.py"
    
    foreach ($file in $files) {
        $content = Get-Content $file.FullName -Raw
        $originalContent = $content
        $fileReplacements = 0
        
        foreach ($pattern in $internalReplacements.Keys) {
            $replacement = $internalReplacements[$pattern]
            if ($content -match $pattern) {
                $content = $content -replace $pattern, $replacement
                $fileReplacements++
            }
        }
        
        if ($content -ne $originalContent) {
            Set-Content -Path $file.FullName -Value $content -NoNewline
            $totalFiles++
            $totalReplacements += $fileReplacements
            Write-Output "Updated: $($file.FullName) ($fileReplacements replacements)"
        }
    }
}

Write-Output ""
Write-Output "Summary:"
Write-Output "  Files updated: $totalFiles"
Write-Output "  Total replacements: $totalReplacements"
Write-Output ""
Write-Output "Internal import fixes complete!"

