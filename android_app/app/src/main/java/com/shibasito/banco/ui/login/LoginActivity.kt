package com.shibasito.banco.ui.login

import android.content.Intent
import android.os.Bundle
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.shibasito.banco.databinding.ActivityLoginBinding
import com.shibasito.banco.network.ProxyClient
import com.shibasito.banco.ui.home.HomeActivity
import com.shibasito.banco.util.PreferencesManager
import kotlinx.coroutines.launch
import org.json.JSONObject

class LoginActivity : AppCompatActivity() {
    private lateinit var binding: ActivityLoginBinding
    private lateinit var proxyClient: ProxyClient
    private lateinit var prefs: PreferencesManager

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityLoginBinding.inflate(layoutInflater)
        setContentView(binding.root)

        proxyClient = ProxyClient()
        prefs = PreferencesManager(this)

        // Si ya está logueado, ir a Home
        if (prefs.isLoggedIn()) {
            startActivity(Intent(this, HomeActivity::class.java))
            finish()
            return
        }

        binding.btnLogin.setOnClickListener {
            val dni = binding.etDni.text?.toString()?.trim() ?: ""
            val idCuenta = binding.etAccount.text?.toString()?.trim()?.toIntOrNull()

            if (dni.isEmpty() || idCuenta == null) {
                Toast.makeText(this, "Por favor completa todos los campos", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }

            login(dni, idCuenta)
        }
    }

    private fun login(dni: String, idCuenta: Int) {
        binding.btnLogin.isEnabled = false
        binding.progressBar.visibility = android.view.View.VISIBLE

        lifecycleScope.launch {
            val result = proxyClient.login(dni, idCuenta)
            
            binding.btnLogin.isEnabled = true
            binding.progressBar.visibility = android.view.View.GONE

            result.onSuccess { response ->
                if (response.getString("status") == "OK") {
                    val nombre = response.getString("nombre")
                    val balance = response.optDouble("balance", 0.0)
                    
                    prefs.saveUser(dni, nombre, idCuenta, balance)
                    
                    Toast.makeText(this@LoginActivity, "Bienvenido, $nombre", Toast.LENGTH_SHORT).show()
                    
                    val intent = Intent(this@LoginActivity, HomeActivity::class.java)
                    startActivity(intent)
                    finish()
                } else {
                    val error = response.optString("error", "Error al iniciar sesión")
                    Toast.makeText(this@LoginActivity, error, Toast.LENGTH_LONG).show()
                }
            }.onFailure { exception ->
                Toast.makeText(
                    this@LoginActivity,
                    "Error: ${exception.message}",
                    Toast.LENGTH_LONG
                ).show()
            }
        }
    }
}

