$content = Get-Content 'C:\ai-bid\docker-compose.yml' -Raw
$content = $content -replace 'context: \./ai-bid-user\r?\n      dockerfile: Dockerfile', "context: .`n      dockerfile: ai-bid-user/Dockerfile"
$content = $content -replace 'context: \./ai-bid-gateway\r?\n      dockerfile: Dockerfile', "context: .`n      dockerfile: ai-bid-gateway/Dockerfile"
$content = $content -replace 'context: \./ai-bid-project\r?\n      dockerfile: Dockerfile', "context: .`n      dockerfile: ai-bid-project/Dockerfile"
$content = $content -replace 'context: \./ai-bid-material\r?\n      dockerfile: Dockerfile', "context: .`n      dockerfile: ai-bid-material/Dockerfile"
$content = $content -replace 'context: \./ai-bid-document\r?\n      dockerfile: Dockerfile', "context: .`n      dockerfile: ai-bid-document/Dockerfile"
$content = $content -replace 'context: \./ai-bid-bid\r?\n      dockerfile: Dockerfile', "context: .`n      dockerfile: ai-bid-bid/Dockerfile"
[System.IO.File]::WriteAllText('C:\ai-bid\docker-compose.yml', $content, [System.Text.Encoding]::UTF8)
Write-Host 'Done'
