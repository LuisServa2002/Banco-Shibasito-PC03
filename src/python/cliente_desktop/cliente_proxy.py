#!/usr/bin/env python3
"""
Proxy Local: Intermediario entre la GUI de escritorio y RabbitMQ.
Resuelve el conflicto de bajo nivel entre pika y tkinter.
"""

import base64
import io
import json
import os
import signal
import socket
import sys
import threading
from datetime import datetime

import qrcode

# Añadir el directorio raíz del proyecto al path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
sys.path.append(ROOT_DIR)

from src.python.common.rpc_client import RpcClient

# Configuración
PROXY_HOST = "127.0.0.1"
PROXY_PORT = 9876
BUFFER_SIZE = 8192


class ClienteProxy:
    """Proxy que gestiona conexiones entre GUI y RabbitMQ"""

    def __init__(self):
        self.rpc_client = None
        self.server_socket = None
        self.running = False
        self.log_lock = threading.Lock()
        self.rabbitmq_lock = threading.Lock()  # Lock para operaciones RabbitMQ

    def log(self, mensaje, nivel="INFO"):
        """Log thread-safe con timestamp"""
        with self.log_lock:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] [{nivel}] {mensaje}", flush=True)

    def conectar_rabbitmq(self):
        """Establece conexión con RabbitMQ"""
        try:
            self.log("Conectando con RabbitMQ...")
            self.rpc_client = RpcClient()
            self.rpc_client.connect()
            self.log("✓ Conexión con RabbitMQ establecida", "SUCCESS")
            return True
        except Exception as e:
            self.log(f"✗ Error conectando con RabbitMQ: {e}", "ERROR")
            return False

    def reconectar_rabbitmq(self):
        """Reconecta a RabbitMQ si la conexión se perdió"""
        with self.rabbitmq_lock:
            try:
                # Cerrar conexión anterior si existe
                if self.rpc_client:
                    try:
                        self.rpc_client.close()
                    except:
                        pass

                self.log("Reconectando a RabbitMQ...", "WARNING")
                return self.conectar_rabbitmq()
            except Exception as e:
                self.log(f"Error en reconexión: {e}", "ERROR")
                return False

    def verificar_conexion_rabbitmq(self):
        """Verifica si la conexión con RabbitMQ está activa"""
        try:
            if not self.rpc_client:
                return False
            if not self.rpc_client.connection or self.rpc_client.connection.is_closed:
                return False
            if not self.rpc_client.channel or self.rpc_client.channel.is_closed:
                return False
            return True
        except:
            return False

    def iniciar_servidor(self):
        """Inicia el servidor TCP local"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((PROXY_HOST, PROXY_PORT))
            self.server_socket.listen(5)
            self.running = True
            self.log(f"✓ Proxy escuchando en {PROXY_HOST}:{PROXY_PORT}", "SUCCESS")
            return True
        except Exception as e:
            self.log(f"✗ Error iniciando servidor TCP: {e}", "ERROR")
            return False

    def manejar_cliente(self, client_socket, addr):
        """Maneja una conexión de cliente (GUI)"""
        cliente_id = f"{addr[0]}:{addr[1]}"
        self.log(f"Nueva conexión desde {cliente_id}")

        try:
            while self.running:
                data = client_socket.recv(BUFFER_SIZE)
                if not data:
                    self.log(f"Cliente {cliente_id} desconectado")
                    break

                try:
                    mensaje = json.loads(data.decode("utf-8"))
                    tipo_operacion = mensaje.get("operacion", "DESCONOCIDO")
                    self.log(f"← Recibido de {cliente_id}: {tipo_operacion}")

                    if tipo_operacion == "GENERAR_QR":
                        qr_data = mensaje.get("data", {})
                        qr_json = json.dumps(qr_data)

                        # Generar imagen en memoria
                        qr_img = qrcode.make(qr_json)
                        buffered = io.BytesIO()
                        qr_img.save(buffered, format="PNG")

                        # Codificar en base64
                        qr_base64 = base64.b64encode(buffered.getvalue()).decode(
                            "utf-8"
                        )

                        respuesta = {"status": "OK", "qr_image": qr_base64}
                    else:
                        # Verificar conexión RabbitMQ antes de enviar
                        if not self.verificar_conexion_rabbitmq():
                            self.log(
                                "Conexión RabbitMQ perdida. Reconectando...", "WARNING"
                            )
                            if not self.reconectar_rabbitmq():
                                raise Exception("No se pudo reconectar a RabbitMQ")

                        # Transformar operacion -> type para RabbitMQ
                        mensaje["type"] = mensaje.pop("operacion")

                        # Transformar id_cuenta -> account
                        if "id_cuenta" in mensaje:
                            mensaje["account"] = mensaje.pop("id_cuenta")

                        # Transformar campos de transferencia
                        if "cuenta_origen" in mensaje:
                            mensaje["from_account"] = mensaje.pop("cuenta_origen")
                        if "cuenta_destino" in mensaje:
                            mensaje["to_account"] = mensaje.pop("cuenta_destino")
                        if "monto" in mensaje:
                            mensaje["amount"] = mensaje.pop("monto")
                        if (
                            mensaje.get("type") == "SOLICITAR_PRESTAMO"
                            and "amount" in mensaje
                        ):
                            mensaje["monto"] = mensaje.pop("amount")
                        # Enviar a RabbitMQ con lock para thread-safety
                        with self.rabbitmq_lock:
                            respuesta = self.rpc_client.call(mensaje)

                    respuesta_json = json.dumps(respuesta) + "\n"
                    client_socket.sendall(respuesta_json.encode("utf-8"))

                    estado = respuesta.get("status", "UNKNOWN")
                    self.log(
                        f"→ Respuesta enviada a {cliente_id}: {estado}",
                        "SUCCESS" if estado == "OK" else "WARNING",
                    )

                except json.JSONDecodeError as e:
                    self.log(f"Error decodificando JSON de {cliente_id}: {e}", "ERROR")
                    error_resp = {"status": "ERROR", "error": "JSON inválido"}
                    client_socket.sendall(
                        (json.dumps(error_resp) + "\n").encode("utf-8")
                    )

                except Exception as e:
                    self.log(f"Error procesando mensaje de {cliente_id}: {e}", "ERROR")
                    error_resp = {"status": "ERROR", "error": str(e)}
                    client_socket.sendall(
                        (json.dumps(error_resp) + "\n").encode("utf-8")
                    )

        except Exception as e:
            self.log(f"Error en conexión con {cliente_id}: {e}", "ERROR")

        finally:
            client_socket.close()
            self.log(f"Conexión cerrada con {cliente_id}")

    def ejecutar(self):
        """Loop principal del proxy"""
        self.log("=== Iniciando Cliente Proxy ===")

        # 1. Conectar con RabbitMQ
        if not self.conectar_rabbitmq():
            self.log("No se pudo conectar con RabbitMQ. Abortando.", "ERROR")
            return 1

        # 2. Iniciar servidor TCP
        if not self.iniciar_servidor():
            self.log("No se pudo iniciar el servidor TCP. Abortando.", "ERROR")
            return 1

        self.log("=== Proxy operativo. Esperando conexiones de GUI ===")

        try:
            while self.running:
                try:
                    # Aceptar conexiones entrantes
                    client_socket, addr = self.server_socket.accept()

                    # Crear hilo para manejar el cliente
                    cliente_thread = threading.Thread(
                        target=self.manejar_cliente,
                        args=(client_socket, addr),
                        daemon=True,
                    )
                    cliente_thread.start()

                except socket.timeout:
                    continue
                except Exception as e:
                    if self.running:
                        self.log(f"Error aceptando conexión: {e}", "ERROR")

        except KeyboardInterrupt:
            self.log("\n=== Interrupción recibida. Cerrando proxy ===", "WARNING")

        finally:
            self.detener()

        return 0

    def detener(self):
        """Cierra todas las conexiones y detiene el proxy"""
        self.log("Cerrando conexiones...")
        self.running = False

        if self.server_socket:
            try:
                self.server_socket.close()
                self.log("✓ Servidor TCP cerrado")
            except Exception as e:
                self.log(f"Error cerrando servidor TCP: {e}", "ERROR")

        if self.rpc_client:
            try:
                self.rpc_client.close()
                self.log("✓ Conexión RabbitMQ cerrada")
            except Exception as e:
                self.log(f"Error cerrando RabbitMQ: {e}", "ERROR")

        self.log("=== Proxy detenido ===")


def signal_handler(signum, frame):
    """Maneja señales de interrupción"""
    print("\n[SIGNAL] Señal recibida. Deteniendo proxy...")
    sys.exit(0)


def main():
    # Registrar manejador de señales
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Crear e iniciar proxy
    proxy = ClienteProxy()
    exit_code = proxy.ejecutar()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
