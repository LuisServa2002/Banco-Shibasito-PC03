package com.shibasito.banco.data.model

data class Prestamo(
    val id: String,
    val idCliente: String,
    val monto: Double,
    val montoPendiente: Double,
    val estado: String, // "activo", "pagado"
    val fechaSolicitud: String,
    val plazo: Int = 12 // meses
)

