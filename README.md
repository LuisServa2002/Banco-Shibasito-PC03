Aquí tienes el `README.md` completo y corregido.

La única sección que he cambiado es la **Sección 5 (Instalación)**, que ahora tiene los comandos correctos para que cualquier persona pueda crear las bases de datos después de clonar el repositorio.

---

# 🏦 Sistema Bancario Shibasito

Sistema bancario distribuido con arquitectura de microservicios usando RabbitMQ, implementando protocolo 2PC para transacciones atómicas.

## 🏗️ Arquitectura

- **Backend:** Java (ServidorCentral, NodoWorker) + Python (ReniecWorker, NodoWorker)
- **Middleware:** RabbitMQ (patrón RPC)
- **Base de Datos:**
  - PostgreSQL: BD1_banco (Cuentas, Transacciones, Préstamos)
  - SQLite: BD2_reniec (Personas)
- **Cliente Desktop:** Python/Tkinter con generación de códigos QR de cobro
- **Distribución:** 2 particiones con 4 nodos workers

## 📋 Requisitos

- **Docker** (para RabbitMQ y PostgreSQL)
- **Java 11+** con JARs incluidos en `lib/`
- **Python 3.10+**
- **Git** (para clonar el repositorio)

## 🚀 Instalación

### 1\. Clonar repositorio

```bash
git clone <tu-repo>
cd PC3
```

### 2\. Crear entorno virtual Python

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows
```

### 3\. Instalar dependencias Python

```bash
pip install -r requirements.txt
```

O manualmente:

```bash
pip install pika qrcode pillow psycopg2-binary
```

### 4\. Iniciar servicios Docker

#### RabbitMQ:

```bash
docker run -d --name rabbitmq-server \
  -p 5672:5672 -p 15672:15672 \
  rabbitmq:3-management
```

#### PostgreSQL:

```bash
docker run -d --name postgres-db \
  -e POSTGRES_PASSWORD=mysecretpassword \
  -p 5432:5432 postgres:13
```

**Verificar que estén corriendo:**

```bash
docker ps
```

### 5\. Crear y poblar base de datos

#### BD1 (Banco - PostgreSQL):

Primero, creamos la base de datos vacía en el contenedor. Luego, cargamos el
schema y los datos desde nuestro script SQL local.

```bash
# 1. Crear la base de datos vacía
docker exec -it postgres-db psql -U postgres -c "CREATE DATABASE bd1_banco;"

# 2. Cargar el schema y los datos
cat scripts_bd/bd1_banco.sql | docker exec -i postgres-db psql -U postgres -d bd1_banco
```

#### BD2 (RENIEC - SQLite):

Creamos la base de datos de RENIEC ejecutando el script .sql, lo cual
generará el archivo `db_reniec/reniec.db`.

```bash
# Crear la BD de RENIEC desde el dump
sqlite3 db_reniec/reniec.db < scripts_bd/bd2_reniec.sql
```

### 6\. Iniciar el sistema completo

```bash
./scripts/iniciar_cluster.sh
```

**Salida esperada:**

```
✓ RabbitMQ está listo
✓ ServidorCentral iniciado
✓ ReniecWorker iniciado
✓ 4 NodosWorker iniciados
✓ ClienteProxy iniciado (puerto 9876)
```

### 7\. Ejecutar cliente GUI

```bash
python src/python/cliente_desktop/cliente_gui.py
```

## 🔐 Credenciales de Prueba

| DNI        | Cuenta | Saldo Inicial | Nombre                      |
| ---------- | ------ | ------------- | --------------------------- |
| `45678912` | `1001` | S/ 2,400.00   | MARÍA ELENA GARCÍA FLORES   |
| `78901234` | `1002` | S/ 1,500.50   | JUAN CARLOS RAMÍREZ QUISPE  |
| `12345678` | `8008` | S/ 5,100.00   | LUIS ALBERTO TORRES MENDOZA |

## 💡 Funcionalidades

### Cliente Desktop (GUI):

- ✅ **Login:** Validación con DNI + Cuenta (verificado contra RENIEC)
- ✅ **Consultar Saldo:** Visualización en tiempo real
- ✅ **Transferencias:** Entre cuentas con protocolo 2PC
- ✅ **Préstamos:** Solicitud con validación de identidad
- ✅ **Historial:** Consulta de transacciones
- ✅ **Códigos QR:** Generación de QR de cobro para app móvil

### Backend:

- ✅ **Protocolo 2PC:** Transacciones atómicas distribuidas
- ✅ **Particionamiento:** Distribución de cuentas en 2 particiones
- ✅ **Alta disponibilidad:** 2 réplicas por partición
- ✅ **Validación RENIEC:** Autenticación contra base de datos ciudadanos

## 🧪 Tests

```bash
# Test completo de mapeo y 2PC
python test_mapeo.py

# Test de login y operaciones básicas
python test_login.py
```

**Salida esperada:**

```
✓ Cuenta 1001 | Partición 1 | Saldo: $ 2400.00
✓ Transferencia completada exitosamente
✓ Préstamo aprobado y registrado
```

## 📱 Código QR (Para App Móvil)

La GUI genera códigos QR de **cobro** con el siguiente formato:

```json
{
  "tipo": "COBRO",
  "subtipo": "COBRO_TRANSFERENCIA",
  "cuenta_cobrador": 1001,
  "dni_cobrador": "45678912",
  "nombre_cobrador": "MARÍA ELENA GARCÍA FLORES",
  "monto": 100.0,
  "concepto": "Pago por servicio",
  "timestamp": "2025-11-04T20:45:00",
  "banco": "Shibasito",
  "qr_id": "QR-1001-1730762700"
}
```

### Flujo del QR:

1.  Usuario Desktop genera QR de cobro
2.  Usuario Móvil escanea el QR
3.  App móvil muestra: "Pagar S/ X a [Nombre]"
4.  Usuario confirma y se ejecuta la transferencia
5.  Ambos saldos se actualizan

**Ver:** `INSTRUCCIONES_APP_MOVIL.md` para integración con app Kotlin/Android.

## 🛑 Detener Sistema

```bash
./scripts/detener_cluster.sh
```

Esto detendrá:

- ServidorCentral
- Todos los NodosWorker (Java y Python)
- ReniecWorker
- ClienteProxy

**Nota:** RabbitMQ y PostgreSQL seguirán corriendo en Docker.

## 📊 Arquitectura Técnica

### Componentes:

```
┌─────────────────┐
│  Cliente GUI    │ (Puerto local)
│  (Tkinter)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  ClienteProxy   │ (Puerto 9876)
│  (TCP Server)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    RabbitMQ     │ (Puerto 5672)
│   (RPC Pattern) │
└────┬──────┬─────┘
     │      │
     ▼      ▼
┌─────────┐ ┌──────────────┐
│Servidor │ │ ReniecWorker │
│Central  │ │  (SQLite)    │
└────┬────┘ └──────────────┘
     │
     ▼
┌────────────────────────┐
│    4 NodosWorker       │
│  Partición 0: Java 0,1 │
│  Partición 1: Py 2,3   │
└───────┬────────────────┘
        │
        ▼
┌─────────────────┐
│   PostgreSQL    │
│   (bd1_banco)   │
└─────────────────┘
```

### Distribución de Cuentas:

```python
particion = id_cuenta % 2
# Cuenta 1001 → Partición 1 (Nodos 2, 3)
# Cuenta 1002 → Partición 0 (Nodos 0, 1)
```

## 📚 Documentación

- **`documentacion/`**: Documentación técnica completa
- **`diagramas/`**: Diagramas de arquitectura y protocolos
- **`INSTRUCCIONES_APP_MOVIL.md`**: Guía para integración móvil
- **`recapitulacion.md`**: Historial de desarrollo y solución de problemas

## 🐛 Solución de Problemas

### Error: "RabbitMQ no está disponible"

```bash
# Verificar estado
docker ps | grep rabbitmq

# Iniciar si está detenido
docker start rabbitmq-server
```

### Error: "Connection refused al proxy"

```bash
# Verificar que el proxy esté escuchando
lsof -i :9876

# Ver logs
tail -f logs/cliente_proxy.log
```

### Error: "Timeout en operaciones"

```bash
# Verificar todos los servicios
ps aux | grep -E "(servidor_central|nodo_worker|reniec_worker)"

# Ver logs de errores
grep ERROR logs/*.log
```

## 📦 Estructura del Proyecto

```
PC3/
├── src/
│   ├── java/
│   │   ├── servidor_central/ServidorCentral.java
│   │   └── nodo_trabajador/NodoWorker.java
│   └── python/
│       ├── cliente_desktop/
│       │   ├── cliente_gui.py        # GUI principal
│       │   └── cliente_proxy.py      # Proxy TCP
│       ├── common/
│       │   ├── rpc_client.py         # Cliente RPC
│       │   └── proxy_client.py       # Cliente del proxy
│       ├── nodo_reniec/reniec_worker.py
│       └── nodo_trabajador/nodo_worker.py
├── scripts/
│   ├── iniciar_cluster.sh
│   ├── detener_cluster.sh
│   └── test_mapeo.py
├── config/
│   └── nodos_config.json
├── lib/                      # JARs de Java
├── scripts_bd/
│   ├── bd1_banco.sql
│   └── bd2_reniec.sql
└── README.md
```

## 👥 Equipo

- **[Tu Nombre]** - Backend Java/Python, Sistema Distribuido
- **[Compañero]** - App Móvil Kotlin/Android

## 📄 Licencia

Proyecto académico - Universidad Nacional de Ingeniería (UNI)
CC4P1 Programación Concurrente y Distribuida - 2025-II

---

## 🎯 Características Destacadas

- ✅ **Protocolo 2PC completo** para transacciones distribuidas
- ✅ **Validación con RENIEC** para autenticación
- ✅ **Particionamiento automático** de datos
- ✅ **Códigos QR** para integración móvil
- ✅ **Manejo robusto de errores** en todos los componentes
- ✅ **Logs detallados** para debugging
- ✅ **GUI moderna** con Tkinter

---

**🚀 ¡Sistema 100% funcional y listo para producción\!**

Para más información, consulta la documentación en `documentacion/` o los diagramas en `diagramas/`.
