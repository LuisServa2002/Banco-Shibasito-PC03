#!/bin/bash

# Script de Diagnóstico para ejecutar cada componente de Python individualmente
# y en primer plano para poder ver los errores de inicio.

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")"/.. && pwd)"
cd "$PROJECT_ROOT"

# Activar el entorno virtual
source .venv/bin/activate
echo "Entorno virtual activado."

echo ""
echo "--- [PASO 1/4] Probando reniec_worker.py ---"
echo "Intentando iniciar... Si tiene éxito, se quedará corriendo. Presiona Ctrl+C para detenerlo y continuar con el siguiente."
sleep 2
python3 src/python/nodo_reniec/reniec_worker.py


echo ""
echo "--- [PASO 2/4] Probando nodo_worker.py (ID 2) ---"
echo "Intentando iniciar... Si tiene éxito, se quedará corriendo. Presiona Ctrl+C para detenerlo y continuar con el siguiente."
sleep 2
python3 src/python/nodo_trabajador/nodo_worker.py 2


echo ""
echo "--- [PASO 3/4] Probando nodo_worker.py (ID 3) ---"
echo "Intentando iniciar... Si tiene éxito, se quedará corriendo. Presiona Ctrl+C para detenerlo y continuar con el siguiente."
sleep 2
python3 src/python/nodo_trabajador/nodo_worker.py 3


echo ""
echo "--- [PASO 4/4] Probando cliente_proxy.py ---"
echo "Intentando iniciar... Si tiene éxito, se quedará corriendo. Presiona Ctrl+C para detenerlo y finalizar el diagnóstico."
sleep 2
python3 src/python/cliente_desktop/cliente_proxy.py

echo ""
echo "✅ Diagnóstico completado. Si has llegado hasta aquí, todos los scripts de Python pueden iniciarse manualmente."
