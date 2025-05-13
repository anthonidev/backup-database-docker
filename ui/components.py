#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
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