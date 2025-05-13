# Script para restaurar base de datos PostgreSQL con manejo apropiado de codificación UTF-8
param(
    [string]$BackupFile = "backup.sql",
    [string]$ContainerName = "nexus_db",
    [string]$DatabaseName = "NexusDB",
    [string]$Username = "postgres"
)

# Verificar que el archivo existe
if (-not (Test-Path $BackupFile)) {
    Write-Error "El archivo de backup $BackupFile no existe."
    exit 1
}

# Verificar que el contenedor está en ejecución
$containerRunning = docker ps --filter "name=$ContainerName" --format "{{.Names}}"
if (-not $containerRunning) {
    Write-Error "El contenedor $ContainerName no está en ejecución."
    exit 1
}

Write-Host "Configurando entorno del contenedor para UTF-8..." -ForegroundColor Cyan
# Asegurar que la configuración del cliente PostgreSQL usa UTF-8
docker exec -i $ContainerName bash -c "echo 'client_encoding = UTF8;' > /tmp/psqlrc"
docker exec -i $ContainerName bash -c "export PGCLIENTENCODING=UTF8"

Write-Host "Restaurando la base de datos desde $BackupFile..." -ForegroundColor Cyan
# Método 1: Copiar el archivo al contenedor y restaurar desde allí
docker cp $BackupFile "${ContainerName}:/tmp/backup.sql"
$result = docker exec -i $ContainerName bash -c "PGCLIENTENCODING=UTF8 psql -U $Username -d $DatabaseName -f /tmp/backup.sql 2>&1"

if ($LASTEXITCODE -ne 0) {
    Write-Error "Error al restaurar la base de datos:"
    Write-Error $result
    exit 1
}

Write-Host "Base de datos restaurada exitosamente!" -ForegroundColor Green
Write-Host "Nota: Si aún hay problemas con caracteres especiales, verifica la configuración de tu contenedor PostgreSQL."