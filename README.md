# PostgreSQL Backup Tool 🗄️

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![CustomTkinter](https://img.shields.io/badge/CustomTkinter-5.0+-green.svg)](https://github.com/TomSchimansky/CustomTkinter)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Support-blue.svg)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Compatible-blue.svg)](https://www.docker.com/)

Una aplicación con interfaz gráfica moderna para realizar copias de seguridad de bases de datos PostgreSQL con soporte multilingüe y multiplatforma.

![Captura de pantalla de PostgreSQL Backup Tool](./example/image.png)

## 🌟 Características

- **Interfaz gráfica moderna** - Usando CustomTkinter para una experiencia visual agradable
- **Soporte multiplataforma** - Compatible con Windows, macOS y Linux
- **Flexibilidad de herramientas** - Utiliza Docker o pg_dump local según disponibilidad
- **Gestión automática de codificación UTF-8** - Evita problemas con caracteres especiales
- **Instrucciones de restauración** - Genera comandos específicos según tu sistema operativo
- **Gestión simplificada de conexiones** - Conexión mediante URL estándar PostgreSQL

## 📋 Requisitos previos

Para utilizar esta herramienta, necesitas tener instalado una de las siguientes opciones:

- **Docker Desktop** - [Descargar Docker](https://www.docker.com/products/docker-desktop/)
- **Cliente PostgreSQL** (pg_dump)
  - Windows: Instalable con PostgreSQL
  - macOS: `brew install postgresql`
  - Linux: `sudo apt-get install postgresql-client`

## 🚀 Instalación

1. Clona este repositorio:
   ```bash
   git clone https://github.com/tu-usuario/postgresql-backup-tool.git
   cd postgresql-backup-tool
   ```

2. Crea un entorno virtual e instala las dependencias:
   ```bash
   # Windows
   python -m venv env
   env\Scripts\activate
   pip install -r requirements.txt

   # macOS/Linux
   python3 -m venv env
   source env/bin/activate
   pip install -r requirements.txt
   ```

3. Ejecuta la aplicación:
   ```bash
   python main.py
   ```

## 📝 Uso

1. Inicia la aplicación.
2. Introduce la URL de conexión en el formato:
   ```
   postgresql://usuario:contraseña@host:puerto/nombre_base_datos
   ```
3. Haz clic en "Iniciar Backup".
4. La aplicación generará un archivo de backup y mostrará instrucciones de restauración.

## 🔄 Restauración de backups

### Windows (PowerShell)

```powershell
.\restore_database.ps1 -BackupFile backup.sql -DatabaseName miBaseDatos
```

### macOS/Linux

```bash
./restore_database.sh --file backup.sql --database miBaseDatos
```

O usando el cliente PostgreSQL directamente:

```bash
PGPASSWORD=tucontraseña psql -h localhost -p 5432 -U usuario -d base_datos < backup.sql
```

## 🧩 Estructura del proyecto

```
postgresql-backup-tool/
├── config/                   # Configuración de la aplicación
│   ├── __init__.py
│   └── settings.py           # Parámetros configurables
├── core/                     # Lógica principal
│   ├── __init__.py
│   ├── backup_manager.py     # Gestión de backups
│   └── system_utils.py       # Utilidades del sistema
├── ui/                       # Interfaz de usuario
│   ├── __init__.py
│   ├── app.py                # Aplicación principal
│   └── components.py         # Componentes de la UI
├── .vscode/                  # Configuración de Visual Studio Code
├── main.py                   # Punto de entrada
├── restore_database.ps1      # Script de restauración para Windows
├── restore_database.sh       # Script de restauración para macOS/Linux
└── README.md                 # Este archivo
```

## 🛠️ Opciones avanzadas

### Parámetros de pg_dump

Los parámetros utilizados por defecto son:
- `-c`: Incluye comandos DROP antes de CREATE
- `--if-exists`: Usa IF EXISTS en comandos DROP
- `--no-owner`: Omite comandos para establecer propiedad
- `--no-privileges`: Omite comandos para establecer privilegios

Puedes modificarlos en `config/settings.py`.

### Solución de problemas de codificación UTF-8

Si experimentas problemas con caracteres especiales:

- En Windows: Usa el parámetro `-Encoding UTF8` con PowerShell
- En macOS/Linux: Usa `iconv -f UTF-8 -t UTF-8 archivo.sql`

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Para cambios importantes:

1. Haz fork del repositorio
2. Crea una nueva rama (`git checkout -b feature/nueva-caracteristica`)
3. Realiza tus cambios y haz commit (`git commit -am 'Añade nueva característica'`)
4. Haz push a la rama (`git push origin feature/nueva-caracteristica`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## 📞 Soporte

Si tienes preguntas o necesitas ayuda:
- Abre un [Issue](https://github.com/anthonidev/backup-database-docker/issues)
- Envía un correo a [softwaretoni21@gmail.com](mailto:softwaretoni21@gmail.com)

---

Hecho con ❤️ por [Anthonidev](https://github.com/anthonidev)