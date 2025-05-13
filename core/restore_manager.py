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
    
    def _get_powershell_script_path(self):
        """Obtiene la ruta al script PowerShell de restauración"""
        # Obtener el directorio del script actual
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(current_dir, "restore_database.ps1")
    
    def _get_bash_script_path(self):
        """Obtiene la ruta al script Bash de restauración"""
        # Obtener el directorio del script actual
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(current_dir, "restore_database.sh")