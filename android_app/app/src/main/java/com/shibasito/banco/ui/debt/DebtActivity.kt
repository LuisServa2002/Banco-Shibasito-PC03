package com.shibasito.banco.ui.debt

import android.os.Bundle
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.recyclerview.widget.LinearLayoutManager
import com.shibasito.banco.databinding.ActivityDebtBinding
import com.shibasito.banco.data.model.Deuda

class DebtActivity : AppCompatActivity() {
    private lateinit var binding: ActivityDebtBinding
    private val deudas = mutableListOf<Deuda>()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityDebtBinding.inflate(layoutInflater)
        setContentView(binding.root)

        setupRecyclerView()
        cargarDeudas()
    }

    private fun setupRecyclerView() {
        val adapter = DeudasAdapter(deudas) { deuda ->
            pagarDeuda(deuda)
        }
        binding.recyclerViewDeudas.apply {
            layoutManager = LinearLayoutManager(this@DebtActivity)
            this.adapter = adapter
        }
    }

    private fun cargarDeudas() {
        // Simular deudas (en producción vendría del backend)
        deudas.clear()
        deudas.add(
            Deuda(
                id = "87",
                descripcion = "Deuda Tienda",
                monto = 481.0,
                fechaVencimiento = "2025-11-06",
                estado = "pendiente"
            )
        )
        binding.recyclerViewDeudas.adapter?.notifyDataSetChanged()

        if (deudas.isEmpty()) {
            binding.tvNoDebts.visibility = android.view.View.VISIBLE
        } else {
            binding.tvNoDebts.visibility = android.view.View.GONE
        }
    }

    private fun pagarDeuda(deuda: Deuda) {
        Toast.makeText(this, "Función de pago de deuda: ${deuda.descripcion}", Toast.LENGTH_SHORT).show()
        // Aquí implementarías la lógica de pago
    }
}

