$ContainerName = "pm-mvp"

$existing = docker ps -a --format "{{.Names}}" | Where-Object { $_ -eq $ContainerName }
if ($existing) {
  docker rm -f $ContainerName | Out-Null
} else {
  Write-Host "Container not running"
}
