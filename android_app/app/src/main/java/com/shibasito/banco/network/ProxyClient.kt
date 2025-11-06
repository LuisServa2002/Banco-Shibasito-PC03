package com.shibasito.banco.network

import android.util.Log
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.json.JSONObject
import java.io.BufferedReader
import java.io.InputStreamReader
import java.io.PrintWriter
import java.net.Socket
import java.net.SocketTimeoutException

class ProxyClient(
    private val host: String = "192.168.43.86", // IP de laptop en la misma red WiFi
    private val port: Int = 9876
) {
    private val TAG = "ProxyClient"
    private val timeout = 30000 // 30 segundos

    suspend fun sendRequest(payload: Map<String, Any>): Result<JSONObject> = withContext(Dispatchers.IO) {
        try {
            val socket = Socket(host, port)
            socket.soTimeout = timeout

            // Enviar JSON al proxy
            val writer = PrintWriter(socket.getOutputStream(), true)
            val jsonPayload = JSONObject(payload as Map<*, *>)
            writer.println(jsonPayload.toString())

            // ✅ Recibir solo UNA línea (el proxy siempre responde JSON + "\n")
            val reader = BufferedReader(InputStreamReader(socket.getInputStream()))
            val responseStr = reader.readLine()?.trim() ?: throw Exception("Respuesta vacía del servidor")

            socket.close()

            val jsonResponse = JSONObject(responseStr)
            Log.d(TAG, "Response: $jsonResponse")

            Result.success(jsonResponse)

        } catch (e: SocketTimeoutException) {
            Log.e(TAG, "Timeout error", e)
            Result.failure(Exception("Timeout: El servidor no respondió a tiempo"))
        } catch (e: Exception) {
            Log.e(TAG, "Connection error", e)
            Result.failure(e)
        }
    }

    suspend fun login(dni: String, idCuenta: Int): Result<JSONObject> {
        val payload = mapOf(
            "operacion" to "LOGIN",
            "dni" to dni,
            "id_cuenta" to idCuenta
        )
        return sendRequest(payload)
    }

    suspend fun consultarCuenta(idCuenta: Int): Result<JSONObject> {
        val payload = mapOf(
            "operacion" to "CONSULTAR_CUENTA",
            "id_cuenta" to idCuenta
        )
        return sendRequest(payload)
    }

    suspend fun transferir(
        cuentaOrigen: Int,
        cuentaDestino: Int,
        monto: Double
    ): Result<JSONObject> {
        val payload = mapOf(
            "operacion" to "TRANSFERIR",
            "cuenta_origen" to cuentaOrigen,
            "cuenta_destino" to cuentaDestino,
            "monto" to monto
        )
        return sendRequest(payload)
    }

    suspend fun solicitarPrestamo(
        idCuenta: Int,
        dni: String,
        monto: Double,
        plazo: Int
    ): Result<JSONObject> {
        val payload = mapOf(
            "operacion" to "SOLICITAR_PRESTAMO",
            "id_cuenta" to idCuenta,
            "dni" to dni,
            "monto" to monto,
            "plazo_meses" to plazo
        )
        return sendRequest(payload)
    }

    suspend fun generarQR(
        cuentaDestino: Int,
        monto: Double
    ): Result<JSONObject> {
        val payload = mapOf(
            "operacion" to "GENERAR_QR",
            "data" to mapOf(
                "tipo" to "TRANSFERENCIA",
                "cuenta_destino" to cuentaDestino,
                "monto" to monto,
                "timestamp" to java.text.SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss", java.util.Locale.getDefault()).format(
                    java.util.Date()
                ),
                "banco" to "Shibasito"
            )
        )
        return sendRequest(payload)
    }

    suspend fun consultarTransacciones(idCuenta: Int): Result<JSONObject> {
        val payload = mapOf(
            "operacion" to "CONSULTAR_TRANSACCIONES",
            "id_cuenta" to idCuenta
        )
        return sendRequest(payload)
    }
}
