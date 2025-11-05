#!/bin/bash

# Script para compilar e iniciar todos los servicios del backend de Shibasito.

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")"/.. && pwd)"
cd "$PROJECT_ROOT"

LOGS_DIR="logs"
BIN_DIR="bin"
# Apuntar directamente al python del venv
VENV_PYTHON=".venv/bin/python3"

if [ ! -f "$VENV_PYTHON" ]; then
    echo "Error: El entorno virtual de Python no se encuentra en .venv/"
    exit 1
fi
# Función para verificar que RabbitMQ está listo
verificar_rabbitmq() {
    echo "Verificando que RabbitMQ esté operativo..."
    MAX_INTENTOS=30
    CONTADOR=0

    while [ $CONTADOR -lt $MAX_INTENTOS ]; do
        if nc -z localhost 5672 2>/dev/null; then
            echo "✓ RabbitMQ está listo"
            return 0
        fi
        CONTADOR=$((CONTADOR + 1))
        echo "  Esperando RabbitMQ... (intento $CONTADOR/$MAX_INTENTOS)"
        sleep 1
    done

    echo "✗ ERROR: RabbitMQ no está disponible después de $MAX_INTENTOS segundos"
    echo "  Asegúrate de que RabbitMQ esté corriendo:"
    echo "  docker ps | grep rabbitmq"
    exit 1
}
echo "[Paso 1/4] Creando directorio de logs..."
rm -rf "$LOGS_DIR"
mkdir -p "$LOGS_DIR"

echo "[Paso 2/4] Compilando código Java..."
mkdir -p "$BIN_DIR"

javac -d "$BIN_DIR" \
    -cp "lib/*" \
    src/java/servidor_central/ServidorCentral.java \
    src/java/nodo_trabajador/NodoWorker.java

echo "Compilación de Java exitosa."

echo "[Paso 3/4] Iniciando servicios backend..."

# Verificar que RabbitMQ está listo
verificar_rabbitmq

# Servidor Central
echo "  -> Iniciando ServidorCentral... (log en logs/servidor_central.log)"
java -cp "$BIN_DIR:lib/*" \
    servidor_central.ServidorCentral config/nodos_config.json \
    >"$LOGS_DIR/servidor_central.log" 2>&1 &
SERVIDOR_PID=$!

sleep 3

# Verificar que el servidor arrancó
if ! ps -p $SERVIDOR_PID >/dev/null 2>&1; then
    echo "✗ ERROR: ServidorCentral falló al iniciar"
    echo "  Revisa el log: logs/servidor_central.log"
    exit 1
fi
echo "     ✓ ServidorCentral iniciado (PID: $SERVIDOR_PID)"

sleep 2

# Worker RENIEC
echo "  -> Iniciando ReniecWorker... (log en logs/reniec_worker.log)"
"$VENV_PYTHON" src/python/nodo_reniec/reniec_worker.py \
    >"$LOGS_DIR/reniec_worker.log" 2>&1 &
RENIEC_PID=$!

sleep 2

# Verificar que RENIEC arrancó
if ! ps -p $RENIEC_PID >/dev/null 2>&1; then
    echo "✗ ERROR: ReniecWorker falló al iniciar"
    echo "  Revisa el log: logs/reniec_worker.log"
    exit 1
fi
echo "     ✓ ReniecWorker iniciado (PID: $RENIEC_PID)"

# Workers Java
for i in 0 1; do
    echo "  -> Iniciando NodoWorker $i (Java)... (log en logs/nodo_worker_$i.log)"
    java -cp "$BIN_DIR:lib/*" \
        nodo_trabajador.NodoWorker $i \
        >"$LOGS_DIR/nodo_worker_$i.log" 2>&1 &
    WORKER_PID=$!

    sleep 2

    if ! ps -p $WORKER_PID >/dev/null 2>&1; then
        echo "✗ ERROR: NodoWorker $i falló al iniciar"
        echo "  Revisa el log: logs/nodo_worker_$i.log"
        exit 1
    fi
    echo "     ✓ NodoWorker $i iniciado (PID: $WORKER_PID)"
done

# Workers Python
for i in 2 3; do
    echo "  -> Iniciando nodo_worker $i (Python)... (log en logs/nodo_worker_$i.log)"
    "$VENV_PYTHON" src/python/nodo_trabajador/nodo_worker.py $i \
        >"$LOGS_DIR/nodo_worker_$i.log" 2>&1 &
    WORKER_PID=$!

    sleep 2

    if ! ps -p $WORKER_PID >/dev/null 2>&1; then
        echo "✗ ERROR: nodo_worker $i falló al iniciar"
        echo "  Revisa el log: logs/nodo_worker_$i.log"
        exit 1
    fi
    echo "     ✓ nodo_worker $i iniciado (PID: $WORKER_PID)"
done

echo "✅ Backend iniciado correctamente."

echo "[Paso 4/4] Iniciando Proxy Local para cliente desktop..."
echo "  -> Iniciando ClienteProxy... (log en logs/cliente_proxy.log)"
"$VENV_PYTHON" src/python/cliente_desktop/cliente_proxy.py \
    >"$LOGS_DIR/cliente_proxy.log" 2>&1 &

sleep 1

echo "✅ Todos los servicios han sido iniciados."
echo ""
echo "=========================================="
echo "ESTADO DEL SISTEMA"
echo "=========================================="
echo "Servicios activos:"
echo "  ✓ ServidorCentral"
echo "  ✓ ReniecWorker"
echo "  ✓ 4 NodosWorker (2 Java, 2 Python)"
echo "  ✓ ClienteProxy (puerto 9876)"
echo ""
echo "Logs disponibles en: $LOGS_DIR/"
echo ""
echo "Próximos pasos:"
echo "  - Para ver logs en tiempo real: tail -f logs/<archivo>.log"
echo "  - Para probar el sistema: $VENV_PYTHON scripts/test_terminal.py"
echo "  - Para detener: ./scripts/detener_cluster.sh"
echo "=========================================="
