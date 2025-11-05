import json
import sys

import pika
import psycopg2
import psycopg2.extras

# --- Configuración ---
WORKER_EXCHANGE = "worker_exchange"

# Configuración de la conexión a PostgreSQL
DB_CONFIG = {
    "dbname": "bd1_banco",
    "user": "postgres",
    "password": "mysecretpassword",
    "host": "localhost",
    "port": "5432",
}


class NodoWorker:
    def __init__(self, worker_id):
        self.worker_id = worker_id
        self.queue_name = f"worker_queue_{worker_id}"
        self.prepared_ops = {}
        self._init_rabbitmq()

    def _get_db_connection(self):
        """Establece y devuelve una conexión a la base de datos."""
        return psycopg2.connect(**DB_CONFIG)

    def _init_rabbitmq(self):
        """Inicializa la conexión y el canal de RabbitMQ con reintentos."""
        max_attempts = 5
        retry_delay = 3

        for attempt in range(1, max_attempts + 1):
            try:
                print(
                    f"[Nodo-{self.worker_id}] Intento {attempt}/{max_attempts} de conexión a RabbitMQ...",
                    flush=True,
                )
                self.connection = pika.BlockingConnection(
                    pika.ConnectionParameters(
                        host="localhost", connection_attempts=3, retry_delay=2
                    )
                )
                self.channel = self.connection.channel()
                self.channel.exchange_declare(
                    exchange=WORKER_EXCHANGE, exchange_type="direct"
                )
                self.channel.queue_declare(queue=self.queue_name, durable=True)
                self.channel.queue_bind(
                    queue=self.queue_name,
                    exchange=WORKER_EXCHANGE,
                    routing_key=self.queue_name,
                )
                print(
                    f"[Nodo-{self.worker_id}] ✓ Conectado exitosamente a RabbitMQ",
                    flush=True,
                )
                print(
                    f"[Nodo-{self.worker_id}] ✓ Escuchando en cola '{self.queue_name}'",
                    flush=True,
                )
                return
            except Exception as e:
                print(
                    f"[Nodo-{self.worker_id}] ✗ Error en intento {attempt}: {e}",
                    flush=True,
                )
                if attempt < max_attempts:
                    print(
                        f"[Nodo-{self.worker_id}] Reintentando en {retry_delay} segundos...",
                        flush=True,
                    )
                    import time

                    time.sleep(retry_delay)
                else:
                    print(
                        f"[Nodo-{self.worker_id}] ✗ FALLO CRÍTICO: No se pudo conectar después de {max_attempts} intentos",
                        flush=True,
                    )
                    sys.exit(1)

    def on_message(self, ch, method, props, body):
        """Callback que se ejecuta al recibir un mensaje."""
        try:
            message = body.decode("utf-8")
            print(f"[Nodo-{self.worker_id}] Mensaje recibido: {message}")
            req = json.loads(message)
            req_type = req.get("type", "").upper()

            response_data = None
            if "PREPARE" in req_type:
                response_data = self._handle_prepare(req)
            elif req_type == "COMMIT":
                self._handle_commit(req)
            elif req_type == "ABORT":
                self._handle_abort(req)
            elif req_type == "CONSULTAR_CUENTA":
                response_data = self._handle_query(req)
            elif req_type == "SUM_PARTITION":
                response_data = self._handle_sum(req)
            else:
                response_data = {"status": "ERROR", "error": "TIPO_DESCONOCIDO"}

            if props.reply_to and response_data:
                ch.basic_publish(
                    exchange="",
                    routing_key=props.reply_to,
                    properties=pika.BasicProperties(
                        correlation_id=props.correlation_id
                    ),
                    body=json.dumps(response_data),
                )
                print(
                    f"[Nodo-{self.worker_id}] Respuesta enviada: {json.dumps(response_data)}"
                )

        except json.JSONDecodeError:
            print(f"[Nodo-{self.worker_id}] [ERROR] JSON mal formado: {body.decode()}")
        except Exception as e:
            print(f"[Nodo-{self.worker_id}] [ERROR] Inesperado: {e}")
        finally:
            ch.basic_ack(delivery_tag=method.delivery_tag)

    def _handle_prepare(self, req):
        tx_id = req.get("tx_id")
        try:
            req_type = req.get("type", "").lower()
            ops_to_prepare = []

            with self._get_db_connection() as conn:
                with conn.cursor() as cursor:
                    if "transfer" in req_type:
                        from_acc, to_acc, amount = (
                            int(req["from"]),
                            int(req["to"]),
                            float(req["amount"]),
                        )

                        # Verificar si la cuenta de origen pertenece a este nodo y si tiene saldo
                        cursor.execute(
                            "SELECT saldo FROM Cuentas WHERE id_cuenta = %s",
                            (from_acc,),
                        )
                        result = cursor.fetchone()
                        if result and result[0] < amount:
                            return {
                                "status": "ERROR",
                                "tx_id": tx_id,
                                "error": "Saldo insuficiente",
                            }

                        if result:  # La cuenta de origen está en este nodo
                            ops_to_prepare.append(("debit", from_acc, amount))

                        # Verificar si la cuenta de destino pertenece a este nodo
                        cursor.execute(
                            "SELECT 1 FROM Cuentas WHERE id_cuenta = %s", (to_acc,)
                        )
                        if cursor.fetchone():
                            ops_to_prepare.append(("credit", to_acc, amount))

            self.prepared_ops[tx_id] = ops_to_prepare
            return {"status": "READY", "tx_id": tx_id}
        except Exception as e:
            return {"status": "ERROR", "tx_id": tx_id, "error": str(e)}

    def _handle_commit(self, req):
        tx_id = req.get("tx_id")
        if tx_id not in self.prepared_ops:
            return

        ops = self.prepared_ops.pop(tx_id, [])
        try:
            with self._get_db_connection() as conn:
                with conn.cursor() as cursor:
                    for op_type, acc, amount in ops:
                        if op_type == "debit":
                            cursor.execute(
                                "UPDATE Cuentas SET saldo = saldo - %s WHERE id_cuenta = %s",
                                (amount, acc),
                            )
                            cursor.execute(
                                "INSERT INTO Transacciones(id_cuenta, tipo_transaccion, monto) VALUES (%s, %s, %s)",
                                (acc, "DEBITO", -amount),
                            )
                        elif op_type == "credit":
                            cursor.execute(
                                "UPDATE Cuentas SET saldo = saldo + %s WHERE id_cuenta = %s",
                                (amount, acc),
                            )
                            cursor.execute(
                                "INSERT INTO Transacciones(id_cuenta, tipo_transaccion, monto) VALUES (%s, %s, %s)",
                                (acc, "CREDITO", amount),
                            )
                    conn.commit()
        except Exception as e:
            print(f"[Nodo-{self.worker_id}] [ERROR] Fallo en commit: {e}")

    def _handle_abort(self, req):
        tx_id = req.get("tx_id")
        self.prepared_ops.pop(tx_id, None)

    def _handle_query(self, req):
        acc = int(req["account"])
        try:
            with self._get_db_connection() as conn:
                with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                    cursor.execute("SELECT * FROM Cuentas WHERE id_cuenta = %s", (acc,))
                    cuenta = cursor.fetchone()
                    if cuenta:
                        return {
                            "status": "OK",
                            "account": acc,
                            "balance": float(cuenta["saldo"]),
                        }
            return {"status": "ERROR", "error": "NO_EXISTE_CUENTA"}
        except Exception as e:
            return {"status": "ERROR", "error": str(e)}

    def _handle_sum(self, req):
        total_sum = 0
        try:
            with self._get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT SUM(saldo) FROM Cuentas")
                    result = cursor.fetchone()
                    if result and result[0] is not None:
                        total_sum = float(result[0])
            return {"status": "OK", "sum": total_sum}
        except Exception as e:
            return {"status": "ERROR", "error": str(e)}

    def start(self):
        """Inicia el consumidor de RabbitMQ."""
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(
            queue=self.queue_name, on_message_callback=self.on_message
        )
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            print("Cerrando conexión...")
            self.connection.close()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python3 src/python/nodo_trabajador/nodo_worker.py <worker-id>")
        sys.exit(1)

    try:
        worker_id = int(sys.argv[1])
        print(
            f"[Nodo-{worker_id}] ========================================", flush=True
        )
        print(f"[Nodo-{worker_id}] Iniciando NodoWorker {worker_id}...", flush=True)
        print(f"[Nodo-{worker_id}] Cola: worker_queue_{worker_id}", flush=True)
        print(
            f"[Nodo-{worker_id}] ========================================", flush=True
        )

        worker = NodoWorker(worker_id)
        print(f"[Nodo-{worker_id}] ✓ Worker inicializado correctamente", flush=True)
        print(
            f"[Nodo-{worker_id}] Esperando mensajes... (Ctrl+C para detener)",
            flush=True,
        )
        worker.start()
    except ValueError:
        print("Error: El ID del trabajador debe ser un número entero.")
        sys.exit(1)
    except KeyboardInterrupt:
        print(f"\n[Nodo-{worker_id}] Interrumpido por usuario", flush=True)
        sys.exit(0)
    except Exception as e:
        print(f"[Nodo-{worker_id}] ✗ Error fatal al iniciar: {e}", flush=True)
        import traceback

        traceback.print_exc()
        sys.exit(1)
