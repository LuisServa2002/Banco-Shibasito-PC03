package com.shibasito.banco.data.model

data class ChatMensaje(
    val id: String,
    val texto: String,
    val esUsuario: Boolean,
    val timestamp: Long = System.currentTimeMillis(),
    val datos: Map<String, Any>? = null // Para datos estructurados (transacciones, deudas)
)

