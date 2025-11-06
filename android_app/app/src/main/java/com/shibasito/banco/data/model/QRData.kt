package com.shibasito.banco.data.model

data class QRData(
    val tipo: String, // "TRANSFERENCIA", "PAGO"
    val cuentaDestino: Int? = null,
    val monto: Double,
    val timestamp: String,
    val banco: String = "Shibasito"
)

