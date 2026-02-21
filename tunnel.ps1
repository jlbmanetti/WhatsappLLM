# Expose port 8000 and get the Callback URL for Meta.
# Run this in a NEW terminal while the app is running (e.g. py -3 app.py).
# Requires Node.js (npx). Fallback without Node: ssh -R 80:localhost:8000 nokey@localhost.run

$ErrorActionPreference = "Stop"
Write-Host ""
Write-Host "  WhatsApp LLM - Tunnel (Callback URL for Meta)" -ForegroundColor Cyan
Write-Host "  ------------------------------------------------" -ForegroundColor Cyan
Write-Host "  Forwarding localhost:8000 to a public URL..." -ForegroundColor Gray
Write-Host "  Use the URL below + /webhook as Callback URL in Meta." -ForegroundColor Yellow
Write-Host "  Example: https://abc.loca.lt  ->  https://abc.loca.lt/webhook" -ForegroundColor DarkGray
Write-Host ""

npx --yes localtunnel --port 8000
