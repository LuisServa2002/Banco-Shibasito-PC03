import json
import os
import sqlite3
import sys
import time

import pika

# Simplificar la modificación del path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

DB_PATH = os.path.join("db_reniec", "reniec.db")
RENIEC_QUEUE = "reniec_queue"


class ReniecWorker:
    def __init__(self):
        self.db_path = DB_PATH
        self._init_rabbitmq()

    def _init_rabbitmq(self):
        """Inicializa conexión a RabbitMQ con reintentos."""
        max_attempts = 5
        retry_delay = 3

        for attempt in range(1, max_attempts + 1):
            try:
                print(
                    f"[ReniecWorker] Intento {attempt}/{max_attempts} de conexión a RabbitMQ...",
                    flush=True,
                )
                self.connection = pika.BlockingConnection(
                    pika.ConnectionParameters(
                        host="localhost", connection_attempts=3, retry_delay=2
                    )
                )
                self.channel = self.connection.channel()
                self.channel.queue_declare(queue=RENIEC_QUEUE, durable=True)
                print("[ReniecWorker] ✓ Conectado exitosamente a RabbitMQ", flush=True)
                print(
                    f"[ReniecWorker] ✓ Escuchando en cola '{RENIEC_QUEUE}'", flush=True
                )
                return
            except Exception as e:
                print(f"[ReniecWorker] ✗ Error en intento {attempt}: {e}", flush=True)
                if attempt < max_attempts:
                    print(
                        f"[ReniecWorker] Reintentando en {retry_delay} segundos...",
                        flush=True,
                    )
                    time.sleep(retry_delay)
                else:
                    print(
                        f"[ReniecWorker] ✗ FALLO CRÍTICO: No se pudo conectar después de {max_attempts} intentos",
                        flush=True,
                    )
                    sys.exit(1)

    def on_message(self, ch, method, props, body):
        try:
            message = body.decode("utf-8")
            print(f"[ReniecWorker] Mensaje recibido: {message}")
            req = json.loads(message)
            req_type = req.get("type", "").upper()

            if req_type == "VALIDAR_DNI":
                response_data = self._handle_validar_dni(req)
            else:
                response_data = {"status": "ERROR", "error": "TIPO_DESCONOCIDO"}

            if props.reply_to:
                ch.basic_publish(
                    exchange="",
                    routing_key=props.reply_to,
                    properties=pika.BasicProperties(
                        correlation_id=props.correlation_id
                    ),
                    body=json.dumps(response_data, default=str),
                )
                print(
                    f"[ReniecWorker] Respuesta enviada: {json.dumps(response_data, default=str)}"
                )

        except Exception as e:
            print(f"[ReniecWorker] [ERROR] Inesperado: {e}")
        finally:
            ch.basic_ack(delivery_tag=method.delivery_tag)

    def _handle_validar_dni(self, req):
        dni = req.get("dni")
        if not dni:
            return {"status": "ERROR", "error": "DNI no proporcionado"}

        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM Personas WHERE dni = ?", (dni,))
                persona = cursor.fetchone()

                if persona:
                    return {"status": "OK", "data": dict(persona)}
                else:
                    return {"status": "ERROR", "error": "DNI no encontrado"}
        except Exception as e:
            print(f"[ReniecWorker] [ERROR] al consultar DB: {e}")
            return {"status": "ERROR", "error": f"Error en base de datos: {e}"}

    def start(self):
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(
            queue=RENIEC_QUEUE, on_message_callback=self.on_message
        )
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            self.connection.close()
            print("[ReniecWorker] Conexión cerrada.")


if __name__ == "__main__":
    print("[ReniecWorker] ========================================", flush=True)
    print("[ReniecWorker] Iniciando ReniecWorker...", flush=True)
    print(f"[ReniecWorker] Base de datos: {DB_PATH}", flush=True)
    print("[ReniecWorker] ========================================", flush=True)

    try:
        worker = ReniecWorker()
        print("[ReniecWorker] ✓ Worker inicializado correctamente", flush=True)
        print("[ReniecWorker] Esperando mensajes... (Ctrl+C para detener)", flush=True)
        worker.start()
    except KeyboardInterrupt:
        print("\n[ReniecWorker] Interrumpido por usuario", flush=True)
        sys.exit(0)
    except Exception as e:
        print(f"[ReniecWorker] ✗ Error fatal al iniciar: {e}", flush=True)
        import traceback

        traceback.print_exc()
        sys.exit(1)
