# 🚀 Pasos para Ejecutar la Aplicación Móvil

## 📋 Pasos Rápidos

### 1️⃣ Iniciar el Backend (Servidor)

```bash
# Desde la carpeta raíz del proyecto
python src/python/cliente_desktop/cliente_proxy.py
```

**Debes ver:**
```
✓ Proxy escuchando en 127.0.0.1:9876
```

> ⚠️ **IMPORTANTE**: Deja esta terminal abierta y corriendo.

---

### 2️⃣ Configurar la Conexión (Solo si usas dispositivo físico)

Si usas **dispositivo físico Android**, edita:

📁 `android_app/app/src/main/java/com/shibasito/banco/network/ProxyClient.kt`

Línea 14, cambia:
```kotlin
private val host: String = "10.0.2.2"  // Para emulador
```

Por la IP de tu computadora:
```kotlin
private val host: String = "192.168.1.XXX"  // Tu IP aquí
```

**Para obtener tu IP:**
- Windows: `ipconfig` en CMD
- Linux/Mac: `ifconfig` en terminal

> ✅ Si usas **emulador Android**, no necesitas cambiar nada.

---

### 3️⃣ Abrir en Android Studio

1. Abre **Android Studio**
2. `File > Open`
3. Selecciona la carpeta `android_app`
4. Espera a que Gradle sincronice (puede tomar 2-5 minutos la primera vez)

---

### 4️⃣ Conectar Dispositivo o Emulador

**Opción A: Emulador**
- `Tools > Device Manager > Create Device`
- Selecciona cualquier dispositivo Android
- Haz clic en ▶️ (Play) para iniciar el emulador

**Opción B: Dispositivo Físico**
- Activa **Opciones de Desarrollador** en tu teléfono
- Activa **Depuración USB**
- Conecta por USB
- Acepta la conexión en el teléfono

---

### 5️⃣ Ejecutar la App

1. En Android Studio, haz clic en el botón **▶️ Run** (o presiona `Shift + F10`)
2. Selecciona tu dispositivo/emulador
3. Espera a que se instale y ejecute

---

### 6️⃣ Probar la Aplicación

**Credenciales de prueba:**
- DNI: `45678912`
- Cuenta: `1001`

---

## ✅ Checklist Rápido

- [ ] Proxy corriendo en puerto 9876
- [ ] IP configurada (solo dispositivo físico)
- [ ] Proyecto abierto en Android Studio
- [ ] Dispositivo/emulador conectado
- [ ] App instalada y ejecutándose

---

## 🐛 Problemas Comunes

| Problema | Solución |
|----------|----------|
| "Conexión rechazada" | Verifica que el proxy esté corriendo |
| "Timeout" | Verifica que el backend esté operativo |
| Error al compilar | `File > Sync Project with Gradle Files` |
| No detecta dispositivo | Verifica cable USB / emulador iniciado |

---

## 📱 Resultado Esperado

Al ejecutar, deberías ver:
1. Pantalla de Login
2. Ingresar DNI y cuenta
3. Pantalla principal con opciones
4. Todas las funcionalidades disponibles

¡Listo! 🎉

