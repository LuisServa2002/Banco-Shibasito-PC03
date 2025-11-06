package com.shibasito.banco.ui.balance

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.shibasito.banco.R
import com.shibasito.banco.data.model.Transaccion
import java.text.NumberFormat
import java.util.Locale

class TransaccionesAdapter(private val transacciones: List<Transaccion>) :
    RecyclerView.Adapter<TransaccionesAdapter.TransaccionViewHolder>() {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): TransaccionViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_transaccion, parent, false)
        return TransaccionViewHolder(view)
    }

    override fun onBindViewHolder(holder: TransaccionViewHolder, position: Int) {
        holder.bind(transacciones[position])
    }

    override fun getItemCount() = transacciones.size

    class TransaccionViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        private val tvId: TextView = itemView.findViewById(R.id.tvId)
        private val tvTipo: TextView = itemView.findViewById(R.id.tvTipo)
        private val tvMonto: TextView = itemView.findViewById(R.id.tvMonto)
        private val tvFecha: TextView = itemView.findViewById(R.id.tvFecha)

        fun bind(transaccion: Transaccion) {
            tvId.text = transaccion.id
            tvTipo.text = transaccion.tipo
            val formatter = NumberFormat.getCurrencyInstance(Locale("es", "PE"))
            tvMonto.text = formatter.format(transaccion.monto)
            tvFecha.text = transaccion.fecha
        }
    }
}

