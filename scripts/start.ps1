$ImageName = "pm-mvp"
$ContainerName = "pm-mvp"
$Root = Split-Path -Parent $PSScriptRoot
$DataDir = Join-Path $Root "backend/data"

New-Item -ItemType Directory -Force -Path $DataDir | Out-Null

docker build -t $ImageName $Root

$existing = docker ps -a --format "{{.Names}}" | Where-Object { $_ -eq $ContainerName }
if ($existing) {
  docker rm -f $ContainerName | Out-Null
}

docker run -d --name $ContainerName -p 8000:8000 --env-file "$Root/backend/.env" -e PM_DB_PATH=/app/backend/data/pm.db -v "${DataDir}:/app/backend/data" $ImageName | Out-Null

Write-Host "Running on http://localhost:8000"
