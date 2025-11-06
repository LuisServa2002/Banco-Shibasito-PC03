package com.shibasito.banco.ui.qr

import android.os.Bundle
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.journeyapps.barcodescanner.ScanContract
import com.journeyapps.barcodescanner.ScanOptions
import com.google.zxing.BarcodeFormat
import com.shibasito.banco.databinding.ActivityQrscanBinding
import com.shibasito.banco.data.model.QRData
import com.shibasito.banco.network.ProxyClient
import com.shibasito.banco.util.PreferencesManager
import com.google.gson.Gson
import kotlinx.coroutines.launch
import org.json.JSONObject

class QRScanActivity : AppCompatActivity() {
    private lateinit var binding: ActivityQrscanBinding
    private lateinit var proxyClient: ProxyClient
    private lateinit var prefs: PreferencesManager
    private val gson = Gson()

    private val qrLauncher = registerForActivityResult(ScanContract()) { result ->
        if (result.contents != null) {
            procesarQR(result.contents)
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityQrscanBinding.inflate(layoutInflater)
        setContentView(binding.root)

        proxyClient = ProxyClient()
        prefs = PreferencesManager(this)

        setupClickListeners()
    }

    private fun setupClickListeners() {
        binding.btnScanQR.setOnClickListener {
            escanearQR()
        }

        binding.btnGenerateQR.setOnClickListener {
            generarQR()
        }

        binding.btnPay.setOnClickListener {
            realizarPago()
        }
    }

    private fun escanearQR() {
        val options = ScanOptions()
        options.setDesiredBarcodeFormats(ScanOptions.QR_CODE)
        options.setPrompt("Escanea el código QR")
        options.setCameraId(0)
        options.setBeepEnabled(false)
        options.setBarcodeImageEnabled(true)
        qrLauncher.launch(options)
    }

    private fun procesarQR(contenido: String) {
        try {
            val qrData = gson.fromJson(contenido, QRData::class.java)
            binding.etDestination.setText(qrData.cuentaDestino?.toString() ?: "")
            binding.etAmount.setText(qrData.monto.toString())

            Toast.makeText(this, "QR escaneado correctamente", Toast.LENGTH_SHORT).show()
        } catch (e: Exception) {
            Toast.makeText(this, "Error al procesar QR: ${e.message}", Toast.LENGTH_LONG).show()
        }
    }

    private fun generarQR() {
        val cuentaDestino = binding.etDestination.text?.toString()?.trim()?.toIntOrNull()
        val monto = binding.etAmount.text?.toString()?.trim()?.toDoubleOrNull()

        if (cuentaDestino == null || monto == null || monto <= 0) {
            Toast.makeText(this, "Ingresa cuenta destino y monto válidos", Toast.LENGTH_SHORT).show()
            return
        }

        binding.progressBar.visibility = android.view.View.VISIBLE

        lifecycleScope.launch {
            val result = proxyClient.generarQR(cuentaDestino, monto)

            binding.progressBar.visibility = android.view.View.GONE

            result.onSuccess { response ->
                if (response.getString("status") == "OK") {
                    val qrImageBase64 = response.optString("qr_image", "")
                    if (qrImageBase64.isNotEmpty()) {
                        // Mostrar QR generado
                        mostrarQRGenerado(qrImageBase64)
                    } else {
                        Toast.makeText(this@QRScanActivity, "QR generado pero no se pudo mostrar", Toast.LENGTH_SHORT).show()
                    }
                } else {
                    Toast.makeText(this@QRScanActivity, "Error al generar QR", Toast.LENGTH_SHORT).show()
                }
            }.onFailure {
                Toast.makeText(this@QRScanActivity, "Error: ${it.message}", Toast.LENGTH_LONG).show()
            }
        }
    }

    private fun mostrarQRGenerado(qrImageBase64: String) {
        // Aquí podrías decodificar la imagen base64 y mostrarla en un ImageView
        Toast.makeText(this, "QR generado exitosamente", Toast.LENGTH_SHORT).show()
    }

    private fun realizarPago() {
        val cuentaDestino = binding.etDestination.text?.toString()?.trim()?.toIntOrNull()
        val monto = binding.etAmount.text?.toString()?.trim()?.toDoubleOrNull()
        val cuentaOrigen = prefs.getIdCuenta()

        if (cuentaDestino == null || monto == null || monto <= 0) {
            Toast.makeText(this, "Ingresa cuenta destino y monto válidos", Toast.LENGTH_SHORT).show()
            return
        }

        binding.progressBar.visibility = android.view.View.VISIBLE

        lifecycleScope.launch {
            val result = proxyClient.transferir(cuentaOrigen, cuentaDestino, monto)

            binding.progressBar.visibility = android.view.View.GONE

            result.onSuccess { response ->
                if (response.getString("status") == "OK") {
                    Toast.makeText(this@QRScanActivity, "Transacción Exitosa", Toast.LENGTH_SHORT).show()
                    binding.etDestination.text?.clear()
                    binding.etAmount.text?.clear()
                    prefs.updateSaldo(response.optDouble("balance", prefs.getSaldo()))
                } else {
                    val error = response.optString("error", "Error en la transacción")
                    Toast.makeText(this@QRScanActivity, error, Toast.LENGTH_LONG).show()
                }
            }.onFailure {
                Toast.makeText(this@QRScanActivity, "Error: ${it.message}", Toast.LENGTH_LONG).show()
            }
        }
    }
}

