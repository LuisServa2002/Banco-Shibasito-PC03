#!/usr/bin/env python3

import sys
import os
import json
from getpass import getpass

# Añadir el directorio raíz del proyecto al path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(ROOT_DIR)

from src.python.common.proxy_client import ProxyClient

def pretty_print(data):
    """Imprime un diccionario o lista de forma legible."""
    print(json.dumps(data, indent=4, ensure_ascii=False))

def main():
    """Función principal del cliente de terminal."""
    client = ProxyClient()
    session = {}

    print("--- Cliente de Terminal para Banco Shibasito ---")

    try:
        print("Conectando al proxy local...")
        client.connect()
        print("¡Conexión exitosa!")
    except Exception as e:
        print(f"Error fatal al conectar con el proxy: {e}")
        return

    while True:
        print("\n--- MENÚ ---")
        if not session:
            print("1. Iniciar Sesión")
        else:
            print(f"Usuario: {session.get('nombre')} | Cuenta: {session.get('account')}")
            print("2. Consultar Saldo")
            print("3. Realizar Transferencia")
            print("4. Solicitar Préstamo")
            print("5. Cerrar Sesión")
        
        print("0. Salir")
        
        opcion = input("Seleccione una opción: ")

        if opcion == '1' and not session:
            try:
                dni = input("Ingrese su DNI: ")
                cuenta = input("Ingrese su N° de Cuenta: ")
                payload = {"type": "LOGIN", "dni": dni, "account": int(cuenta)}
                response = client.call(payload)
                if response.get("status") == "OK":
                    session = response
                    print("\n✅ Inicio de sesión exitoso.")
                    pretty_print(session)
                else:
                    print(f"\n❌ Error: {response.get('error')}")
            except Exception as e:
                print(f"Error durante el login: {e}")

        elif opcion == '2' and session:
            try:
                payload = {"type": "CONSULTAR_CUENTA", "account": session.get("account")}
                response = client.call(payload)
                print("\n--- Saldo de la Cuenta ---")
                pretty_print(response)
            except Exception as e:
                print(f"Error durante la consulta: {e}")

        elif opcion == '3' and session:
            try:
                cuenta_destino = int(input("Ingrese la cuenta destino: "))
                monto = float(input("Ingrese el monto: ") )
                payload = {
                    "type": "TRANSFERIR_CUENTA",
                    "from_account": session.get("account"),
                    "to_account": cuenta_destino,
                    "amount": monto,
                    "description": "Transferencia desde cliente de terminal"
                }
                response = client.call(payload)
                print("\n--- Resultado de la Transferencia ---")
                pretty_print(response)
            except Exception as e:
                print(f"Error durante la transferencia: {e}")

        elif opcion == '4' and session:
            try:
                monto = float(input("Ingrese el monto a solicitar: "))
                plazo = int(input("Ingrese el plazo en meses: "))
                payload = {
                    "type": "SOLICITAR_PRESTAMO",
                    "account": session.get("account"),
                    "dni": session.get("dni"),
                    "monto": monto,
                    "plazo_meses": plazo
                }
                response = client.call(payload)
                print("\n--- Resultado de la Solicitud de Préstamo ---")
                pretty_print(response)
            except Exception as e:
                print(f"Error en la solicitud: {e}")

        elif opcion == '5' and session:
            session = {}
            print("\nSesión cerrada.")

        elif opcion == '0':
            print("Cerrando cliente...")
            client.close()
            break
        else:
            print("Opción no válida. Intente de nuevo.")

if __name__ == "__main__":
    main()
