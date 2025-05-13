#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import threading
import customtkinter as ctk

from config.settings import APP_TITLE, DEFAULT_WIDTH, DEFAULT_HEIGHT, DEFAULT_CONNECTION_URL, DEFAULT_BACKUP_FILENAME
from core.system_utils import get_system_info, get_available_tools, get_install_instructions
from core.backup_manager import BackupManager
from core.restore_manager import RestoreManager
from ui.components import ConsoleOutput, ConnectionFrame, ActionButtonsFrame, RestoreFrame

class PostgreSQLBackupApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configuración de la ventana
        self.title(APP_TITLE)
        self.geometry(f"{DEFAULT_WIDTH}x{DEFAULT_HEIGHT}")
        
        # Establecer tema
        ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
        ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"
        
        # Variables
        self.connection_var = ctk.StringVar(value=DEFAULT_CONNECTION_URL)
        self.backup_file_var = ctk.StringVar(value=DEFAULT_BACKUP_FILENAME)
        self.container_name_var = ctk.StringVar(value="nexus_db")
        self.database_name_var = ctk.StringVar(value="NexusDB")
        self.username_var = ctk.StringVar(value="postgres")
        
        # Detectar sistema operativo
        self.system_info = get_system_info()
        
        # Inicializar gestores
        self.backup_manager = BackupManager(logger_callback=self.log)
        self.restore_manager = RestoreManager(logger_callback=self.log)
        
        # Crear interfaz
        self.create_widgets()
    
    def create_widgets(self):
        """Crea todos los widgets de la interfaz"""
        
        # Frame principal
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(padx=20, pady=20, fill="both", expand=True)
        
        # Título
        title_label = ctk.CTkLabel(
            main_frame, 
            text=APP_TITLE, 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Crear pestañas
        self.tabview = ctk.CTkTabview(main_frame)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Configurar pestañas
        self.tab_backup = self.tabview.add("Backup")
        self.tab_restore = self.tabview.add("Restauración")
        
        # Seleccionar pestaña por defecto
        self.tabview.set("Backup")
        
        # Configurar pestaña de Backup
        self.setup_backup_tab()
        
        # Configurar pestaña de Restauración
        self.setup_restore_tab()
    
    def setup_backup_tab(self):
        """Configura la pestaña de backup"""
        
        # Frame para la conexión
        conn_frame = ConnectionFrame(
            self.tab_backup,
            self.connection_var
        )
        conn_frame.pack(fill="x", padx=10, pady=10)
        
        # Frame de botones
        button_frame = ActionButtonsFrame(
            self.tab_backup,
            self.start_backup
        )
        button_frame.pack(fill="x", padx=10, pady=10)
        
        # Panel de salida
        output_label = ctk.CTkLabel(
            self.tab_backup, 
            text="Salida:",
            anchor="w"
        )
        output_label.pack(anchor="w", padx=10, pady=(10, 0))
        
        self.backup_output_console = ConsoleOutput(
            self.tab_backup,
            width=650,
            height=300
        )
        self.backup_output_console.pack(fill="both", expand=True, padx=10, pady=10)
    
    def setup_restore_tab(self):
        """Configura la pestaña de restauración"""
        
        # Frame para los parámetros de restauración
        self.restore_frame = RestoreFrame(
            self.tab_restore,
            self.backup_file_var,
            self.container_name_var,
            self.database_name_var,
            self.username_var,
            self.browse_backup_file,
            self.start_restore
        )
        self.restore_frame.pack(fill="x", padx=10, pady=10)
        
        # Panel de salida para restauración
        output_label = ctk.CTkLabel(
            self.tab_restore, 
            text="Salida:",
            anchor="w"
        )
        output_label.pack(anchor="w", padx=10, pady=(10, 0))
        
        self.restore_output_console = ConsoleOutput(
            self.tab_restore,
            width=650,
            height=300
        )
        self.restore_output_console.pack(fill="both", expand=True, padx=10, pady=10)
    
    def log(self, message):
        """Registra un mensaje en la consola activa"""
        active_tab = self.tabview.get()
        if active_tab == "Backup":
            self.backup_output_console.append(message)
        else:
            self.restore_output_console.append(message)
    
    def browse_backup_file(self):
        """Abre un diálogo para seleccionar un archivo de backup"""
        filetypes = [("SQL Files", "*.sql"), ("All Files", "*.*")]
        filename = ctk.filedialog.askopenfilename(
            title="Seleccionar archivo de backup",
            filetypes=filetypes
        )
        if filename:
            self.backup_file_var.set(filename)
    
    def start_backup(self):
        """Inicia el proceso de backup en un hilo separado"""
        # Limpiar la salida actual
        self.backup_output_console.clear()
        
        # Iniciar backup en un hilo separado para evitar bloquear la interfaz
        threading.Thread(target=self.perform_backup, daemon=True).start()
    
    def start_restore(self):
        """Inicia el proceso de restauración en un hilo separado"""
        # Limpiar la salida actual
        self.restore_output_console.clear()
        
        # Iniciar restauración en un hilo separado
        threading.Thread(target=self.perform_restore, daemon=True).start()
    
    def perform_backup(self):
        """Realiza el backup de la base de datos"""
        connection_url = self.connection_var.get()
        
        # Analizar URL de conexión
        conn_info = self.backup_manager.parse_connection_url(connection_url)
        if not conn_info:
            return
        
        # Crear nombre de archivo
        backup_file = self.backup_manager.create_backup_filename(conn_info['database'])
        final_backup = DEFAULT_BACKUP_FILENAME
        
        # Mostrar cabecera
        self.log("="*50)
        self.log(f"INICIANDO BACKUP DE BASE DE DATOS")
        self.log(f"Sistema operativo: {sys.platform}")
        self.log("="*50)
        
        # Verificar herramientas disponibles
        tools = get_available_tools()
        self.log(f"\nVerificación de herramientas:")
        self.log(f"Docker: {'✓ disponible' if tools['has_docker'] else '✗ no disponible'}")
        self.log(f"pg_dump: {'✓ disponible' if tools['has_pg_dump'] else '✗ no disponible'}")
        
        # Ejecutar backup según las herramientas disponibles
        backup_successful = False
        
        if tools['has_pg_dump'] and not sys.platform.startswith('win'):
            self.log(f"\n→ Usando pg_dump local...")
            backup_successful = self.backup_manager.backup_with_local_pg_dump(
                conn_info, backup_file, final_backup
            )
        elif tools['has_docker']:
            self.log(f"\n→ Usando Docker...")
            backup_successful = self.backup_manager.backup_with_docker(
                conn_info, backup_file, final_backup
            )
        else:
            self.log("\n✗ No hay herramientas disponibles para crear el backup.")
            self.log("\n" + get_install_instructions())
        
        # Mostrar instrucciones de restauración si el backup fue exitoso
        if backup_successful:
            instructions = self.backup_manager.get_restore_instructions(conn_info, final_backup)
            for line in instructions:
                self.log(line)
    
    def perform_restore(self):
        """Realiza la restauración de la base de datos"""
        # Obtener parámetros
        backup_file = self.backup_file_var.get()
        container_name = self.container_name_var.get()
        database_name = self.database_name_var.get()
        username = self.username_var.get()
        
        # Verificar que el archivo existe
        if not os.path.isfile(backup_file):
            self.log(f"✗ Error: El archivo de backup {backup_file} no existe.")
            return
        
        # Mostrar cabecera
        self.log("="*50)
        self.log(f"INICIANDO RESTAURACIÓN DE BASE DE DATOS")
        self.log(f"Sistema operativo: {sys.platform}")
        self.log(f"Archivo de backup: {backup_file}")
        self.log("="*50)
        
        # Verificar herramientas disponibles
        tools = get_available_tools()
        self.log(f"\nVerificación de herramientas:")
        self.log(f"Docker: {'✓ disponible' if tools['has_docker'] else '✗ no disponible'}")
        self.log(f"psql: {'✓ disponible' if tools['has_pg_dump'] else '✗ no disponible'}")
        
        # Ejecutar restauración según el sistema operativo
        if self.system_info["is_windows"]:
            self.log("\n→ Usando script de PowerShell para Windows...")
            self.restore_manager.restore_with_powershell(
                backup_file, container_name, database_name, username
            )
        else:  # macOS o Linux
            self.log("\n→ Usando script Bash para macOS/Linux...")
            self.restore_manager.restore_with_bash(
                backup_file, container_name, database_name, username
            )