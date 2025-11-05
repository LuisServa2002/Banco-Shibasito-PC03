# 🏦 Sistema Bancario Shibasito

Sistema bancario distribuido con arquitectura de microservicios usando RabbitMQ.

## 🏗️ Arquitectura

- **Backend:** Java + Python
- **Middleware:** RabbitMQ
- **Base de Datos:** PostgreSQL (Banco) + SQLite (RENIEC)
- **Cliente Desktop:** Python/Tkinter con generación de QR

## 📋 Requisitos

- Docker (para RabbitMQ y PostgreSQL)
- Java 11+
- Python 3.10+
- PostgreSQL cliente

## 🚀 Instalación

### 1. Clonar repositorio

```bash
git clone <tu-repo>
cd PC3
```

### 2. Crear entorno virtual

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows
```

### 3. Instalar dependencias Python

```bash
pip install pika qrcode pillow psycopg2-binary
```

### 4. Iniciar servicios Docker

```bash
# RabbitMQ
docker run -d --name rabbitmq-server \
  -p 5672:5672 -p 15672:15672 \
  rabbitmq:3-management

# PostgreSQL
docker run -d --name postgres-db \
  -e POSTGRES_PASSWORD=mysecretpassword \
  -p 5432:5432 postgres:13
```

### 5. Crear base de datos

```bash
docker exec -it postgres-db psql -U postgres
CREATE DATABASE bd1_banco;
\c bd1_banco
\i scripts_bd/bd1_banco.sql
\q
```

### 6. Iniciar sistema

```bash
./scripts/iniciar_cluster.sh
```

### 7. Ejecutar cliente GUI

```bash
python src/python/cliente_desktop/cliente_gui.py
```

## 🔐 Credenciales de Prueba

- DNI: `45678912` - Cuenta: `1001`
- DNI: `78901234` - Cuenta: `1002`
- DNI: `12345678` - Cuenta: `8008`

## 🧪 Tests

```bash
python test_mapeo.py
python test_login.py
```

## 📱 Código QR

La GUI genera códigos QR con formato:

```json
{
  "tipo": "TRANSFERENCIA",
  "cuenta_destino": 1001,
  "monto": 150.0,
  "timestamp": "2025-11-04T16:30:00",
  "banco": "Shibasito"
}
```

## 🛑 Detener Sistema

```bash
./scripts/detener_cluster.sh
```

## 📚 Documentación

Ver carpeta `documentacion/` para:

- Arquitectura detallada
- Diagramas de protocolo
- ADRs (Architectural Decision Records)

## 👥 Equipo

- [Tu nombre] - Backend Java/Python
- [Compañero] - App Móvil Kotlin

## 📄 Licencia

[Tu licencia]
