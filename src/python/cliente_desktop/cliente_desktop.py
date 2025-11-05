#!/usr/bin/env python3
"""
Cliente de Escritorio - Banco Shibasito
Versión PURA: Solo tkinter + stdlib, SIN PIL, SIN pika, SIN qrcode
"""

import base64
import json
import socket
import threading
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, simpledialog, ttk

# Configuración del proxy
PROXY_HOST = "127.0.0.1"
PROXY_PORT = 9876
TIMEOUT = 30  # segundos


from src.python.common.proxy_client import ProxyClient


class LoanDialog(simpledialog.Dialog):
    def body(self, master):
        tk.Label(master, text="Monto a solicitar:").grid(row=0, sticky=tk.W)
        tk.Label(master, text="Plazo en meses:").grid(row=1, sticky=tk.W)
        self.e1 = tk.Entry(master)
        self.e2 = tk.Entry(master)
        self.e1.grid(row=0, column=1)
        self.e2.grid(row=1, column=1)
        return self.e1

    def apply(self):
        try:
            amount = float(self.e1.get())
            term = int(self.e2.get())
            self.result = (amount, term)
        except ValueError:
            messagebox.showerror(
                "Entrada inválida", "Por favor, ingrese valores numéricos válidos."
            )
            self.result = None


class TransferDialog(simpledialog.Dialog):
    def body(self, master):
        tk.Label(master, text="Cuenta Destino:").grid(row=0, sticky=tk.W)
        tk.Label(master, text="Monto:").grid(row=1, sticky=tk.W)
        tk.Label(master, text="Concepto:").grid(row=2, sticky=tk.W)
        self.e1 = tk.Entry(master)
        self.e2 = tk.Entry(master)
        self.e3 = tk.Entry(master)
        self.e1.grid(row=0, column=1)
        self.e2.grid(row=1, column=1)
        self.e3.grid(row=2, column=1)
        return self.e1

    def apply(self):
        try:
            to_account = int(self.e1.get())
            amount = float(self.e2.get())
            description = self.e3.get()
            self.result = (to_account, amount, description)
        except ValueError:
            messagebox.showerror(
                "Entrada inválida",
                "Por favor, ingrese un número de cuenta y monto válidos.",
            )
            self.result = None


class LoginWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.proxy_client = None
        self.user_data = None

        self.title("Banco Shibasito - Iniciar Sesión")
        self.geometry("350x200")
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.transient(parent)
        self.grab_set()

        tk.Label(self, text="DNI:").pack(pady=(10, 0))
        self.dni_entry = tk.Entry(self)
        self.dni_entry.pack(pady=5, padx=20, fill=tk.X)

        tk.Label(self, text="N° de Cuenta:").pack()
        self.account_entry = tk.Entry(self)
        self.account_entry.pack(pady=5, padx=20, fill=tk.X)

        self.login_button = tk.Button(self, text="Ingresar", command=self.attempt_login)
        self.login_button.pack(pady=15)

        self.status_label = tk.Label(self, text="", fg="red")
        self.status_label.pack()

    def on_closing(self):
        if self.proxy_client:
            self.proxy_client.close()
        self.parent.destroy()

    def attempt_login(self):
        self.login_button.config(state="disabled")
        threading.Thread(target=self._connection_and_login_thread, daemon=True).start()

    def _connection_and_login_thread(self):
        try:
            # 1. Conectar al proxy local
            self.status_label.config(text="Conectando con el servidor...", fg="blue")
            self.proxy_client = ProxyClient()
            self.proxy_client.connect()

            # 2. Validar entradas
            dni = self.dni_entry.get().strip()
            account = self.account_entry.get().strip()

            if not dni.isdigit() or len(dni) != 8:
                self.status_label.config(
                    text="DNI debe tener 8 dígitos numéricos.", fg="red"
                )
                self.login_button.config(state="normal")
                return

            if not account.isdigit():
                self.status_label.config(
                    text="N° de cuenta debe ser numérico.", fg="red"
                )
                self.login_button.config(state="normal")
                return

            # 3. Intentar login via proxy
            self.status_label.config(text="Validando credenciales...", fg="blue")
            payload = {"type": "LOGIN", "dni": dni, "account": int(account)}
            response = self.proxy_client.call(payload)

            if response and response.get("status") == "OK":
                self.user_data = response
                self.destroy()
            else:
                self.status_label.config(
                    text=response.get("error", "Credenciales inválidas"), fg="red"
                )
                self.login_button.config(state="normal")

        except ConnectionError as e:
            self.status_label.config(text=f"Error de conexión: {e}", fg="red")
            self.login_button.config(state="normal")
        except Exception as e:
            self.status_label.config(text=f"Error: {e}", fg="red")
            self.login_button.config(state="normal")


class ChatGUI:
    def __init__(self, root, proxy_client, user_data):
        self.root = root
        self.proxy_client = proxy_client
        self.session = user_data

        root.title(f"Banco Shibasito - {self.session.get('nombre', 'Usuario')}")
        root.geometry("960x600")
        root.protocol("WM_DELETE_WINDOW", self.on_closing)
        root.configure(bg="#f4f6f9")

        # Header
        header_frame = tk.Frame(root, bg="#d0e0f0")
        header_frame.pack(fill=tk.X, pady=(0, 5))

        user_info = f"Usuario: {self.session.get('nombre')} | Cuenta: {self.session.get('account')} | DNI: {self.session.get('dni')}"
        tk.Label(header_frame, text=user_info, bg="#d0e0f0").pack(side=tk.LEFT, padx=10)
        tk.Button(header_frame, text="Cerrar Sesión", command=self.logout).pack(
            side=tk.RIGHT, padx=10
        )

        main = tk.Frame(root, bg="#f4f6f9")
        main.pack(fill=tk.BOTH, expand=True)

        # Chat log
        chat_frame = tk.Frame(main, bg="white", bd=2, relief="groove")
        chat_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)

        tk.Label(
            chat_frame,
            text="Log de Operaciones",
            font=("Segoe UI", 12, "bold"),
            bg="white",
        ).pack(anchor="w", padx=10, pady=(5, 0))

        self.txt = tk.Text(
            chat_frame,
            height=10,
            state="disabled",
            wrap=tk.WORD,
            bg="#fdfdfd",
            fg="#222",
        )
        self.txt.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 5))
        self.txt.tag_config("success", background="#d4edda", foreground="#155724")
        self.txt.tag_config("error", background="#f8d7da", foreground="#721c24")
        self.txt.tag_config("info", foreground="#0078d7")

        # Botones
        button_frames = tk.Frame(main, bg="#f4f6f9")
        button_frames.pack(fill=tk.X, padx=10, pady=4)

        consultas_frame = tk.Frame(button_frames, bg="#f4f6f9")
        consultas_frame.pack(fill=tk.X)

        operaciones_frame = tk.Frame(button_frames, bg="#f4f6f9")
        operaciones_frame.pack(fill=tk.X, pady=2)

        utilidades_frame = tk.Frame(button_frames, bg="#f4f6f9")
        utilidades_frame.pack(fill=tk.X)

        self.buttons = []

        buttons_consultas = [
            ("Consultar Saldo", self.consultar_cuenta),
            ("Ver Transacciones", self.ver_transacciones),
            ("Estado Préstamos", self.ver_prestamos),
        ]
        buttons_operaciones = [
            ("Transferir Dinero", self.transferir_dinero),
            ("Solicitar Préstamo", self.solicitar_prestamo),
            ("Generar Mi QR", self.generar_qr_cobro),
        ]
        buttons_utilidades = [
            ("Limpiar Pantalla", self.clear_chat),
            ("Actualizar Datos", self.actualizar_datos),
        ]

        for text, cmd in buttons_consultas:
            btn = tk.Button(
                consultas_frame,
                text=text,
                command=cmd,
                width=20,
                bg="#e1e5ea",
                relief="groove",
            )
            btn.pack(side=tk.LEFT, padx=5)
            self.buttons.append(btn)

        for text, cmd in buttons_operaciones:
            btn = tk.Button(
                operaciones_frame,
                text=text,
                command=cmd,
                width=20,
                bg="#d1d5da",
                relief="groove",
            )
            btn.pack(side=tk.LEFT, padx=5)
            self.buttons.append(btn)

        for text, cmd in buttons_utilidades:
            btn = tk.Button(
                utilidades_frame,
                text=text,
                command=cmd,
                width=20,
                bg="#c1c5ca",
                relief="groove",
            )
            btn.pack(side=tk.LEFT, padx=5)
            self.buttons.append(btn)

        #Tabla
        self.table_frame = tk.Frame(main, bg="#f4f6f9")
        self.table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.tree = ttk.Treeview(
            self.table_frame, columns=("c1", "c2", "c3", "c4"), show="headings"
        )
        self.tree.pack(fill=tk.BOTH, expand=True)
        self._init_table(["ID", "Descripción", "Monto", "Fecha"])

    def _set_button_state(self, state):
        for btn in self.buttons:
            btn.config(state=state)

    def on_closing(self):
        self.proxy_client.close()
        self.root.destroy()

    def logout(self):
        self.root.destroy()
        main()

    def generar_qr_cobro(self):
        """Genera QR delegando TODO al proxy (imagen viene como base64)"""
        qr_window = tk.Toplevel(self.root)
        qr_window.title(f"Mi Código QR - Cuenta {self.session.get('account')}")
        qr_window.geometry("400x500")
        qr_window.resizable(False, False)
        qr_window.transient(self.root)
        qr_window.grab_set()

        try:
            # 1. Pedir al proxy que genere el QR
            qr_data = {
                "tipo": "pago_shibasito",
                "account_to": self.session.get("account"),
                "nombre_receptor": self.session.get("nombre"),
            }
            payload = {"type": "GENERAR_QR", "data": qr_data}

            self.append_text("Generando código QR...", "info")
            response = self.proxy_client.call(payload)

            if response.get("status") != "OK":
                raise Exception(response.get("error", "No se pudo generar el QR"))

            # 2. Decodificar la imagen de base64 y mostrarla
            qr_base64 = response.get("qr_image")
            qr_bytes = base64.b64decode(qr_base64)

            # Usar solo tkinter para mostrar la imagen (PhotoImage puede leer PNG desde bytes)
            qr_photo = tk.PhotoImage(data=qr_bytes)

            qr_label = tk.Label(qr_window, image=qr_photo)
            qr_label.image = qr_photo  # Mantener referencia
            qr_label.pack(pady=10)

            tk.Label(qr_window, text="Muestra este código a quien te pagará").pack()
            tk.Label(qr_window, text=f"Cuenta: {self.session.get('account')}").pack()
            tk.Label(qr_window, text=f"Titular: {self.session.get('nombre')}").pack(
                pady=(0, 10)
            )

            self.append_text("Código QR generado exitosamente", "success")

        except Exception as e:
            error_label = tk.Label(
                qr_window, text=f"Error al generar QR: {e}", fg="red"
            )
            error_label.pack(pady=20)
            self.append_text(f"Error generando QR: {e}", "error")

        tk.Button(qr_window, text="Cerrar", command=qr_window.destroy).pack()

    def transferir_dinero(self):
        dialog = TransferDialog(self.root, title="Transferir Dinero")
        if dialog.result:
            to_account, amount, description = dialog.result

            if to_account == self.session.get("account"):
                messagebox.showerror(
                    "Error", "No puede transferir dinero a su propia cuenta."
                )
                return

            if amount <= 0:
                messagebox.showerror("Error", "El monto debe ser positivo.")
                return

            if not messagebox.askyesno(
                "Confirmar Transferencia",
                f"¿Está seguro que desea transferir S/. {amount:.2f} a la cuenta {to_account}?",
            ):
                return

            payload = {
                "type": "TRANSFERIR_CUENTA",
                "from_account": self.session.get("account"),
                "to_account": to_account,
                "amount": amount,
                "description": description,
            }

            self.append_text(
                f"Iniciando transferencia de S/. {amount:.2f} a la cuenta {to_account}...",
                "info",
            )
            threading.Thread(
                target=self._do_generic_rpc, args=(payload,), daemon=True
            ).start()

    def solicitar_prestamo(self):
        dialog = LoanDialog(self.root, title="Solicitar Préstamo")
        if dialog.result:
            amount, term = dialog.result

            if amount <= 0 or term <= 0:
                messagebox.showerror(
                    "Error", "El monto y el plazo deben ser positivos."
                )
                return

            if not messagebox.askyesno(
                "Confirmar Préstamo",
                f"¿Está seguro que desea solicitar un préstamo de S/. {amount:.2f} a {term} meses?",
            ):
                return

            payload = {
                "type": "SOLICITAR_PRESTAMO",
                "account": self.session.get("account"),
                "dni": self.session.get("dni"),
                "monto": amount,
                "plazo_meses": term,
            }

            self.append_text(
                f"Enviando solicitud de préstamo por S/. {amount:.2f} a {term} meses...",
                "info",
            )
            threading.Thread(
                target=self._do_generic_rpc, args=(payload,), daemon=True
            ).start()

    def _do_generic_rpc(self, payload):
        self._set_button_state(tk.DISABLED)
        try:
            resp = self.proxy_client.call(payload)
            if resp and resp.get("status") == "OK":
                self.append_text(resp.get("message", "Operación exitosa."), "success")
                self.actualizar_datos()
            else:
                self.append_text(
                    f"Error: {resp.get('error', 'Ocurrió un error desconocido')}",
                    "error",
                )
        except Exception as e:
            self.append_text(f"Error de comunicación: {e}", "error")
        finally:
            self._set_button_state(tk.NORMAL)

    def _init_table(self, headers):
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = [f"c{i}" for i in range(1, len(headers) + 1)]
        for i, h in enumerate(headers, start=1):
            self.tree.heading(f"c{i}", text=h)
            self.tree.column(f"c{i}", width=150, anchor="center")

    def _fill_table(self, rows):
        self.tree.delete(*self.tree.get_children())
        for row in rows:
            self.tree.insert("", "end", values=row)

    def append_text(self, txt, sender="system"):
        self.txt.config(state="normal")
        ts = datetime.now().strftime("[%H:%M:%S] ")
        self.txt.insert(tk.END, ts + txt + "\n", sender)
        self.txt.config(state="disabled")
        self.txt.see(tk.END)

    def clear_chat(self):
        self.txt.config(state="normal")
        self.txt.delete("1.0", tk.END)
        self.txt.config(state="disabled")
        self._init_table(["ID", "Descripción", "Monto", "Fecha"])

    def actualizar_datos(self):
        self.append_text("Actualizando todos los datos...", "info")
        self.consultar_cuenta()
        self.ver_transacciones()
        self.ver_prestamos()

    def consultar_cuenta(self):
        payload = {"type": "CONSULTAR_CUENTA", "account": self.session.get("account")}
        threading.Thread(
            target=self._do_query_and_show, args=(payload, "cuenta"), daemon=True
        ).start()

    def ver_transacciones(self):
        payload = {
            "type": "CONSULTAR_TRANSACCIONES",
            "account": self.session.get("account"),
        }
        threading.Thread(
            target=self._do_query_and_show, args=(payload, "transacciones"), daemon=True
        ).start()

    def ver_prestamos(self):
        payload = {
            "type": "ESTADO_PAGO_PRESTAMO",
            "account": self.session.get("account"),
        }
        threading.Thread(
            target=self._do_query_and_show, args=(payload, "prestamos"), daemon=True
        ).start()

    def _do_query_and_show(self, payload, mode):
        self._set_button_state(tk.DISABLED)
        self.append_text(f"Consultando {mode}...", "info")
        try:
            resp = self.proxy_client.call(payload)
            if not isinstance(resp, dict) or resp.get("status") != "OK":
                self.append_text(
                    f"Error consultando {mode}: {resp.get('error', 'respuesta inválida')}",
                    "error",
                )
                return

            if mode == "cuenta":
                self._init_table(["Cuenta", "Saldo"])
                row = (resp.get("account"), resp.get("balance"))
                self._fill_table([row])
                self.append_text(
                    f"Saldo en cuenta {row[0]}: S/. {float(row[1]):.2f}", "success"
                )
            elif mode == "transacciones":
                self._init_table(["ID", "Concepto", "Monto", "Fecha"])
                data = resp.get("data", [])
                rows = [
                    (
                        d.get("id", "-"),
                        d.get("tipo", "-"),
                        d.get("monto", "-"),
                        d.get("fecha", "-"),
                    )
                    for d in data
                ]
                self._fill_table(rows)
                self.append_text(f"{len(rows)} transacciones encontradas.", "success")
            elif mode == "prestamos":
                self._init_table(["ID", "Monto pendiente", "Estado", "Fecha"])
                data = resp.get("data", [])
                rows = [
                    (
                        p.get("id_prestamo", "-"),
                        p.get("monto_pendiente", "-"),
                        p.get("estado", "-"),
                        p.get("fecha_solicitud", "-"),
                    )
                    for p in data
                ]
                self._fill_table(rows)
                self.append_text(f"{len(rows)} préstamos encontrados.", "success")
        except Exception as e:
            self.append_text(f"Error de comunicación consultando {mode}: {e}", "error")
        finally:
            self._set_button_state(tk.NORMAL)


def main():
    print("=== Iniciando Cliente Desktop Shibasito ===")
    root = tk.Tk()
    root.withdraw()  # Ocultar ventana principal

    login = LoginWindow(root)
    root.wait_window(login)

    if login.user_data:
        root.deiconify()
        app = ChatGUI(root, login.proxy_client, login.user_data)
        root.mainloop()
    else:
        if login.proxy_client:
            login.proxy_client.close()
        root.destroy()


if __name__ == "__main__":
    main()