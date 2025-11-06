package com.shibasito.banco.ui.loan

import android.os.Bundle
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.shibasito.banco.databinding.ActivityLoanBinding
import com.shibasito.banco.network.ProxyClient
import com.shibasito.banco.util.PreferencesManager
import kotlinx.coroutines.launch
import org.json.JSONObject

class LoanActivity : AppCompatActivity() {
    private lateinit var binding: ActivityLoanBinding
    private lateinit var proxyClient: ProxyClient
    private lateinit var prefs: PreferencesManager

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityLoanBinding.inflate(layoutInflater)
        setContentView(binding.root)

        proxyClient = ProxyClient()
        prefs = PreferencesManager(this)

        binding.btnRequest.setOnClickListener {
            solicitarPrestamo()
        }
    }

    private fun solicitarPrestamo() {
        val monto = binding.etAmount.text?.toString()?.trim()?.toDoubleOrNull()
        val plazo = binding.etTerm.text?.toString()?.trim()?.toIntOrNull()
        val dni = prefs.getUserDni() ?: return
        val idCuenta = prefs.getIdCuenta()

        if (monto == null || monto <= 0) {
            Toast.makeText(this, "Ingresa un monto válido", Toast.LENGTH_SHORT).show()
            return
        }

        if (plazo == null || plazo <= 0) {
            Toast.makeText(this, "Ingresa un plazo válido (en meses)", Toast.LENGTH_SHORT).show()
            return
        }

        binding.progressBar.visibility = android.view.View.VISIBLE
        binding.btnRequest.isEnabled = false

        lifecycleScope.launch {
            val result = proxyClient.solicitarPrestamo(idCuenta, dni, monto, plazo)

            binding.progressBar.visibility = android.view.View.GONE
            binding.btnRequest.isEnabled = true

            result.onSuccess { response ->
                if (response.getString("status") == "OK") {
                    Toast.makeText(
                        this@LoanActivity,
                        "Préstamo solicitado exitosamente",
                        Toast.LENGTH_SHORT
                    ).show()
                    binding.etAmount.text?.clear()
                    binding.etTerm.text?.clear()
                } else {
                    val error = response.optString("error", "Error al solicitar préstamo")
                    Toast.makeText(this@LoanActivity, error, Toast.LENGTH_LONG).show()
                }
            }.onFailure {
                Toast.makeText(
                    this@LoanActivity,
                    "Error: ${it.message}",
                    Toast.LENGTH_LONG
                ).show()
            }
        }
    }
}

