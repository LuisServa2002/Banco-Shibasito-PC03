# 📱 Instrucciones de Instalación y Configuración

## Requisitos Previos

1. **Android Studio** (versión Hedgehog o superior)
2. **JDK 8** o superior
3. **Android SDK** con API 24+ instalado
4. **Proxy del servidor** corriendo en el puerto 9876

## Pasos de Instalación

### 1. Importar el Proyecto

1. Abre Android Studio
2. Selecciona `File > Open`
3. Navega a la carpeta `android_app`
4. Selecciona la carpeta y haz clic en `OK`
5. Espera a que Gradle sincronice el proyecto

### 2. Configurar la Conexión al Proxy

**IMPORTANTE**: Debes configurar la IP del servidor según tu entorno.

#### Para Emulador Android:
El emulador usa `10.0.2.2` para referirse al localhost de la máquina host. Ya está configurado por defecto.

#### Para Dispositivo Físico:
1. Asegúrate de que tu dispositivo y tu computadora estén en la misma red WiFi
2. Obtén la IP de tu computadora:
   - **Windows**: Abre CMD y ejecuta `ipconfig`
   - **Linux/Mac**: Abre terminal y ejecuta `ifconfig` o `ip addr`
3. Busca la dirección IPv4 (ejemplo: `192.168.1.100`)
4. Edita el archivo `app/src/main/java/com/shibasito/banco/network/ProxyClient.kt`
5. Cambia la línea 14:
   ```kotlin
   private val host: String = "192.168.1.100"  // Tu IP aquí
   ```

### 3. Iniciar el Proxy del Servidor

Antes de ejecutar la app, asegúrate de que el proxy esté corriendo:

```bash
# Desde la carpeta raíz del proyecto
python src/python/cliente_desktop/cliente_proxy.py
```

Deberías ver:
```
✓ Proxy escuchando en 127.0.0.1:9876
```

### 4. Compilar y Ejecutar

#### Opción A: Desde Android Studio
1. Conecta tu dispositivo Android o inicia un emulador
2. Haz clic en el botón `Run` (▶️) o presiona `Shift + F10`
3. Selecciona tu dispositivo/emulador
4. Espera a que la app se instale y ejecute

#### Opción B: Desde la Terminal
```bash
cd android_app
./gradlew installDebug
```

### 5. Verificar la Instalación

1. La app debería abrirse automáticamente
2. Deberías ver la pantalla de Login
3. Prueba con las credenciales de prueba:
   - DNI: `45678912`
   - Cuenta: `1001`

## Solución de Problemas

### Error: "Conexión rechazada"
- Verifica que el proxy esté corriendo en el puerto 9876
- Verifica que la IP en `ProxyClient.kt` sea correcta
- Si usas dispositivo físico, verifica que esté en la misma red WiFi

### Error: "Timeout"
- Verifica que el backend esté corriendo
- Verifica que RabbitMQ esté corriendo
- Revisa los logs del proxy para más detalles

### Error al compilar
```bash
# Limpia el proyecto
./gradlew clean

# Reconstruye
./gradlew build
```

### Error: "SDK not found"
1. Abre `File > Settings > Appearance & Behavior > System Settings > Android SDK`
2. Instala el SDK Platform para API 34
3. Instala las herramientas de build necesarias

### Error al escanear QR
- Verifica que la app tenga permisos de cámara
- Ve a `Configuración > Apps > Banco Shibasito > Permisos`
- Activa el permiso de cámara

## Configuración de Red Adicional

Si necesitas cambiar el puerto del proxy:

1. Edita `ProxyClient.kt` línea 15:
   ```kotlin
   private val port: Int = 9876  // Cambia el puerto aquí
   ```

2. Asegúrate de que el proxy esté configurado para usar el mismo puerto

## Credenciales de Prueba

| DNI | Cuenta | Nombre |
|-----|--------|--------|
| 45678912 | 1001 | MARÍA ELENA GARCÍA FLORES |
| 87654321 | 1002 | CARLOS ALBERTO RAMÍREZ SOTO |
| 98765432 | 8008 | JOSÉ MIGUEL TORRES VEGA |

## Estructura de la App

- **LoginActivity**: Pantalla de inicio de sesión
- **HomeActivity**: Menú principal con opciones
- **ChatActivity**: Chat con el bot bancario (ChatB)
- **BalanceActivity**: Consulta de saldo y transacciones
- **QRScanActivity**: Escaneo y generación de códigos QR
- **LoanActivity**: Solicitud de préstamos
- **DebtActivity**: Gestión de deudas

## Notas Importantes

1. **Red**: La app requiere conexión de red activa
2. **Proxy**: El proxy debe estar corriendo antes de usar la app
3. **Backend**: El backend completo (RabbitMQ, PostgreSQL, etc.) debe estar operativo
4. **Permisos**: La app solicitará permisos de Internet y Cámara (para QR)

## Soporte

Si encuentras problemas:
1. Revisa los logs de Android Studio (pestaña Logcat)
2. Revisa los logs del proxy en `logs/cliente_proxy.log`
3. Verifica que todos los servicios del backend estén corriendo

