package com.shibasito.banco.ui.chat

import android.os.Bundle
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.LinearLayoutManager
import com.shibasito.banco.databinding.ActivityChatBinding
import com.shibasito.banco.data.model.ChatMensaje
import com.shibasito.banco.network.ProxyClient
import com.shibasito.banco.util.PreferencesManager
import kotlinx.coroutines.launch
import org.json.JSONObject

class ChatActivity : AppCompatActivity() {
    private lateinit var binding: ActivityChatBinding
    private lateinit var chatAdapter: ChatAdapter
    private val mensajes = mutableListOf<ChatMensaje>()
    private lateinit var proxyClient: ProxyClient
    private lateinit var prefs: PreferencesManager

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityChatBinding.inflate(layoutInflater)
        setContentView(binding.root)

        proxyClient = ProxyClient()
        prefs = PreferencesManager(this)

        setupRecyclerView()
        setupClickListeners()

        // Mensaje de bienvenida
        agregarMensajeBot("Hola! Soy ChatB, tu asistente bancario. ¿En qué puedo ayudarte?")
    }

    private fun setupRecyclerView() {
        chatAdapter = ChatAdapter(mensajes)
        binding.recyclerViewChat.apply {
            layoutManager = LinearLayoutManager(this@ChatActivity)
            adapter = chatAdapter
        }
    }

    private fun setupClickListeners() {
        binding.btnSend.setOnClickListener {
            val mensaje = binding.etMessage.text?.toString()?.trim() ?: ""
            if (mensaje.isNotEmpty()) {
                enviarMensaje(mensaje)
                binding.etMessage.text?.clear()
            }
        }
    }

    private fun enviarMensaje(texto: String) {
        val mensajeUsuario = ChatMensaje(
            id = System.currentTimeMillis().toString(),
            texto = texto,
            esUsuario = true
        )
        mensajes.add(mensajeUsuario)
        chatAdapter.notifyItemInserted(mensajes.size - 1)
        binding.recyclerViewChat.scrollToPosition(mensajes.size - 1)

        // Procesar mensaje del bot
        procesarMensajeBot(texto.lowercase())
    }

    private fun procesarMensajeBot(texto: String) {
        when {
            texto.contains("transacciones") || texto.contains("movimientos") -> {
                consultarTransacciones()
            }
            texto.contains("saldo") -> {
                consultarSaldo()
            }
            texto.contains("deuda") || texto.contains("deudas") -> {
                consultarDeudas()
            }
            texto.contains("préstamo") || texto.contains("prestamo") -> {
                agregarMensajeBot("Para solicitar un préstamo, ve al menú principal y selecciona 'Solicitar Préstamo'")
            }
            else -> {
                agregarMensajeBot("No entendí tu solicitud. Puedes pedirme tus transacciones, saldo o deudas.")
            }
        }
    }

    private fun consultarTransacciones() {
        agregarMensajeBot("Consultando tus transacciones del mes...")
        
        lifecycleScope.launch {
            val idCuenta = prefs.getIdCuenta()
            val result = proxyClient.consultarCuenta(idCuenta)
            
            result.onSuccess { response ->
                if (response.getString("status") == "OK") {
                    val transacciones = response.optJSONArray("transacciones") ?: org.json.JSONArray()
                    val mensaje = StringBuilder("Tus transacciones del mes:\n\n")
                    
                    for (i in 0 until transacciones.length()) {
                        val trans = transacciones.getJSONObject(i)
                        val id = trans.optString("id_transac", "")
                        val tipo = trans.optString("tipo", "")
                        val monto = trans.optDouble("monto", 0.0)
                        mensaje.append("$id $tipo $monto\n")
                    }
                    
                    agregarMensajeBot(mensaje.toString())
                } else {
                    agregarMensajeBot("Error al consultar transacciones")
                }
            }.onFailure {
                agregarMensajeBot("Error de conexión. Intenta más tarde.")
            }
        }
    }

    private fun consultarSaldo() {
        lifecycleScope.launch {
            val idCuenta = prefs.getIdCuenta()
            val result = proxyClient.consultarCuenta(idCuenta)
            
            result.onSuccess { response ->
                if (response.getString("status") == "OK") {
                    val saldo = response.optDouble("balance", 0.0)
                    agregarMensajeBot("Tu saldo disponible es: S/ $saldo")
                } else {
                    agregarMensajeBot("Error al consultar saldo")
                }
            }.onFailure {
                agregarMensajeBot("Error de conexión. Intenta más tarde.")
            }
        }
    }

    private fun consultarDeudas() {
        // Simular consulta de deudas
        agregarMensajeBot("Tienes una deuda que vence en 2 días...\n\nId Deuda Monto\n87 Deuda Tienda 481")
    }

    private fun agregarMensajeBot(texto: String, datos: Map<String, Any>? = null) {
        val mensaje = ChatMensaje(
            id = System.currentTimeMillis().toString(),
            texto = texto,
            esUsuario = false,
            datos = datos
        )
        mensajes.add(mensaje)
        chatAdapter.notifyItemInserted(mensajes.size - 1)
        binding.recyclerViewChat.scrollToPosition(mensajes.size - 1)
    }
}

