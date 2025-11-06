package com.shibasito.banco

import android.content.Intent
import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import com.shibasito.banco.ui.home.HomeActivity
import com.shibasito.banco.ui.login.LoginActivity
import com.shibasito.banco.util.PreferencesManager

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val prefs = PreferencesManager(this)

        // Redirigir a Login o Home según el estado de sesión
        val intent = if (prefs.isLoggedIn()) {
            Intent(this, HomeActivity::class.java)
        } else {
            Intent(this, LoginActivity::class.java)
        }

        startActivity(intent)
        finish()
    }
}

