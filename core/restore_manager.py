#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import subprocess
from core.system_utils import get_system_info


class RestoreManager:
    def __init__(self, logger_callback=None):
        """
        Inicializa el gestor de restauración
        
        Args:
            logger_callback (callable): Función para registrar mensajes
        """
        self.logger = logger_callback if logger_callback else print
        self.system_info = get_system_info()
    
    def log(self, message):
        """Registra un mensaje usando el callback configurado"""
        if self.logger:
            self.logger(message)
    
    def restore_with_powershell(self, backup_file, container_name, database_name, username):
        """
        Ejecuta el script de restauración de PowerShell para Windows
        
        Args:
            backup_file (str): Ruta al archivo de backup
            container_name (str): Nombre del contenedor Docker
            database_name (str): Nombre de la base de datos
            username (str): Nombre de usuario de PostgreSQL
        
        Returns:
            bool: True si la restauración fue exitosa, False en caso contrario
        """
        # Obtener la ruta al script PowerShell
        script_path = self._get_powershell_script_path()
        
        if not os.path.isfile(script_path):
            self.log(f"✗ Error: No se encontró el script de restauración en {script_path}")
            return False
        
        # Comando para ejecutar el script PowerShell
        command = [
            "powershell",
            "-ExecutionPolicy", "Bypass",
            "-File", script_path,
            "-BackupFile", backup_file,
            "-ContainerName", container_name,
            "-DatabaseName", database_name,
            "-Username", username
        ]
        
        self.log(f"Ejecutando comando: {' '.join(command)}")
        
        try:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                universal_newlines=True
            )
            
            # Leer y mostrar la salida en tiempo real
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    self.log(output.strip())
            
            # Capturar errores
            rc = process.poll()
            if rc != 0:
                stderr = process.stderr.read()
                if stderr:
                    self.log(f"Error: {stderr}")
                self.log(f"✗ El script de restauración falló con código {rc}")
                return False
            
            self.log("✓ Restauración completada exitosamente")
            return True
            
        except Exception as e:
            self.log(f"✗ Error al ejecutar el script: {e}")
            return False
    
    def restore_with_bash(self, backup_file, container_name, database_name, username):
        """
        Ejecuta el script de restauración Bash para macOS/Linux
        
        Args:
            backup_file (str): Ruta al archivo de backup
            container_name (str): Nombre del contenedor Docker
            database_name (str): Nombre de la base de datos
            username (str): Nombre de usuario de PostgreSQL
        
        Returns:
            bool: True si la restauración fue exitosa, False en caso contrario
        """
        # Obtener la ruta al script Bash
        script_path = self._get_bash_script_path()
        
        if not os.path.isfile(script_path):
            self.log(f"✗ Error: No se encontró el script de restauración en {script_path}")
            return False
        
        # Asegurar que el script tiene permisos de ejecución
        try:
            os.chmod(script_path, 0o755)
        except Exception as e:
            self.log(f"Advertencia: No se pudieron establecer permisos de ejecución: {e}")
        
        # Comando para ejecutar el script Bash
        command = [
            script_path,
            "-f", backup_file,
            "-c", container_name,
            "-d", database_name,
            "-u", username
        ]
        
        self.log(f"Ejecutando comando: {' '.join(command)}")
        
        try:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                universal_newlines=True
            )
            
            # Leer y mostrar la salida en tiempo real
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    self.log(output.strip())
            
            # Capturar errores
            rc = process.poll()
            if rc != 0:
                stderr = process.stderr.read()
                if stderr:
                    self.log(f"Error: {stderr}")
                self.log(f"✗ El script de restauración falló con código {rc}")
                return False
            
            self.log("✓ Restauración completada exitosamente")
            return True
            
        except Exception as e:
            self.log(f"✗ Error al ejecutar el script: {e}")
            return False
    
    def restore_with_connection_url(self, backup_file, connection_url):
        """
        Restaura un backup directamente a un servidor PostgreSQL usando una URL de conexión
        
        Args:
            backup_file (str): Ruta al archivo de backup
            connection_url (str): URL de conexión PostgreSQL para el destino
        
        Returns:
            bool: True si la restauración fue exitosa, False en caso contrario
        """
        # Analizar la URL de conexión
        conn_info = self._parse_connection_url(connection_url)
        if not conn_info:
            self.log(f"✗ Error: URL de conexión inválida: {connection_url}")
            return False
        
        self.log(f"→ Restaurando backup a servidor remoto: {conn_info['host']}:{conn_info['port']}/{conn_info['database']}")
        
        # Verificar el archivo de backup
        if not os.path.isfile(backup_file):
            self.log(f"✗ Error: El archivo de backup no existe: {backup_file}")
            return False
        
        # Ejecutar restauración según el sistema operativo
        if self.system_info["is_windows"]:
            # Primero intentar usar el script PowerShell específico
            script_path = self._get_remote_powershell_script_path()
            if os.path.isfile(script_path):
                return self._restore_with_remote_powershell_script(backup_file, connection_url, script_path)
            else:
                self.log(f"Script específico no encontrado, usando método estándar...")
                return self._restore_remote_windows(backup_file, conn_info)
        else:  # macOS o Linux
            # Primero intentar usar el script Bash específico
            script_path = self._get_remote_bash_script_path()
            if os.path.isfile(script_path):
                return self._restore_with_remote_bash_script(backup_file, connection_url, script_path)
            else:
                self.log(f"Script específico no encontrado, usando método estándar...")
                return self._restore_remote_unix(backup_file, conn_info)
    
    def _restore_remote_windows(self, backup_file, conn_info):
        """Restauración remota en Windows usando psql"""
        # Configurar entorno
        env = os.environ.copy()
        env['PGPASSWORD'] = conn_info['password']
        
        # Construir comando
        command = [
            "psql",
            "-h", conn_info['host'],
            "-p", conn_info['port'],
            "-U", conn_info['username'],
            "-d", conn_info['database'],
            "-f", backup_file
        ]
        
        self.log(f"Ejecutando comando: {' '.join(command)}")
        
        try:
            # Ejecutar comando
            process = subprocess.Popen(
                command,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                universal_newlines=True
            )
            
            # Leer y mostrar la salida en tiempo real
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    self.log(output.strip())
            
            # Capturar errores
            rc = process.poll()
            if rc != 0:
                stderr = process.stderr.read()
                if stderr:
                    self.log(f"Error: {stderr}")
                self.log(f"✗ La restauración falló con código {rc}")
                return False
            
            self.log("✓ Restauración remota completada exitosamente")
            return True
            
        except Exception as e:
            self.log(f"✗ Error al ejecutar la restauración remota: {e}")
            # Verificar si psql está instalado
            if isinstance(e, FileNotFoundError):
                self.log("✗ El comando 'psql' no fue encontrado. Necesitas instalar el cliente PostgreSQL.")
                self.log("  - Para Windows: Descarga PostgreSQL desde https://www.postgresql.org/download/windows/")
            return False
    
    def _restore_remote_unix(self, backup_file, conn_info):
        """Restauración remota en macOS/Linux usando psql"""
        # Configurar entorno
        env = os.environ.copy()
        env['PGPASSWORD'] = conn_info['password']
        
        # Construir comando
        command = [
            "psql",
            "-h", conn_info['host'],
            "-p", conn_info['port'],
            "-U", conn_info['username'],
            "-d", conn_info['database'],
            "-f", backup_file
        ]
        
        self.log(f"Ejecutando comando: {' '.join(command)}")
        
        try:
            # Ejecutar comando
            process = subprocess.Popen(
                command,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                universal_newlines=True
            )
            
            # Leer y mostrar la salida en tiempo real
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    self.log(output.strip())
            
            # Capturar errores
            rc = process.poll()
            if rc != 0:
                stderr = process.stderr.read()
                if stderr:
                    self.log(f"Error: {stderr}")
                self.log(f"✗ La restauración falló con código {rc}")
                return False
            
            self.log("✓ Restauración remota completada exitosamente")
            return True
            
        except Exception as e:
            self.log(f"✗ Error al ejecutar la restauración remota: {e}")
            # Verificar si psql está instalado
            if isinstance(e, FileNotFoundError):
                self.log("✗ El comando 'psql' no fue encontrado. Necesitas instalar el cliente PostgreSQL.")
                if self.system_info["is_macos"]:
                    self.log("  - Para macOS: brew install postgresql")
                else:
                    self.log("  - Para Linux: sudo apt-get install postgresql-client")
            return False
    
    def _parse_connection_url(self, connection_url):
        """Analiza una URL de conexión PostgreSQL y devuelve sus componentes"""
        import re
        pattern = r'postgresql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)'
        match = re.match(pattern, connection_url)
        
        if not match:
            self.log("✗ No se pudo analizar la URL de conexión.")
            return None
        
        return {
            "username": match.group(1),
            "password": match.group(2),
            "host": match.group(3),
            "port": match.group(4),
            "database": match.group(5)
        }
    
    def _restore_with_remote_powershell_script(self, backup_file, connection_url, script_path):
        """Restaura a un servidor remoto usando un script PowerShell dedicado"""
        
        # Comando para ejecutar el script PowerShell
        command = [
            "powershell",
            "-ExecutionPolicy", "Bypass",
            "-File", script_path,
            "-BackupFile", backup_file,
            "-ConnectionURL", connection_url
        ]
        
        self.log(f"Ejecutando comando: {' '.join(command)}")
        
        try:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                universal_newlines=True
            )
            
            # Leer y mostrar la salida en tiempo real
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    self.log(output.strip())
            
            # Capturar errores
            rc = process.poll()
            if rc != 0:
                stderr = process.stderr.read()
                if stderr:
                    self.log(f"Error: {stderr}")
                self.log(f"✗ El script de restauración remota falló con código {rc}")
                return False
            
            self.log("✓ Restauración remota completada exitosamente")
            return True
            
        except Exception as e:
            self.log(f"✗ Error al ejecutar el script: {e}")
            return False
    
    def _restore_with_remote_bash_script(self, backup_file, connection_url, script_path):
        """Restaura a un servidor remoto usando un script Bash dedicado"""
        
        # Asegurar que el script tiene permisos de ejecución
        try:
            os.chmod(script_path, 0o755)
        except Exception as e:
            self.log(f"Advertencia: No se pudieron establecer permisos de ejecución: {e}")
        
        # Comando para ejecutar el script Bash
        command = [
            script_path,
            "-f", backup_file,
            "-c", connection_url
        ]
        
        self.log(f"Ejecutando comando: {' '.join(command)}")
        
        try:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                universal_newlines=True
            )
            
            # Leer y mostrar la salida en tiempo real
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    self.log(output.strip())
            
            # Capturar errores
            rc = process.poll()
            if rc != 0:
                stderr = process.stderr.read()
                if stderr:
                    self.log(f"Error: {stderr}")
                self.log(f"✗ El script de restauración remota falló con código {rc}")
                return False
            
            self.log("✓ Restauración remota completada exitosamente")
            return True
            
        except Exception as e:
            self.log(f"✗ Error al ejecutar el script: {e}")
            return False
    
    def _get_remote_powershell_script_path(self):
        """Obtiene la ruta al script PowerShell de restauración remota"""
        # Obtener el directorio del script actual
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(current_dir, "restore_remote.ps1")
    
    def _get_remote_bash_script_path(self):
        """Obtiene la ruta al script Bash de restauración remota"""
        # Obtener el directorio del script actual
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(current_dir, "restore_remote.sh") 