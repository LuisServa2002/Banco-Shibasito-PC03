package com.shibasito.banco.data.model

data class Deuda(
    val id: String,
    val descripcion: String,
    val monto: Double,
    val fechaVencimiento: String,
    val estado: String = "pendiente"
)

