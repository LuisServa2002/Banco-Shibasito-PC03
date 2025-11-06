package com.shibasito.banco.ui.debt

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.shibasito.banco.R
import com.shibasito.banco.data.model.Deuda
import java.text.NumberFormat
import java.util.Locale

class DeudasAdapter(
    private val deudas: List<Deuda>,
    private val onPayClick: (Deuda) -> Unit
) : RecyclerView.Adapter<DeudasAdapter.DeudaViewHolder>() {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): DeudaViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_deuda, parent, false)
        return DeudaViewHolder(view)
    }

    override fun onBindViewHolder(holder: DeudaViewHolder, position: Int) {
        holder.bind(deudas[position])
    }

    override fun getItemCount() = deudas.size

    inner class DeudaViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        private val tvId: TextView = itemView.findViewById(R.id.tvId)
        private val tvDescripcion: TextView = itemView.findViewById(R.id.tvDescripcion)
        private val tvMonto: TextView = itemView.findViewById(R.id.tvMonto)
        private val tvFecha: TextView = itemView.findViewById(R.id.tvFecha)
        private val btnPay: Button = itemView.findViewById(R.id.btnPay)

        fun bind(deuda: Deuda) {
            tvId.text = "ID: ${deuda.id}"
            tvDescripcion.text = deuda.descripcion
            val formatter = NumberFormat.getCurrencyInstance(Locale("es", "PE"))
            tvMonto.text = formatter.format(deuda.monto)
            tvFecha.text = "Vence: ${deuda.fechaVencimiento}"

            btnPay.setOnClickListener {
                onPayClick(deuda)
            }
        }
    }
}

