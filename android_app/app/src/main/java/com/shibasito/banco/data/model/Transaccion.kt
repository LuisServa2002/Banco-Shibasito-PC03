package com.shibasito.banco.data.model

import java.util.Date

data class Transaccion(
    val id: String,
    val idCuenta: Int,
    val tipo: String, // "deposito", "retiro", "transferencia", "comision"
    val monto: Double,
    val fecha: String,
    val descripcion: String = ""
)

