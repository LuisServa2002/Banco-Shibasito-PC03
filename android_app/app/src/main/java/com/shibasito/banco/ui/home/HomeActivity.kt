package com.shibasito.banco.ui.home

import android.content.Intent
import android.os.Bundle
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import com.shibasito.banco.databinding.ActivityHomeBinding
import com.shibasito.banco.ui.balance.BalanceActivity
import com.shibasito.banco.ui.chat.ChatActivity
import com.shibasito.banco.ui.debt.DebtActivity
import com.shibasito.banco.ui.loan.LoanActivity
import com.shibasito.banco.ui.login.LoginActivity
import com.shibasito.banco.ui.qr.QRScanActivity
import com.shibasito.banco.util.PreferencesManager

class HomeActivity : AppCompatActivity() {
    private lateinit var binding: ActivityHomeBinding
    private lateinit var prefs: PreferencesManager

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityHomeBinding.inflate(layoutInflater)
        setContentView(binding.root)

        prefs = PreferencesManager(this)

        // Verificar si está logueado
        if (!prefs.isLoggedIn()) {
            startActivity(Intent(this, LoginActivity::class.java))
            finish()
            return
        }

        setupUI()
        setupClickListeners()
    }

    private fun setupUI() {
        val nombre = prefs.getUserNombre() ?: "Usuario"
        binding.tvWelcome.text = getString(com.shibasito.banco.R.string.welcome, nombre)
    }

    private fun setupClickListeners() {
        binding.cardChat.setOnClickListener {
            startActivity(Intent(this, ChatActivity::class.java))
        }

        binding.cardBalance.setOnClickListener {
            startActivity(Intent(this, BalanceActivity::class.java))
        }

        binding.cardQR.setOnClickListener {
            startActivity(Intent(this, QRScanActivity::class.java))
        }

        binding.cardLoan.setOnClickListener {
            startActivity(Intent(this, LoanActivity::class.java))
        }

        binding.cardDebt.setOnClickListener {
            startActivity(Intent(this, DebtActivity::class.java))
        }

        binding.btnLogout.setOnClickListener {
            showLogoutDialog()
        }
    }

    private fun showLogoutDialog() {
        AlertDialog.Builder(this)
            .setTitle("Cerrar Sesión")
            .setMessage("¿Estás seguro que deseas cerrar sesión?")
            .setPositiveButton("Sí") { _, _ ->
                prefs.clear()
                startActivity(Intent(this, LoginActivity::class.java))
                finish()
            }
            .setNegativeButton("No", null)
            .show()
    }
}

