#!/usr/bin/env python3
"""
Poblar AMBAS bases de datos (RENIEC y Banco) con 10,000 usuarios
para pruebas de carga. (VERSIÓN CORREGIDA)
"""
import psycopg2
import psycopg2.extras
import sqlite3
import os
import random
from datetime import datetime

# --- Configuración ---
NUM_USUARIOS = 10000
CUENTA_START_ID = 1000
DNI_START_ID = 70000000 # DNI base de 8 dígitos

# --- Conexión a RENIEC (SQLite) ---
DB_RENEC_PATH = "db_reniec/reniec.db"
os.makedirs("db_reniec", exist_ok=True)
conn_reniec = sqlite3.connect(DB_RENEC_PATH)
cursor_reniec = conn_reniec.cursor()

# --- Conexión a BANCO (PostgreSQL) ---
DB_BANCO_CONFIG = {
    "dbname": "bd1_banco",
    "user": "postgres",
    "password": "mysecretpassword",
    "host": "localhost",
    "port": "5432",
}

try:
    conn_banco = psycopg2.connect(**DB_BANCO_CONFIG)
    cursor_banco = conn_banco.cursor()
except Exception as e:
    print(f"❌ Error conectando a PostgreSQL: {e}")
    print("Asegúrate de que el contenedor 'postgres-db' esté corriendo.")
    exit(1)


def poblar_masivo():
    print(f"Iniciando poblamiento masivo de {NUM_USUARIOS} usuarios...")
    
    # --- 1. Crear Tablas (si no existen) ---
    # (Usamos los schemas reales que proporcionaste)
    
    # RENIEC
    cursor_reniec.execute("""
    CREATE TABLE IF NOT EXISTS Personas (
        dni TEXT PRIMARY KEY, apellido_paterno TEXT, apellido_materno TEXT,
        nombres TEXT, fecha_nacimiento TEXT, sexo TEXT, direccion TEXT
    )""")
    
    # BANCO
    # No creamos la tabla, asumimos que ya existe por bd1_banco.sql
    
    # --- 2. Generar Datos ---
    personas_data = []
    cuentas_data = []
    
    start_time = datetime.now()
    
    for i in range(NUM_USUARIOS):
        dni = str(DNI_START_ID + i)
        id_cuenta = CUENTA_START_ID + i
        nombres = f"Nombres {i}"
        apellido_p = f"ApellidoPaterno{i}"
        apellido_m = f"ApellidoMaterno{i}"
        
        # Datos para RENIEC
        personas_data.append((
            dni,
            apellido_p,
            apellido_m,
            nombres,
            "1990-01-01", "M", f"Calle Falsa {i}"
        ))
        
        # Datos para BANCO (Schema Corregido)
        nombre_completo = f"{nombres} {apellido_p} {apellido_m}"
        saldo_inicial = round(random.uniform(500, 10000), 2)
        cuentas_data.append((
            id_cuenta,
            nombre_completo, # <-- La columna que faltaba
            dni,
            saldo_inicial
        ))

    print("Datos generados. Insertando en bases de datos...")

    # --- 3. Insertar en Lotes (Batch) ---
    
    # Insertar en RENIEC
    cursor_reniec.executemany(
        "INSERT OR REPLACE INTO Personas (dni, apellido_paterno, apellido_materno, nombres, fecha_nacimiento, sexo, direccion) VALUES (?, ?, ?, ?, ?, ?, ?)",
        personas_data
    )
    conn_reniec.commit()
    print(f"✓ {len(personas_data)} registros insertados/reemplazados en RENIEC.")

    # Insertar en BANCO (Query Corregida)
    psycopg2.extras.execute_batch(
        cursor_banco,
        "INSERT INTO cuentas (id_cuenta, nombre_cliente, dni, saldo) VALUES (%s, %s, %s, %s) ON CONFLICT (id_cuenta) DO UPDATE SET saldo = EXCLUDED.saldo, dni = EXCLUDED.dni, nombre_cliente = EXCLUDED.nombre_cliente",
        cuentas_data
    )
    conn_banco.commit()
    print(f"✓ {len(cuentas_data)} registros insertados/actualizados en BANCO.")
    
    end_time = datetime.now()
    print(f"\n✅ Poblamiento completado en {(end_time - start_time).total_seconds():.2f} segundos.")
    
    # --- 4. Cerrar Conexiones ---
    conn_reniec.close()
    conn_banco.close()

if __name__ == "__main__":
    poblar_masivo()
