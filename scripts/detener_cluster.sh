#!/bin/bash

# Script para detener todos los servicios del backend de Shibasito.

echo "Deteniendo todos los servicios de Shibasito..."

# Detener el Proxy del Cliente
pkill -f "cliente_proxy.py"
echo "  -> ClienteProxy detenido."

# Detener el Servidor Central de Java
pkill -f "servidor_central.ServidorCentral"
echo "  -> ServidorCentral detenido."

# Detener los Nodos Trabajadores de Java
pkill -f "nodo_trabajador.NodoWorker"
echo "  -> NodosWorker de Java detenidos."

# Detener los workers de Python
pkill -f "reniec_worker.py"
echo "  -> ReniecWorker detenido."
pkill -f "nodo_trabajador/nodo_worker.py"
echo "  -> NodosWorker de Python detenidos."

# Limpiar directorio de logs
rm -rf logs
echo "  -> Directorio de logs eliminado."

echo ""
echo "✅ Todos los servicios han sido detenidos."
