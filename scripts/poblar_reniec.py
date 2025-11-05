import sqlite3
import os

DB_DIR = 'db_reniec'
DB_NAME = 'reniec.db'
DB_PATH = os.path.join(DB_DIR, DB_NAME)
SCHEMA_PATH = os.path.join(DB_DIR, 'schema.sql')

def poblar_reniec():
    """Crea y puebla la base de datos de RENIEC con datos de ejemplo."""
    if os.path.exists(DB_PATH):
        print(f"La base de datos '{DB_PATH}' ya existe. No se realizarán cambios.")
        return

    print(f"Creando base de datos RENIEC en '{DB_PATH}'...")
    os.makedirs(DB_DIR, exist_ok=True)

    try:
        with open(SCHEMA_PATH, 'r') as f:
            schema_sql = f.read()

        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.executescript(schema_sql)
            print("Tabla 'Personas' creada.")

            personas_ejemplo = [
                ('12345678', 'GARCIA', 'LOPEZ', 'JUAN CARLOS', '1990-05-15', 'M', 'AV. SIEMPREVIVA 123'),
                ('87654321', 'MARTINEZ', 'RODRIGUEZ', 'MARIA ELENA', '1985-11-20', 'F', 'CALLE FALSA 456'),
                ('11223344', 'QUISPE', 'MAMANI', 'PEDRO PABLO', '2000-01-30', 'M', 'JR. PERDIDO 789'),
                ('44332211', 'FLORES', 'DIAZ', 'ANA SOFIA', '1998-07-22', 'F', 'PASAJE INEXISTENTE 101')
            ]

            cursor.executemany(
                "INSERT INTO Personas (dni, apellido_paterno, apellido_materno, nombres, fecha_nacimiento, sexo, direccion) VALUES (?, ?, ?, ?, ?, ?, ?)",
                personas_ejemplo
            )
            print(f"{len(personas_ejemplo)} personas de ejemplo insertadas.")
            conn.commit()
        print("Base de datos RENIEC creada y poblada con éxito.")

    except Exception as e:
        print(f"Error al inicializar la base de datos RENIEC: {e}")
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)

if __name__ == "__main__":
    poblar_reniec()
