#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cliente Desktop - Banco Shibasito
GUI moderna con Tkinter para operaciones bancarias
Incluye generación de códigos QR para transacciones móviles
"""

import json
import os
import sys
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, scrolledtext, ttk

# Agregar el path de common para importar ProxyClient
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "common"))

try:
    from proxy_client import ProxyClient
except ImportError:
    print("ERROR: No se pudo importar ProxyClient")
    print("Asegúrate de que el archivo common/proxy_client.py existe")
    sys.exit(1)

# Importar bibliotecas para QR
try:
    import qrcode
    from PIL import Image, ImageTk

    QR_AVAILABLE = True
except ImportError:
    print("⚠️  ADVERTENCIA: qrcode o Pillow no están instalados")
    print("Instala con: pip install qrcode[pil] pillow")
    QR_AVAILABLE = False


class BancoShibasitoGUI:
    """Interfaz gráfica principal del cliente desktop"""

    def __init__(self, root):
        self.root = root
        self.root.title("Banco Shibasito - Cliente Desktop")
        self.root.geometry("900x700")
        self.root.resizable(True, True)

        # Variables de sesión
        self.logged_in = False
        self.current_dni = None
        self.current_account = None
        self.current_name = None

        # Cliente proxy
        self.proxy = ProxyClient(host="localhost", port=9876)

        # Configurar estilos
        self.setup_styles()

        # Crear interfaz
        self.create_widgets()

        # Mostrar pantalla de login
        self.show_login_screen()

    def setup_styles(self):
        """Configurar estilos personalizados"""
        style = ttk.Style()
        style.theme_use("clam")

        # Colores del banco Shibasito
        bg_color = "#f0f4f8"
        primary_color = "#2563eb"
        secondary_color = "#10b981"
        danger_color = "#ef4444"

        self.root.configure(bg=bg_color)

        # Estilo para botones principales
        style.configure(
            "Primary.TButton",
            background=primary_color,
            foreground="white",
            padding=10,
            font=("Helvetica", 10, "bold"),
        )

        # Estilo para botones secundarios
        style.configure(
            "Secondary.TButton",
            background=secondary_color,
            foreground="white",
            padding=10,
            font=("Helvetica", 10, "bold"),
        )

        # Estilo para labels
        style.configure(
            "Title.TLabel",
            background=bg_color,
            foreground=primary_color,
            font=("Helvetica", 18, "bold"),
        )

        style.configure(
            "Subtitle.TLabel",
            background=bg_color,
            foreground="#475569",
            font=("Helvetica", 12),
        )

    def create_widgets(self):
        """Crear widgets principales"""
        # Frame contenedor principal
        self.main_container = ttk.Frame(self.root, padding="20")
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # Header
        self.header_frame = ttk.Frame(self.main_container)
        self.header_frame.pack(fill=tk.X, pady=(0, 20))

        self.title_label = ttk.Label(
            self.header_frame, text="🏦 Banco Shibasito", style="Title.TLabel"
        )
        self.title_label.pack(side=tk.LEFT)

        self.user_label = ttk.Label(self.header_frame, text="", style="Subtitle.TLabel")
        self.user_label.pack(side=tk.RIGHT)

        # Frame de contenido (cambiará según la pantalla)
        self.content_frame = ttk.Frame(self.main_container)
        self.content_frame.pack(fill=tk.BOTH, expand=True)

    def clear_content(self):
        """Limpiar el frame de contenido"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    # ============================================
    # PANTALLA DE LOGIN
    # ============================================

    def show_login_screen(self):
        """Mostrar pantalla de inicio de sesión"""
        self.clear_content()
        self.user_label.config(text="")

        # Frame centrado para login
        login_frame = ttk.Frame(self.content_frame)
        login_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # Título
        ttk.Label(login_frame, text="Iniciar Sesión", style="Title.TLabel").grid(
            row=0, column=0, columnspan=2, pady=(0, 20)
        )

        # Campo DNI
        ttk.Label(login_frame, text="DNI:", font=("Helvetica", 11)).grid(
            row=1, column=0, sticky=tk.W, pady=5
        )
        self.dni_entry = ttk.Entry(login_frame, width=30, font=("Helvetica", 11))
        self.dni_entry.grid(row=1, column=1, pady=5, padx=10)

        # Campo Cuenta
        ttk.Label(login_frame, text="N° Cuenta:", font=("Helvetica", 11)).grid(
            row=2, column=0, sticky=tk.W, pady=5
        )
        self.account_entry = ttk.Entry(login_frame, width=30, font=("Helvetica", 11))
        self.account_entry.grid(row=2, column=1, pady=5, padx=10)

        # Botón login
        ttk.Button(
            login_frame, text="Ingresar", style="Primary.TButton", command=self.do_login
        ).grid(row=3, column=0, columnspan=2, pady=20)

        # Bind Enter key
        self.dni_entry.bind("<Return>", lambda e: self.do_login())
        self.account_entry.bind("<Return>", lambda e: self.do_login())

        # Focus en DNI
        self.dni_entry.focus()

    def do_login(self):
        """Ejecutar login"""
        dni = self.dni_entry.get().strip()
        account = self.account_entry.get().strip()

        if not dni or not account:
            messagebox.showerror("Error", "Complete todos los campos")
            return

        if not dni.isdigit() or len(dni) != 8:
            messagebox.showerror("Error", "DNI debe tener 8 dígitos")
            return

        if not account.isdigit():
            messagebox.showerror("Error", "Número de cuenta inválido")
            return

        # Intentar login
        try:
            response = self.proxy.send_request(
                {"operacion": "LOGIN", "dni": dni, "id_cuenta": int(account)}
            )

            if response.get("status") == "OK":
                self.logged_in = True
                self.current_dni = dni
                self.current_account = int(account)
                self.current_name = response.get("data", {}).get(
                    "nombre_completo", "Usuario"
                )

                messagebox.showinfo(
                    "Bienvenido",
                    f"¡Hola {self.current_name}!\n\nSesión iniciada correctamente",
                )
                self.show_main_menu()
            else:
                messagebox.showerror(
                    "Error de Login", response.get("message", "Credenciales inválidas")
                )
        except Exception as e:
            messagebox.showerror(
                "Error de Conexión", f"No se pudo conectar al servidor:\n{e}"
            )

    # ============================================
    # MENÚ PRINCIPAL
    # ============================================

    def show_main_menu(self):
        """Mostrar menú principal después del login"""
        self.clear_content()
        self.user_label.config(
            text=f"👤 {self.current_name} | Cuenta: {self.current_account}"
        )

        # Crear grid de botones
        menu_frame = ttk.Frame(self.content_frame)
        menu_frame.pack(expand=True)

        buttons = [
            ("💰 Consultar Saldo", self.show_balance_screen, "Primary.TButton"),
            ("💸 Transferir Dinero", self.show_transfer_screen, "Secondary.TButton"),
            ("💳 Solicitar Préstamo", self.show_loan_screen, "Secondary.TButton"),
            ("📋 Historial", self.show_history_screen, "Primary.TButton"),
            ("📱 Generar QR", self.show_qr_screen, "Secondary.TButton"),
            ("🚪 Cerrar Sesión", self.logout, "Primary.TButton"),
        ]

        row, col = 0, 0
        for text, command, style in buttons:
            btn = ttk.Button(
                menu_frame, text=text, style=style, command=command, width=25
            )
            btn.grid(row=row, column=col, padx=10, pady=10, sticky="ew")
            col += 1
            if col > 1:
                col = 0
                row += 1

    def logout(self):
        """Cerrar sesión"""
        self.logged_in = False
        self.current_dni = None
        self.current_account = None
        self.current_name = None
        self.show_login_screen()

    # ============================================
    # PANTALLA DE SALDO
    # ============================================

    def show_balance_screen(self):
        """Mostrar consulta de saldo"""
        self.clear_content()

        ttk.Label(
            self.content_frame, text="💰 Consultar Saldo", style="Title.TLabel"
        ).pack(pady=20)

        # Frame de información
        info_frame = ttk.LabelFrame(
            self.content_frame, text="Información de Cuenta", padding=20
        )
        info_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Consultar saldo
        try:
            response = self.proxy.send_request(
                {"operacion": "CONSULTAR_CUENTA", "id_cuenta": self.current_account}
            )

            if response.get("status") == "OK":
                saldo = float(response.get("balance", 0.0))

                ttk.Label(
                    info_frame,
                    text=f"Cuenta N°: {self.current_account}",
                    font=("Helvetica", 14),
                ).pack(pady=5)

                ttk.Label(
                    info_frame,
                    text=f"Titular: {self.current_name}",
                    font=("Helvetica", 12),
                ).pack(pady=5)

                ttk.Label(
                    info_frame, text="Saldo Actual:", font=("Helvetica", 12)
                ).pack(pady=10)

                ttk.Label(
                    info_frame,
                    text=f"S/ {saldo:,.2f}",
                    font=("Helvetica", 24, "bold"),
                    foreground="#10b981",
                ).pack(pady=10)
            else:
                messagebox.showerror(
                    "Error", response.get("message", "Error al consultar saldo")
                )
        except Exception as e:
            messagebox.showerror("Error", f"Error de conexión: {e}")

        # Botón volver
        ttk.Button(
            self.content_frame,
            text="⬅️ Volver al Menú",
            style="Primary.TButton",
            command=self.show_main_menu,
        ).pack(pady=20)

    # ============================================
    # PANTALLA DE TRANSFERENCIA
    # ============================================

    def show_transfer_screen(self):
        """Mostrar pantalla de transferencia"""
        self.clear_content()

        ttk.Label(
            self.content_frame, text="💸 Transferir Dinero", style="Title.TLabel"
        ).pack(pady=20)

        # Frame de formulario
        form_frame = ttk.LabelFrame(
            self.content_frame, text="Datos de Transferencia", padding=20
        )
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Cuenta destino
        ttk.Label(form_frame, text="Cuenta Destino:", font=("Helvetica", 11)).grid(
            row=0, column=0, sticky=tk.W, pady=10
        )
        self.transfer_account_entry = ttk.Entry(
            form_frame, width=30, font=("Helvetica", 11)
        )
        self.transfer_account_entry.grid(row=0, column=1, pady=10, padx=10)

        # Monto
        ttk.Label(form_frame, text="Monto (S/):", font=("Helvetica", 11)).grid(
            row=1, column=0, sticky=tk.W, pady=10
        )
        self.transfer_amount_entry = ttk.Entry(
            form_frame, width=30, font=("Helvetica", 11)
        )
        self.transfer_amount_entry.grid(row=1, column=1, pady=10, padx=10)

        # Botón transferir
        ttk.Button(
            form_frame,
            text="✅ Realizar Transferencia",
            style="Secondary.TButton",
            command=self.do_transfer,
        ).grid(row=2, column=0, columnspan=2, pady=20)

        # Botón volver
        ttk.Button(
            self.content_frame,
            text="⬅️ Volver al Menú",
            style="Primary.TButton",
            command=self.show_main_menu,
        ).pack(pady=20)

    def do_transfer(self):
        """Ejecutar transferencia"""
        cuenta_destino = self.transfer_account_entry.get().strip()
        monto_str = self.transfer_amount_entry.get().strip()

        if not cuenta_destino or not monto_str:
            messagebox.showerror("Error", "Complete todos los campos")
            return

        try:
            cuenta_destino = int(cuenta_destino)
            monto = float(monto_str)

            if monto <= 0:
                messagebox.showerror("Error", "El monto debe ser mayor a 0")
                return

            if cuenta_destino == self.current_account:
                messagebox.showerror("Error", "No puedes transferir a tu misma cuenta")
                return

            # Confirmar
            if not messagebox.askyesno(
                "Confirmar Transferencia",
                f"¿Deseas transferir S/ {monto:.2f} a la cuenta {cuenta_destino}?",
            ):
                return

            # Realizar transferencia
            response = self.proxy.send_request(
                {
                    "operacion": "TRANSFERIR_CUENTA",
                    "cuenta_origen": self.current_account,
                    "cuenta_destino": cuenta_destino,
                    "monto": monto,
                }
            )

            if response.get("status") == "OK":
                messagebox.showinfo(
                    "Éxito",
                    f"✅ Transferencia completada\n\nMonto: S/ {monto:.2f}\nDestino: {cuenta_destino}",
                )
                self.transfer_account_entry.delete(0, tk.END)
                self.transfer_amount_entry.delete(0, tk.END)
            else:
                messagebox.showerror(
                    "Error", response.get("message", "Error al realizar transferencia")
                )
        except ValueError:
            messagebox.showerror("Error", "Monto o cuenta inválidos")
        except Exception as e:
            messagebox.showerror("Error", f"Error de conexión: {e}")

    # ============================================
    # PANTALLA DE PRÉSTAMO
    # ============================================

    def show_loan_screen(self):
        """Mostrar pantalla de solicitud de préstamo"""
        self.clear_content()

        ttk.Label(
            self.content_frame, text="💳 Solicitar Préstamo", style="Title.TLabel"
        ).pack(pady=20)

        # Frame de formulario
        form_frame = ttk.LabelFrame(
            self.content_frame, text="Datos del Préstamo", padding=20
        )
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Monto
        ttk.Label(form_frame, text="Monto (S/):", font=("Helvetica", 11)).grid(
            row=0, column=0, sticky=tk.W, pady=10
        )
        self.loan_amount_entry = ttk.Entry(form_frame, width=30, font=("Helvetica", 11))
        self.loan_amount_entry.grid(row=0, column=1, pady=10, padx=10)

        # Plazo en meses
        ttk.Label(form_frame, text="Plazo (meses):", font=("Helvetica", 11)).grid(
            row=1, column=0, sticky=tk.W, pady=10
        )
        self.loan_term_entry = ttk.Entry(form_frame, width=30, font=("Helvetica", 11))
        self.loan_term_entry.grid(row=1, column=1, pady=10, padx=10)
        self.loan_term_entry.insert(0, "12")

        # Botón solicitar
        ttk.Button(
            form_frame,
            text="✅ Solicitar Préstamo",
            style="Secondary.TButton",
            command=self.do_loan_request,
        ).grid(row=2, column=0, columnspan=2, pady=20)

        # Botón volver
        ttk.Button(
            self.content_frame,
            text="⬅️ Volver al Menú",
            style="Primary.TButton",
            command=self.show_main_menu,
        ).pack(pady=20)

    def do_loan_request(self):
        """Ejecutar solicitud de préstamo"""
        monto_str = self.loan_amount_entry.get().strip()
        plazo_str = self.loan_term_entry.get().strip()

        if not monto_str or not plazo_str:
            messagebox.showerror("Error", "Complete todos los campos")
            return

        try:
            monto = float(monto_str)
            plazo = int(plazo_str)

            if monto <= 0:
                messagebox.showerror("Error", "El monto debe ser mayor a 0")
                return

            if plazo <= 0 or plazo > 360:
                messagebox.showerror("Error", "El plazo debe estar entre 1 y 360 meses")
                return

            # Confirmar
            if not messagebox.askyesno(
                "Confirmar Préstamo",
                f"¿Deseas solicitar un préstamo de S/ {monto:.2f} a {plazo} meses?",
            ):
                return

            # Solicitar préstamo
            response = self.proxy.send_request(
                {
                    "operacion": "SOLICITAR_PRESTAMO",
                    "dni": self.current_dni,
                    "id_cuenta": self.current_account,
                    "monto": monto,
                    "plazo_meses": plazo,
                }
            )

            if response.get("status") == "OK":
                data = response.get("data", {})
                messagebox.showinfo(
                    "Préstamo Aprobado",
                    f"✅ ¡Préstamo aprobado!\n\n"
                    f"Monto: S/ {monto:.2f}\n"
                    f"Plazo: {plazo} meses\n"
                    f"ID Préstamo: {data.get('id_prestamo', 'N/A')}",
                )
                self.loan_amount_entry.delete(0, tk.END)
                self.loan_term_entry.delete(0, tk.END)
                self.loan_term_entry.insert(0, "12")
            else:
                messagebox.showerror(
                    "Error", response.get("message", "Error al solicitar préstamo")
                )
        except ValueError:
            messagebox.showerror("Error", "Monto o plazo inválidos")
        except Exception as e:
            messagebox.showerror("Error", f"Error de conexión: {e}")

    # ============================================
    # PANTALLA DE HISTORIAL
    # ============================================

    def show_history_screen(self):
        """Mostrar historial de transacciones REAL"""
        self.clear_content()

        ttk.Label(
            self.content_frame,
            text="📋 Historial de Transacciones",
            style="Title.TLabel",
        ).pack(pady=20)

        # Frame de historial
        history_frame = ttk.LabelFrame(
            self.content_frame, text="Últimas Operaciones", padding=20
        )
        history_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Área de texto con scroll
        text_area = scrolledtext.ScrolledText(
            history_frame, width=100, height=25, font=("Courier", 10), wrap=tk.NONE
        )
        text_area.pack(fill=tk.BOTH, expand=True)

        # Consultar historial
        try:
            response = self.proxy.send_request(
                {
                    "operacion": "CONSULTAR_HISTORIAL",
                    "id_cuenta": self.current_account,
                    "limit": 20,
                }
            )

            if response.get("status") == "OK":
                transacciones = response.get("data", {}).get("transacciones", [])

                if not transacciones:
                    text_area.insert(tk.END, "📃 No hay transacciones registradas\n\n")
                else:
                    # Header
                    text_area.insert(tk.END, "=" * 90 + "\n")
                    text_area.insert(
                        tk.END, f"{'ID':<8} {'TIPO':<15} {'MONTO':>12} {'FECHA':<25}\n"
                    )
                    text_area.insert(tk.END, "=" * 90 + "\n\n")

                    # Transacciones
                    for tx in transacciones:
                        tx_id = tx.get("id", "N/A")
                        tipo = tx.get("tipo", "DESCONOCIDO")
                        monto = float(tx.get("monto", 0.0))
                        fecha = tx.get("fecha", "N/A")

                        # Formatear fecha (quitar microsegundos)
                        if "." in fecha:
                            fecha = fecha.split(".")[0]

                        # Color según tipo
                        prefix = "  ➡️ " if "CREDITO" in tipo.upper() else "  ⬅️ "
                        signo = "+" if "CREDITO" in tipo.upper() else ""

                        line = f"{prefix}{tx_id:<6} {tipo:<15} {signo}S/ {monto:>9.2f}   {fecha}\n"
                        text_area.insert(tk.END, line)

                    text_area.insert(tk.END, "\n" + "=" * 90 + "\n")
                    text_area.insert(
                        tk.END, f"Total de transacciones: {len(transacciones)}\n"
                    )

            else:
                text_area.insert(tk.END, "❌ Error al consultar historial\n\n")
                text_area.insert(tk.END, response.get("message", "Error desconocido"))

        except Exception as e:
            text_area.insert(tk.END, f"❌ Error de conexión: {e}\n")

        text_area.config(state=tk.DISABLED)

        # Botón volver
        ttk.Button(
            self.content_frame,
            text="⬅️ Volver al Menú",
            style="Primary.TButton",
            command=self.show_main_menu,
        ).pack(pady=20)

    # ============================================
    # PANTALLA DE CÓDIGO QR
    # ============================================

    def show_qr_screen(self):
        """Mostrar generación de código QR para app móvil"""
        self.clear_content()

        ttk.Label(
            self.content_frame, text="📱 Generar Código QR", style="Title.TLabel"
        ).pack(pady=20)

        if not QR_AVAILABLE:
            ttk.Label(
                self.content_frame,
                text="⚠️ Biblioteca QR no disponible\n\nInstala con: pip install qrcode[pil] pillow",
                font=("Helvetica", 12),
                foreground="#ef4444",
            ).pack(pady=20)

            ttk.Button(
                self.content_frame,
                text="⬅️ Volver al Menú",
                style="Primary.TButton",
                command=self.show_main_menu,
            ).pack(pady=20)
            return

        # Frame de formulario
        form_frame = ttk.LabelFrame(
            self.content_frame, text="Datos para QR", padding=20
        )
        form_frame.pack(fill=tk.X, padx=20, pady=20)

        # Tipo de operación
        ttk.Label(form_frame, text="Operación:", font=("Helvetica", 11)).grid(
            row=0, column=0, sticky=tk.W, pady=10
        )
        self.qr_operation_var = tk.StringVar(value="TRANSFERENCIA")
        operations = ["TRANSFERENCIA", "PAGO", "SOLICITUD_SALDO"]
        self.qr_operation_combo = ttk.Combobox(
            form_frame,
            textvariable=self.qr_operation_var,
            values=operations,
            state="readonly",
            width=28,
            font=("Helvetica", 11),
        )
        self.qr_operation_combo.grid(row=0, column=1, pady=10, padx=10)

        # Monto
        ttk.Label(form_frame, text="Monto (S/):", font=("Helvetica", 11)).grid(
            row=1, column=0, sticky=tk.W, pady=10
        )
        self.qr_amount_entry = ttk.Entry(form_frame, width=30, font=("Helvetica", 11))
        self.qr_amount_entry.grid(row=1, column=1, pady=10, padx=10)

        # Botón generar
        ttk.Button(
            form_frame,
            text="🎯 Generar Código QR",
            style="Secondary.TButton",
            command=self.generate_qr,
        ).grid(row=2, column=0, columnspan=2, pady=20)

        # Frame para mostrar QR
        self.qr_display_frame = ttk.LabelFrame(
            self.content_frame, text="Código QR Generado", padding=20
        )
        self.qr_display_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        ttk.Label(
            self.qr_display_frame,
            text="👆 Complete los datos y genere el código QR",
            font=("Helvetica", 11),
        ).pack(pady=40)

        # Botón volver
        ttk.Button(
            self.content_frame,
            text="⬅️ Volver al Menú",
            style="Primary.TButton",
            command=self.show_main_menu,
        ).pack(pady=20)

    def generate_qr(self):
        """Generar código QR con datos de transacción"""
        operation = self.qr_operation_var.get()
        monto_str = self.qr_amount_entry.get().strip()

        if not monto_str:
            messagebox.showerror("Error", "Ingrese un monto")
            return

        try:
            monto = float(monto_str)
            if monto <= 0:
                messagebox.showerror("Error", "El monto debe ser mayor a 0")
                return

            # Crear datos del QR
            qr_data = {
                "tipo": operation,
                "cuenta_destino": self.current_account,
                "monto": monto,
                "timestamp": datetime.now().isoformat(),
                "banco": "Shibasito",
            }

            # Generar QR
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(json.dumps(qr_data))
            qr.make(fit=True)

            # Crear imagen
            img = qr.make_image(fill_color="black", back_color="white")

            # Convertir para Tkinter
            img = img.resize((300, 300))
            photo = ImageTk.PhotoImage(img)

            # Limpiar frame de display
            for widget in self.qr_display_frame.winfo_children():
                widget.destroy()

            # Mostrar QR
            qr_label = ttk.Label(self.qr_display_frame, image=photo)
            qr_label.image = photo  # Mantener referencia
            qr_label.pack(pady=10)

            # Instrucciones
            ttk.Label(
                self.qr_display_frame,
                text="📱 Escanea este código con la app móvil",
                font=("Helvetica", 11, "bold"),
            ).pack(pady=10)

            ttk.Label(
                self.qr_display_frame,
                text=f"Operación: {operation}\nMonto: S/ {monto:.2f}\nCuenta: {self.current_account}",
                font=("Helvetica", 10),
            ).pack(pady=5)

        except ValueError:
            messagebox.showerror("Error", "Monto inválido")
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar QR: {e}")


def main():
    """Función principal"""
    root = tk.Tk()
    app = BancoShibasitoGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
