$file = "C:\ai-bid\docker-compose.yml"
$content = Get-Content $file -Raw
$old = 'test: ["CMD", "curl", "-f", "http://localhost:8086/health"]'
$new = 'test: ["CMD-SHELL", "python -c \""import urllib.request;urllib.request.urlopen('\'http://localhost:8086/health\'')"\""]'
$content = $content.Replace($old, $new)
[System.IO.File]::WriteAllText($file, $content, [System.Text.Encoding]::UTF8)
Write-Host "Done"
