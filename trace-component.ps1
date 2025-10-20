# Save as trace-component.ps1
param($Component="singletons")  # or providers, request_handler, etc.
Get-ChildItem -Recurse -Include *.py |
    Select-String -Pattern "\b$Component\b" |
    Select-Object -ExpandProperty Path |
    Sort-Object -Unique |
    ForEach-Object { [PSCustomObject]@{Component=$Component; File=$_} } |
    Export-Csv -Path "backbone-$Component.csv" -NoTypeInformation
Write-Host "📊 backbone-$Component.csv created"

