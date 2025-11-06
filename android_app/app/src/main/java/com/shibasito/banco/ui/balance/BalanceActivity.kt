package com.shibasito.banco.ui.balance

import android.os.Bundle
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.LinearLayoutManager
import com.shibasito.banco.databinding.ActivityBalanceBinding
import com.shibasito.banco.data.model.Transaccion
import com.shibasito.banco.network.ProxyClient
import com.shibasito.banco.util.PreferencesManager
import kotlinx.coroutines.launch
import org.json.JSONArray
import org.json.JSONObject
import java.text.NumberFormat
import java.util.Locale

class BalanceActivity : AppCompatActivity() {
    private lateinit var binding: ActivityBalanceBinding
    private lateinit var transaccionesAdapter: TransaccionesAdapter
    private val transacciones = mutableListOf<Transaccion>()
    private lateinit var proxyClient: ProxyClient
    private lateinit var prefs: PreferencesManager

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityBalanceBinding.inflate(layoutInflater)
        setContentView(binding.root)

        proxyClient = ProxyClient()
        prefs = PreferencesManager(this)

        setupRecyclerView()
        cargarDatos()
    }

    private fun setupRecyclerView() {
        transaccionesAdapter = TransaccionesAdapter(transacciones)
        binding.recyclerViewTransacciones.apply {
            layoutManager = LinearLayoutManager(this@BalanceActivity)
            adapter = transaccionesAdapter
        }
    }

    private fun cargarDatos() {
        binding.progressBar.visibility = android.view.View.VISIBLE

        lifecycleScope.launch {
            val idCuenta = prefs.getIdCuenta()
            val result = proxyClient.consultarCuenta(idCuenta)

            binding.progressBar.visibility = android.view.View.GONE

            result.onSuccess { response ->
                if (response.getString("status") == "OK") {
                    val saldo = response.optDouble("balance", 0.0)
                    val formatter = NumberFormat.getCurrencyInstance(Locale("es", "PE"))
                    binding.tvSaldo.text = formatter.format(saldo)

                    // Cargar transacciones
                    val transaccionesArray = response.optJSONArray("transacciones") ?: JSONArray()
                    transacciones.clear()
                    for (i in 0 until transaccionesArray.length()) {
                        val trans = transaccionesArray.getJSONObject(i)
                        val transaccion = Transaccion(
                            id = trans.optString("id_transac", ""),
                            idCuenta = trans.optInt("id_cuenta", 0),
                            tipo = trans.optString("tipo", ""),
                            monto = trans.optDouble("monto", 0.0),
                            fecha = trans.optString("fecha", ""),
                            descripcion = trans.optString("descripcion", "")
                        )
                        transacciones.add(transaccion)
                    }
                    transaccionesAdapter.notifyDataSetChanged()
                } else {
                    Toast.makeText(
                        this@BalanceActivity,
                        "Error al cargar datos",
                        Toast.LENGTH_SHORT
                    ).show()
                }
            }.onFailure {
                Toast.makeText(
                    this@BalanceActivity,
                    "Error de conexión: ${it.message}",
                    Toast.LENGTH_LONG
                ).show()
            }
        }
    }
}

