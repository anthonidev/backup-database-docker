#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import customtkinter as ctk

class ConsoleOutput(ctk.CTkTextbox):
    """Componente para mostrar salida tipo consola"""
    
    def __init__(self, master, **kwargs):
        font_family = "Consolas" if sys.platform == "win32" else "Courier"
        super().__init__(
            master, 
            font=ctk.CTkFont(family=font_family),
            **kwargs
        )
        self.configure(state="disabled")
    
    def clear(self):
        """Limpia el contenido"""
        self.configure(state="normal")
        self.delete("1.0", "end")
        self.configure(state="disabled")
    
    def append(self, message):
        """Añade un mensaje al final"""
        self.configure(state="normal")
        self.insert("end", message + "\n")
        self.see("end")
        self.configure(state="disabled")
        self.update_idletasks()

class ConnectionFrame(ctk.CTkFrame):
    """Frame para la información de conexión"""
    
    def __init__(self, master, connection_var, **kwargs):
        super().__init__(master, **kwargs)
        
        # Etiqueta
        self.conn_label = ctk.CTkLabel(
            self, 
            text="URL de conexión:"
        )
        self.conn_label.pack(anchor="w", padx=10, pady=(10, 0))
        
        # Campo de entrada
        self.conn_entry = ctk.CTkEntry(
            self, 
            textvariable=connection_var,
            width=500
        )
        self.conn_entry.pack(fill="x", padx=10, pady=10)
        
        # Ejemplo
        self.example_label = ctk.CTkLabel(
            self, 
            text="Ejemplo: postgresql://usuario:contraseña@localhost:5432/mi_base_de_datos",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        self.example_label.pack(anchor="w", padx=10, pady=(0, 10))

class ActionButtonsFrame(ctk.CTkFrame):
    """Frame para botones de acción"""
    
    def __init__(self, master, backup_callback, **kwargs):
        super().__init__(master, **kwargs)
        
        # Botón de backup
        self.backup_button = ctk.CTkButton(
            self, 
            text="Iniciar Backup", 
            command=backup_callback
        )
        self.backup_button.pack(side="left", padx=10, pady=10)

   
class RestoreFrame(ctk.CTkFrame):
    """Frame para la restauración de la base de datos"""
    
    def __init__(self, master, backup_file_var, container_name_var, database_name_var, 
                 username_var, connection_url_var, browse_callback, restore_callback, 
                 remote_restore_callback, **kwargs):
        super().__init__(master, **kwargs)
        
        # Crear un notebook con pestañas
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Pestañas para los diferentes métodos de restauración
        self.tab_local = self.tabview.add("Docker Local")
        self.tab_remote = self.tabview.add("Conexión Remota")
        
        # Pestaña por defecto
        self.tabview.set("Docker Local")
        
        # Configurar pestaña Docker Local
        self.setup_local_tab(backup_file_var, container_name_var, database_name_var, 
                           username_var, browse_callback, restore_callback)
        
        # Configurar pestaña Conexión Remota
        self.setup_remote_tab(backup_file_var, connection_url_var, browse_callback, 
                            remote_restore_callback)
    
    def setup_local_tab(self, backup_file_var, container_name_var, database_name_var, 
                       username_var, browse_callback, restore_callback):
        """Configura la pestaña de restauración local con Docker"""
        row = 0
        
        # Archivo de backup
        self.file_label = ctk.CTkLabel(
            self.tab_local, 
            text="Archivo de backup:"
        )
        self.file_label.grid(row=row, column=0, sticky="w", padx=10, pady=(10, 0))
        
        self.file_frame = ctk.CTkFrame(self.tab_local, fg_color="transparent")
        self.file_frame.grid(row=row+1, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 10))
        self.file_frame.columnconfigure(0, weight=1)
        
        self.file_entry = ctk.CTkEntry(
            self.file_frame, 
            textvariable=backup_file_var,
            width=400
        )
        self.file_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        
        self.browse_button = ctk.CTkButton(
            self.file_frame, 
            text="Examinar", 
            command=browse_callback,
            width=100
        )
        self.browse_button.grid(row=0, column=1)
        
        row += 2
        
        # Container name
        self.container_label = ctk.CTkLabel(
            self.tab_local, 
            text="Nombre del contenedor:"
        )
        self.container_label.grid(row=row, column=0, sticky="w", padx=10, pady=(10, 0))
        
        self.container_entry = ctk.CTkEntry(
            self.tab_local, 
            textvariable=container_name_var,
            width=500
        )
        self.container_entry.grid(row=row+1, column=0, sticky="ew", padx=10, pady=(0, 10))
        
        row += 2
        
        # Database name
        self.db_label = ctk.CTkLabel(
            self.tab_local, 
            text="Nombre de la base de datos:"
        )
        self.db_label.grid(row=row, column=0, sticky="w", padx=10, pady=(10, 0))
        
        self.db_entry = ctk.CTkEntry(
            self.tab_local, 
            textvariable=database_name_var,
            width=500
        )
        self.db_entry.grid(row=row+1, column=0, sticky="ew", padx=10, pady=(0, 10))
        
        row += 2
        
        # Username
        self.user_label = ctk.CTkLabel(
            self.tab_local, 
            text="Usuario de PostgreSQL:"
        )
        self.user_label.grid(row=row, column=0, sticky="w", padx=10, pady=(10, 0))
        
        self.user_entry = ctk.CTkEntry(
            self.tab_local, 
            textvariable=username_var,
            width=500
        )
        self.user_entry.grid(row=row+1, column=0, sticky="ew", padx=10, pady=(0, 10))
        
        row += 2
        
        # Botón de restauración
        self.restore_button = ctk.CTkButton(
            self.tab_local, 
            text="Iniciar Restauración en Docker Local", 
            command=restore_callback
        )
        self.restore_button.grid(row=row, column=0, padx=10, pady=10)
        
        # Configurar grid
        self.tab_local.columnconfigure(0, weight=1)
    
    def setup_remote_tab(self, backup_file_var, connection_url_var, browse_callback, remote_restore_callback):
        """Configura la pestaña de restauración remota"""
        row = 0
        
        # Archivo de backup
        self.remote_file_label = ctk.CTkLabel(
            self.tab_remote, 
            text="Archivo de backup:"
        )
        self.remote_file_label.grid(row=row, column=0, sticky="w", padx=10, pady=(10, 0))
        
        self.remote_file_frame = ctk.CTkFrame(self.tab_remote, fg_color="transparent")
        self.remote_file_frame.grid(row=row+1, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 10))
        self.remote_file_frame.columnconfigure(0, weight=1)
        
        self.remote_file_entry = ctk.CTkEntry(
            self.remote_file_frame, 
            textvariable=backup_file_var,  # Comparte la misma variable que la otra pestaña
            width=400
        )
        self.remote_file_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        
        self.remote_browse_button = ctk.CTkButton(
            self.remote_file_frame, 
            text="Examinar", 
            command=browse_callback,
            width=100
        )
        self.remote_browse_button.grid(row=0, column=1)
        
        row += 2
        
        # URL de conexión
        self.conn_label = ctk.CTkLabel(
            self.tab_remote, 
            text="URL de conexión de destino:"
        )
        self.conn_label.grid(row=row, column=0, sticky="w", padx=10, pady=(10, 0))
        
        self.conn_entry = ctk.CTkEntry(
            self.tab_remote, 
            textvariable=connection_url_var,
            width=500
        )
        self.conn_entry.grid(row=row+1, column=0, sticky="ew", padx=10, pady=(0, 10))
        
        # Ejemplo
        self.example_label = ctk.CTkLabel(
            self.tab_remote, 
            text="Ejemplo: postgresql://usuario:contraseña@servidor:5432/base_de_datos",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        self.example_label.grid(row=row+2, column=0, sticky="w", padx=10, pady=(0, 10))
        
        row += 3
        
        # Botón de restauración remota
        self.remote_restore_button = ctk.CTkButton(
            self.tab_remote, 
            text="Iniciar Restauración Remota", 
            command=remote_restore_callback
        )
        self.remote_restore_button.grid(row=row, column=0, padx=10, pady=10)
        
        # Configurar grid
        self.tab_remote.columnconfigure(0, weight=1)
    """Frame para la restauración de la base de datos"""
    
    def __init__(self, master, backup_file_var, container_name_var, database_name_var, 
                 username_var, connection_url_var, browse_callback, restore_callback, 
                 remote_restore_callback, **kwargs):
        super().__init__(master, **kwargs)
        
        # Crear un notebook con pestañas
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Pestañas para los diferentes métodos de restauración
        self.tab_local = self.tabview.add("Docker Local")
        self.tab_remote = self.tabview.add("Conexión Remota")
        
        # Pestaña por defecto
        self.tabview.set("Docker Local")
        
        # Configurar pestaña Docker Local
        self.setup_local_tab(backup_file_var, container_name_var, database_name_var, 
                           username_var, browse_callback, restore_callback)
        
        # Configurar pestaña Conexión Remota
        self.setup_remote_tab(backup_file_var, connection_url_var, browse_callback, 
                            remote_restore_callback)
    
    def setup_local_tab(self, backup_file_var, container_name_var, database_name_var, 
                       username_var, browse_callback, restore_callback):
        """Configura la pestaña de restauración local con Docker"""
        row = 0
        
        # Archivo de backup
        self.file_label = ctk.CTkLabel(
            self.tab_local, 
            text="Archivo de backup:"
        )
        self.file_label.grid(row=row, column=0, sticky="w", padx=10, pady=(10, 0))
        
        self.file_frame = ctk.CTkFrame(self.tab_local, fg_color="transparent")
        self.file_frame.grid(row=row+1, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 10))
        self.file_frame.columnconfigure(0, weight=1)
        
        self.file_entry = ctk.CTkEntry(
            self.file_frame, 
            textvariable=backup_file_var,
            width=400
        )
        self.file_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        
        self.browse_button = ctk.CTkButton(
            self.file_frame, 
            text="Examinar", 
            command=browse_callback,
            width=100
        )
        self.browse_button.grid(row=0, column=1)
        
        row += 2
        
        # Container name
        self.container_label = ctk.CTkLabel(
            self.tab_local, 
            text="Nombre del contenedor:"
        )
        self.container_label.grid(row=row, column=0, sticky="w", padx=10, pady=(10, 0))
        
        self.container_entry = ctk.CTkEntry(
            self.tab_local, 
            textvariable=container_name_var,
            width=500
        )
        self.container_entry.grid(row=row+1, column=0, sticky="ew", padx=10, pady=(0, 10))
        
        row += 2
        
        # Database name
        self.db_label = ctk.CTkLabel(
            self.tab_local, 
            text="Nombre de la base de datos:"
        )
        self.db_label.grid(row=row, column=0, sticky="w", padx=10, pady=(10, 0))
        
        self.db_entry = ctk.CTkEntry(
            self.tab_local, 
            textvariable=database_name_var,
            width=500
        )
        self.db_entry.grid(row=row+1, column=0, sticky="ew", padx=10, pady=(0, 10))
        
        row += 2
        
        # Username
        self.user_label = ctk.CTkLabel(
            self.tab_local, 
            text="Usuario de PostgreSQL:"
        )
        self.user_label.grid(row=row, column=0, sticky="w", padx=10, pady=(10, 0))
        
        self.user_entry = ctk.CTkEntry(
            self.tab_local, 
            textvariable=username_var,
            width=500
        )
        self.user_entry.grid(row=row+1, column=0, sticky="ew", padx=10, pady=(0, 10))
        
        row += 2
        
        # Botón de restauración
        self.restore_button = ctk.CTkButton(
            self.tab_local, 
            text="Iniciar Restauración en Docker Local", 
            command=restore_callback
        )
        self.restore_button.grid(row=row, column=0, padx=10, pady=10)
        
        # Configurar grid
        self.tab_local.columnconfigure(0, weight=1)
    
    def setup_remote_tab(self, backup_file_var, connection_url_var, browse_callback, remote_restore_callback):
        """Configura la pestaña de restauración remota"""
        row = 0
        
        # Archivo de backup
        self.remote_file_label = ctk.CTkLabel(
            self.tab_remote, 
            text="Archivo de backup:"
        )
        self.remote_file_label.grid(row=row, column=0, sticky="w", padx=10, pady=(10, 0))
        
        self.remote_file_frame = ctk.CTkFrame(self.tab_remote, fg_color="transparent")
        self.remote_file_frame.grid(row=row+1, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 10))
        self.remote_file_frame.columnconfigure(0, weight=1)
        
        self.remote_file_entry = ctk.CTkEntry(
            self.remote_file_frame, 
            textvariable=backup_file_var,  # Comparte la misma variable que la otra pestaña
            width=400
        )
        self.remote_file_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        
        self.remote_browse_button = ctk.CTkButton(
            self.remote_file_frame, 
            text="Examinar", 
            command=browse_callback,
            width=100
        )
        self.remote_browse_button.grid(row=0, column=1)
        
        row += 2
        
        # URL de conexión
        self.conn_label = ctk.CTkLabel(
            self.tab_remote, 
            text="URL de conexión de destino:"
        )
        self.conn_label.grid(row=row, column=0, sticky="w", padx=10, pady=(10, 0))
        
        self.conn_entry = ctk.CTkEntry(
            self.tab_remote, 
            textvariable=connection_url_var,
            width=500
        )
        self.conn_entry.grid(row=row+1, column=0, sticky="ew", padx=10, pady=(0, 10))
        
        # Ejemplo
        self.example_label = ctk.CTkLabel(
            self.tab_remote, 
            text="Ejemplo: postgresql://usuario:contraseña@servidor:5432/base_de_datos",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        self.example_label.grid(row=row+2, column=0, sticky="w", padx=10, pady=(0, 10))
        
        row += 3
        
        # Botón de restauración remota
        self.remote_restore_button = ctk.CTkButton(
            self.tab_remote, 
            text="Iniciar Restauración Remota", 
            command=remote_restore_callback
        )
        self.remote_restore_button.grid(row=row, column=0, padx=10, pady=10)
        
        # Configurar grid
        self.tab_remote.columnconfigure(0, weight=1)