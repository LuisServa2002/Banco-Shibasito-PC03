#!/usr/bin/env python3

import json
import socket


class ProxyClient:
    """Cliente que se comunica con el proxy local via TCP"""

    def __init__(self, host="127.0.0.1", port=9876):
        """
        Inicializa el cliente del proxy

        Args:
            host: Dirección del proxy (por defecto localhost)
            port: Puerto del proxy (por defecto 9876)
        """
        self.host = host
        self.port = port
        self.timeout = 30  # segundos

    def send_request(self, payload):
        """
        Envía un mensaje al proxy y espera respuesta

        Args:
            payload: Diccionario con la solicitud

        Returns:
            Diccionario con la respuesta del servidor
        """
        try:
            # Crear socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            sock.connect((self.host, self.port))

            # Enviar mensaje
            mensaje_json = json.dumps(payload) + "\n"
            sock.sendall(mensaje_json.encode("utf-8"))

            # Recibir respuesta
            buffer = b""
            while True:
                chunk = sock.recv(8192)
                if not chunk:
                    break
                buffer += chunk
                # El proxy envía JSON completo seguido de nueva línea
                if b"\n" in buffer:
                    break

            sock.close()

            # Parsear respuesta
            respuesta = json.loads(buffer.decode("utf-8").strip())
            return respuesta

        except socket.timeout:
            return {
                "status": "error",
                "message": "Timeout: El servidor no respondió a tiempo",
            }
        except ConnectionRefusedError:
            return {
                "status": "error",
                "message": "Conexión rechazada. Asegúrate que el proxy esté corriendo en el puerto 9876",
            }
        except json.JSONDecodeError as e:
            return {"status": "error", "message": f"Error decodificando respuesta: {e}"}
        except Exception as e:
            return {"status": "error", "message": f"Error de conexión: {e}"}

    def connect(self):
        """Método de compatibilidad (no hace nada, la conexión es por request)"""
        pass

    def call(self, payload):
        """Alias de send_request para compatibilidad"""
        return self.send_request(payload)

    def close(self):
        """Método de compatibilidad (no hay conexión persistente)"""
        pass
