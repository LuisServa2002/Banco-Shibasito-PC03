import json
import time
import uuid

import pika


class RpcClient:
    """Cliente RPC genérico para RabbitMQ."""

    def __init__(self):
        self.connection = None
        self.channel = None
        self.callback_queue = None
        self.response = None
        self.corr_id = None

    def connect(self):
        """Establece la conexión y el canal. Lanza excepción si falla."""
        if self.connection and self.connection.is_open:
            return

        print("[RpcClient] Conectando a RabbitMQ...", flush=True)
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host="localhost", connection_attempts=3, retry_delay=2
            )
        )
        self.channel = self.connection.channel()

        # Declarar cola exclusiva para respuestas
        result = self.channel.queue_declare(queue="", exclusive=True)
        self.callback_queue = result.method.queue

        # Configurar consumidor
        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True,
        )

        print(
            f"[RpcClient] ✓ Conectado. Cola de respuesta: {self.callback_queue}",
            flush=True,
        )

    def on_response(self, ch, method, props, body):
        """Callback que se ejecuta cuando se recibe una respuesta."""
        if self.corr_id == props.correlation_id:
            self.response = body
            print(
                f"[RpcClient] ✓ Respuesta recibida (correlation_id: {props.correlation_id})",
                flush=True,
            )

    def call(self, message, routing_key="client_requests_queue", timeout=30):
        """Envía un mensaje RPC y espera la respuesta."""
        if not self.connection or not self.connection.is_open:
            raise ConnectionError("No hay conexión con el servidor RabbitMQ.")

        # Reset estado
        self.response = None
        self.corr_id = str(uuid.uuid4())

        print(f"[RpcClient] Enviando: {message.get('type', 'UNKNOWN')}", flush=True)
        print(f"[RpcClient] correlation_id: {self.corr_id}", flush=True)

        # Publicar mensaje
        self.channel.basic_publish(
            exchange="",
            routing_key=routing_key,
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id,
                content_type="application/json",
            ),
            body=json.dumps(message),
        )

        print(f"[RpcClient] Esperando respuesta (timeout: {timeout}s)...", flush=True)

        # ✅ CORRECCIÓN: Procesar eventos de RabbitMQ mientras espera
        start_time = time.time()
        while self.response is None:
            # Procesar eventos durante 1 segundo
            self.connection.process_data_events(time_limit=1)

            # Verificar timeout
            elapsed = time.time() - start_time
            if elapsed >= timeout:
                raise TimeoutError(
                    f"La solicitud RPC ha expirado después de {timeout} segundos."
                )

        # Parsear y retornar respuesta
        try:
            result = json.loads(self.response.decode())
            print("[RpcClient] ✓ Respuesta parseada exitosamente", flush=True)
            return result
        except json.JSONDecodeError as e:
            print(f"[RpcClient] ✗ Error al parsear respuesta: {e}", flush=True)
            return {
                "status": "ERROR",
                "error": f"Respuesta inválida del servidor: {self.response.decode()}",
            }

    def close(self):
        """Cierra la conexión con RabbitMQ."""
        if self.connection and self.connection.is_open:
            print("[RpcClient] Cerrando conexión...", flush=True)
            self.connection.close()
            print("[RpcClient] ✓ Conexión cerrada", flush=True)
