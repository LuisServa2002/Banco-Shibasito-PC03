import sys
import os

# Añadir el directorio raíz del proyecto al path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
sys.path.append(ROOT_DIR)

from src.python.common.rpc_client import RpcClient

def menu():
    print("\n--- CLIENTE BANCO (MODO TEST) ---")
    print("1. Consultar cuenta")
    print("2. Transferir dinero")
    print("3. Solicitar Préstamo (TEST)")
    print("4. Validar DNI (TEST)")
    print("5. Salir")

def main():
    client = RpcClient()
    while True:
        menu()
        op = input("Seleccione: ")
        
        try:
            if op == "1":
                acc = input("Número de cuenta: ")
                response = client.call({"type":"CONSULTAR_CUENTA","account":int(acc)})
                print("[Respuesta]:", response)
            elif op == "2":
                f = input("Cuenta origen: ")
                t = input("Cuenta destino: ")
                amt = input("Monto: ")
                response = client.call({"type":"TRANSFERIR_CUENTA","from":int(f),"to":int(t),"amount":float(amt)})
                print("[Respuesta]:", response)
            elif op == "3":
                acc = input("ID de cuenta para el préstamo: ")
                amt = input("Monto a solicitar: ")
                response = client.call({"type":"SOLICITAR_PRESTAMO","account":int(acc),"amount":float(amt)})
                print("[Respuesta]:", response)
            elif op == "4":
                dni = input("DNI a validar: ")
                response = client.call({"type":"VALIDAR_DNI","dni":dni})
                print("[Respuesta]:", response)
            elif op == "5":
                break
            else:
                print("Opción inválida.")
        except ValueError:
            print("[Error] Entrada inválida, por favor ingrese números donde corresponda.")
        except Exception as e:
            print(f"[Error inesperado]: {e}")
    
    client.close()
    print("Conexión cerrada.")

if __name__ == "__main__":
    main()