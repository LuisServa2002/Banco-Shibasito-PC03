package com.shibasito.banco.data.model

data class Usuario(
    val dni: String,
    val nombre: String,
    val idCuenta: Int,
    val saldo: Double = 0.0
)

