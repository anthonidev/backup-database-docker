# Script para restaurar base de datos PostgreSQL en un servidor remoto desde Windows
param(
    [string]$BackupFile = "backup.sql",
    [string]$ConnectionURL = "postgresql://postgres:123@localhost:5432/postgres"
)

# Verificar que el archivo existe
if (-not (Test-Path $BackupFile)) {
    Write-Error "El archivo de backup $BackupFile no existe."
    exit 1
}

# Función para analizar la URL de conexión
function Parse-ConnectionURL {
    param([string]$URL)
    
    $pattern = "postgresql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)"
    if ($URL -match $pattern) {
        $username = $matches[1]
        $password = $matches[2]
        $hostname = $matches[3]  # Cambiado de $host a $hostname para evitar conflicto
        $port = $matches[4]
        $database = $matches[5]
        
        Write-Host "Usuario: $username"
        Write-Host "Host: $hostname"
        Write-Host "Puerto: $port"
        Write-Host "Base de datos: $database"
        
        return @{
            Username = $username
            Password = $password
            Host = $hostname     # Cambiado de $host a $hostname
            Port = $port
            Database = $database
        }
    } else {
        Write-Error "Formato de URL incorrecto."
        Write-Host "Formato esperado: postgresql://usuario:contraseña@host:puerto/basededatos"
        return $null
    }
}

# Función para verificar si psql está disponible
function Test-PSQLAvailable {
    try {
        $null = & psql --version
        return $true
    } catch {
        return $false
    }
}

# Función para restaurar usando psql
function Restore-WithPSQL {
    param(
        [string]$BackupFile,
        [hashtable]$ConnectionInfo
    )
    
    Write-Host "Restaurando la base de datos desde $BackupFile..." -ForegroundColor Cyan
    Write-Host "Destino: $($ConnectionInfo.Host):$($ConnectionInfo.Port)/$($ConnectionInfo.Database)" -ForegroundColor Cyan
    
    # Configurar entorno para UTF-8
    $env:PGCLIENTENCODING = "UTF8"
    $env:PGPASSWORD = $ConnectionInfo.Password
    
    try {
        $result = & psql -h $ConnectionInfo.Host -p $ConnectionInfo.Port -U $ConnectionInfo.Username -d $ConnectionInfo.Database -f $BackupFile 2>&1
        
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Error al restaurar la base de datos:"
            Write-Error $result
            return $false
        } else {
            Write-Host "¡Base de datos restaurada exitosamente!" -ForegroundColor Green
            return $true
        }
    } catch {
        Write-Error "Error al ejecutar psql: $_"
        return $false
    } finally {
        # Limpiar variable de contraseña
        Remove-Item Env:\PGPASSWORD -ErrorAction SilentlyContinue
    }
}

# Verificar si psql está disponible
if (-not (Test-PSQLAvailable)) {
    Write-Error "PostgreSQL (psql) no está instalado o no está disponible en el PATH."
    Write-Host "Instala PostgreSQL client desde: https://www.postgresql.org/download/windows/"
    exit 1
}

# Analizar la URL de conexión
$connectionInfo = Parse-ConnectionURL -URL $ConnectionURL
if (-not $connectionInfo) {
    exit 1
}

# Ejecutar restauración
$result = Restore-WithPSQL -BackupFile $BackupFile -ConnectionInfo $connectionInfo

if (-not $result) {
    exit 1
}

Write-Host "Nota: Si hay problemas con caracteres especiales, verifica la configuración de codificación de PostgreSQL." -ForegroundColor Yellow