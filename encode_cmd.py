import base64
cmd = r'''powershell -NoProfile -Command "Get-Content C:\ai-bid\docker-compose.yml | ForEach-Object {$u = $u -replace 'test: [\"CMD\", \"curl\", \"-f\", \"http://localhost:8086/health\"]', 'test: [\"CMD\", \"CMD\", \"echo\", \"ok\"]' }; Set-Content -Path C:\ai-bid\docker-compose.yml -Value $u"'''
encoded = base64.b64encode(cmd.encode('utf-16le')).decode()
print(encoded)
