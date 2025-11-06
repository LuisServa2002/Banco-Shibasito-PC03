package com.shibasito.banco.util

import android.content.Context
import android.content.SharedPreferences

class PreferencesManager(context: Context) {
    private val prefs: SharedPreferences = context.getSharedPreferences(
        PREFS_NAME,
        Context.MODE_PRIVATE
    )

    companion object {
        private const val PREFS_NAME = "BancoShibasitoPrefs"
        private const val KEY_DNI = "dni"
        private const val KEY_NOMBRE = "nombre"
        private const val KEY_ID_CUENTA = "id_cuenta"
        private const val KEY_SALDO = "saldo"
        private const val KEY_IS_LOGGED_IN = "is_logged_in"
    }

    fun saveUser(dni: String, nombre: String, idCuenta: Int, saldo: Double) {
        prefs.edit().apply {
            putString(KEY_DNI, dni)
            putString(KEY_NOMBRE, nombre)
            putInt(KEY_ID_CUENTA, idCuenta)
            putFloat(KEY_SALDO, saldo.toFloat())
            putBoolean(KEY_IS_LOGGED_IN, true)
            apply()
        }
    }

    fun getUserDni(): String? = prefs.getString(KEY_DNI, null)
    fun getUserNombre(): String? = prefs.getString(KEY_NOMBRE, null)
    fun getIdCuenta(): Int = prefs.getInt(KEY_ID_CUENTA, -1)
    fun getSaldo(): Double = prefs.getFloat(KEY_SALDO, 0f).toDouble()
    fun isLoggedIn(): Boolean = prefs.getBoolean(KEY_IS_LOGGED_IN, false)

    fun updateSaldo(saldo: Double) {
        prefs.edit().putFloat(KEY_SALDO, saldo.toFloat()).apply()
    }

    fun clear() {
        prefs.edit().clear().apply()
    }
}

