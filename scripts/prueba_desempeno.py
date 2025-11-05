import threading
import time
import random
import sys
import os
from collections import Counter

# Añadir el directorio raíz del proyecto al path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(ROOT_DIR)

from src.python.common.rpc_client import RpcClient

# --- Configuración de la Prueba ---
NUM_CLIENTES_CONCURRENTES = 20  # Número de hilos/clientes
OPERACIONES_POR_CLIENTE = 50    # Cuántas operaciones hará cada cliente

# Cuentas válidas para la simulación (basado en la lógica de ServidorCentral)
# Pares (id_cuenta, dni)
CUENTAS_VALIDAS = [
    (1001, "12345678"),
    (1002, "12345678"),
    (4001, "87654321"),
    (4002, "87654321"),
]

# --- Almacenamiento de Resultados ---
results_lock = threading.Lock()
results = Counter()
latencies = []

def simular_cliente(client_id, num_operaciones):
    """Función que simula el comportamiento de un cliente bancario."""
    global results, latencies
    rpc_client = RpcClient()
    
    # Simular un login inicial para obtener datos de sesión
    cuenta_actual, dni_actual = random.choice(CUENTAS_VALIDAS)
    
    for i in range(num_operaciones):
        operacion = random.choice(["consulta", "transferencia", "prestamo"])
        start_time = time.time()
        
        try:
            if operacion == "consulta":
                payload = {"type": "CONSULTAR_CUENTA", "account": cuenta_actual}
                response = rpc_client.call(payload)
            
            elif operacion == "transferencia":
                # Elegir una cuenta destino que no sea la propia
                cuenta_destino = random.choice([c[0] for c in CUENTAS_VALIDAS if c[0] != cuenta_actual])
                monto = round(random.uniform(10.0, 500.0), 2)
                payload = {
                    "type": "TRANSFERIR_CUENTA",
                    "from_account": cuenta_actual,
                    "to_account": cuenta_destino,
                    "amount": monto,
                    "description": f"Transferencia de prueba {client_id}-{i}"
                }
                response = rpc_client.call(payload)

            elif operacion == "prestamo":
                monto = round(random.uniform(1000.0, 15000.0), 2)
                plazo = random.choice([12, 24, 36, 48])
                payload = {
                    "type": "SOLICITAR_PRESTAMO",
                    "account": cuenta_actual,
                    "dni": dni_actual,
                    "monto": monto,
                    "plazo_meses": plazo
                }
                response = rpc_client.call(payload)

            end_time = time.time()

            with results_lock:
                latencies.append(end_time - start_time)
                if response and response.get("status") == "OK":
                    results["exitosas"] += 1
                else:
                    print(f"[Cliente {client_id}] Error en op {i+1}: {response}")
                    results["fallidas"] += 1
        
        except Exception as e:
            end_time = time.time()
            print(f"[Cliente {client_id}] Excepción en op {i+1}: {e}")
            with results_lock:
                latencies.append(end_time - start_time)
                results["excepciones"] += 1

        time.sleep(random.uniform(0.1, 0.5)) # Simular tiempo entre operaciones

    rpc_client.close()

if __name__ == "__main__":
    threads = []
    total_operaciones = NUM_CLIENTES_CONCURRENTES * OPERACIONES_POR_CLIENTE

    print("--- Iniciando Prueba de Desempeño del Sistema Bancario ---")
    print(f"Clientes concurrentes: {NUM_CLIENTES_CONCURRENTES}")
    print(f"Operaciones por cliente: {OPERACIONES_POR_CLIENTE}")
    print(f"Total de operaciones a realizar: {total_operaciones}")
    print("---------------------------------------------------------")

    start_time = time.time()

    for i in range(NUM_CLIENTES_CONCURRENTES):
        thread = threading.Thread(target=simular_cliente, args=(i + 1, OPERACIONES_POR_CLIENTE))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    end_time = time.time()
    duracion_total = end_time - start_time

    print("\n--- Resultados de la Prueba de Desempeño ---")
    print(f"Tiempo total de ejecución: {duracion_total:.2f} segundos")
    print(f"Total de operaciones: {sum(results.values())}")
    print(f"  - Exitosas: {results['exitosas']}")
    print(f"  - Fallidas (errores de lógica): {results['fallidas']}")
    print(f"  - Fallidas (excepciones): {results['excepciones']}")
    
    if duracion_total > 0:
        ops_por_segundo = sum(results.values()) / duracion_total
        print(f"Rendimiento (operaciones/segundo): {ops_por_segundo:.2f}")

    if latencies:
        latencia_promedio = sum(latencies) / len(latencies)
        print(f"Latencia promedio por operación: {latencia_promedio*1000:.2f} ms")
    
    print("---------------------------------------------")
