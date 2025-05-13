#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import threading
import customtkinter as ctk

from config.settings import APP_TITLE, DEFAULT_WIDTH, DEFAULT_HEIGHT, DEFAULT_CONNECTION_URL, DEFAULT_BACKUP_FILENAME
from core.system_utils import get_available_tools, get_install_instructions
from core.backup_manager import BackupManager
from ui.components import ConsoleOutput, ConnectionFrame, ActionButtonsFrame

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
        
        # Inicializar gestor de backup con nuestro logger
        self.backup_manager = BackupManager(logger_callback=self.log)
        
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
        
        # Frame para la conexión
        conn_frame = ConnectionFrame(
            main_frame,
            self.connection_var
        )
        conn_frame.pack(fill="x", padx=10, pady=10)
        
        # Frame de botones
        button_frame = ActionButtonsFrame(
            main_frame,
            self.start_backup
        )
        button_frame.pack(fill="x", padx=10, pady=10)
        
        # Panel de salida
        output_label = ctk.CTkLabel(
            main_frame, 
            text="Salida:",
            anchor="w"
        )
        output_label.pack(anchor="w", padx=10, pady=(10, 0))
        
        self.output_console = ConsoleOutput(
            main_frame,
            width=650,
            height=350
        )
        self.output_console.pack(fill="both", expand=True, padx=10, pady=10)
    
    def log(self, message):
        """Registra un mensaje en la consola de salida"""
        self.output_console.append(message)
    
    def start_backup(self):
        """Inicia el proceso de backup en un hilo separado"""
        # Limpiar la salida actual
        self.output_console.clear()
        
        # Iniciar backup en un hilo separado para evitar bloquear la interfaz
        threading.Thread(target=self.perform_backup, daemon=True).start()
    
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