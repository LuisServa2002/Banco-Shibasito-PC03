# 📱 Aplicación Móvil Banco Shibasito

Aplicación móvil Android desarrollada en Kotlin para el sistema bancario Shibasito.

## 🎯 Características

- ✅ **Login/Autenticación**: Validación con DNI y número de cuenta mediante RENIEC
- ✅ **Chat Banco**: Asistente virtual (ChatB) para consultas bancarias
- ✅ **Consulta de Saldo**: Visualización de saldo y transacciones recientes
- ✅ **Pago con QR**: Escaneo y generación de códigos QR para transacciones
- ✅ **Solicitud de Préstamos**: Solicitud de préstamos desde la app
- ✅ **Gestión de Deudas**: Visualización y pago de deudas pendientes

## 🏗️ Arquitectura

- **Lenguaje**: Kotlin
- **SDK Mínimo**: Android 7.0 (API 24)
- **SDK Objetivo**: Android 14 (API 34)
- **Comunicación**: TCP Socket con proxy local (puerto 9876)
- **Librerías principales**:
  - Material Design Components
  - ZXing para códigos QR
  - Kotlin Coroutines
  - Gson para JSON

## 📋 Requisitos

- Android Studio Hedgehog o superior
- JDK 8 o superior
- Android SDK 34
- Dispositivo Android o emulador con API 24+

## 🚀 Instalación

1. **Importar proyecto en Android Studio**
   ```bash
   # Abrir Android Studio y seleccionar "Open an existing project"
   # Navegar a la carpeta android_app
   ```

2. **Configurar la conexión al proxy**
   - En `ProxyClient.kt`, cambiar el host según tu entorno:
     - Emulador Android: `10.0.2.2` (localhost de la máquina host)
     - Dispositivo físico: IP de tu máquina (ej: `192.168.1.100`)

3. **Asegurar que el proxy esté corriendo**
   ```bash
   # En el proyecto principal, ejecutar:
   python src/python/cliente_desktop/cliente_proxy.py
   ```

4. **Compilar y ejecutar**
   - En Android Studio: `Run > Run 'app'`
   - O desde la terminal: `./gradlew installDebug`

## 📱 Uso

### Login
- Ingresa tu DNI y número de cuenta
- El sistema validará tus credenciales con RENIEC

### Chat Banco
- Escribe mensajes como:
  - "Envía mis transacciones del mes"
  - "Cuál es mi saldo"
  - "Tengo deudas"
- El bot ChatB responderá automáticamente

### Pago con QR
- Opción 1: Escanear código QR de otra persona/comercio
- Opción 2: Ingresar cuenta destino y monto manualmente
- Generar QR para recibir pagos

### Solicitar Préstamo
- Ingresa el monto deseado
- Selecciona el plazo en meses
- La solicitud se validará con RENIEC

## 🔧 Configuración de Red

### Para Emulador Android
El emulador usa `10.0.2.2` para referirse al localhost de la máquina host.

### Para Dispositivo Físico
1. Conectar dispositivo y computadora a la misma red WiFi
2. Obtener IP de la computadora:
   ```bash
   # Windows
   ipconfig
   
   # Linux/Mac
   ifconfig
   ```
3. Actualizar `ProxyClient.kt` con la IP obtenida

## 📁 Estructura del Proyecto

```
android_app/
├── app/
│   └── src/
│       └── main/
│           ├── java/com/shibasito/banco/
│           │   ├── data/model/          # Modelos de datos
│           │   ├── network/             # Cliente de red (ProxyClient)
│           │   ├── ui/                  # Actividades y adaptadores
│           │   │   ├── login/
│           │   │   ├── home/
│           │   │   ├── chat/
│           │   │   ├── balance/
│           │   │   ├── qr/
│           │   │   ├── loan/
│           │   │   └── debt/
│           │   └── util/                # Utilidades (PreferencesManager)
│           └── res/                     # Recursos (layouts, strings, etc.)
├── build.gradle.kts
└── settings.gradle.kts
```

## 🔐 Credenciales de Prueba

- DNI: `45678912` - Cuenta: `1001`
- DNI: `87654321` - Cuenta: `1002`
- DNI: `98765432` - Cuenta: `8008`

## 🐛 Solución de Problemas

### Error de conexión
- Verificar que el proxy esté corriendo en el puerto 9876
- Verificar que la IP en `ProxyClient.kt` sea correcta
- Verificar permisos de Internet en `AndroidManifest.xml`

### Error al escanear QR
- Verificar permisos de cámara en la configuración del dispositivo
- Asegurarse de que la cámara esté disponible

### Build errors
- Limpiar proyecto: `Build > Clean Project`
- Reconstruir: `Build > Rebuild Project`
- Sincronizar Gradle: `File > Sync Project with Gradle Files`

## 📝 Notas

- La app requiere conexión de red activa
- El proxy debe estar corriendo antes de usar la app
- Los datos se almacenan localmente usando SharedPreferences
- Para producción, se recomienda usar HTTPS y autenticación más robusta

## 👥 Equipo

Desarrollado como parte del proyecto de Banco Shibasito para CC4P1 - Programación Concurrente y Distribuida.

