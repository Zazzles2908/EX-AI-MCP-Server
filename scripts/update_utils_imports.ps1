# Update utils imports after reorganization (Phase 1.C.9)
# This script updates all imports from old flat structure to new folder structure

Write-Output "Updating utils imports across codebase..."

# Define replacements (old pattern -> new pattern)
$replacements = @{
    'from utils\.file_utils import' = 'from utils.file.operations import'
    'from utils\.file_utils_expansion import' = 'from utils.file.expansion import'
    'from utils\.file_utils_helpers import' = 'from utils.file.helpers import'
    'from utils\.file_utils_json import' = 'from utils.file.json import'
    'from utils\.file_utils_reading import' = 'from utils.file.reading import'
    'from utils\.file_utils_security import' = 'from utils.file.security import'
    'from utils\.file_utils_tokens import' = 'from utils.file.tokens import'
    'from utils\.file_cache import' = 'from utils.file.cache import'
    'from utils\.file_types import' = 'from utils.file.types import'
    
    'from utils\.conversation_memory import' = 'from utils.conversation.memory import'
    'from utils\.conversation_history import' = 'from utils.conversation.history import'
    'from utils\.conversation_models import' = 'from utils.conversation.models import'
    'from utils\.conversation_threads import' = 'from utils.conversation.threads import'
    
    'from utils\.model_context import' = 'from utils.model.context import'
    'from utils\.model_restrictions import' = 'from utils.model.restrictions import'
    'from utils\.token_estimator import' = 'from utils.model.token_estimator import'
    'from utils\.token_utils import' = 'from utils.model.token_utils import'
    
    'from utils\.config_bootstrap import' = 'from utils.config.bootstrap import'
    'from utils\.config_helpers import' = 'from utils.config.helpers import'
    'from utils\.security_config import' = 'from utils.config.security import'
    
    'from utils\.progress_messages import' = 'from utils.progress.messages import'
    
    'from utils\.health import' = 'from utils.infrastructure.health import'
    'from utils\.metrics import' = 'from utils.infrastructure.metrics import'
    'from utils\.instrumentation import' = 'from utils.infrastructure.instrumentation import'
    'from utils\.lru_cache_ttl import' = 'from utils.infrastructure.lru_cache_ttl import'
    'from utils\.storage_backend import' = 'from utils.infrastructure.storage_backend import'
    'from utils\.costs import' = 'from utils.infrastructure.costs import'
    'from utils\.docs_validator import' = 'from utils.infrastructure.docs_validator import'
    'from utils\.error_handling import' = 'from utils.infrastructure.error_handling import'
}

# Get all Python files (exclude backups and archive)
$files = Get-ChildItem -Recurse -Include "*.py" -Exclude "*_BACKUP.py","*archive*" | Where-Object { $_.FullName -notlike "*\archive\*" -and $_.FullName -notlike "*\__pycache__\*" }

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
        Write-Output "Updated: $($file.FullName) ($fileReplacements replacements)"
    }
}

Write-Output ""
Write-Output "Summary:"
Write-Output "  Files updated: $totalFiles"
Write-Output "  Total replacements: $totalReplacements"
Write-Output ""
Write-Output "Import updates complete!"

