```mermaid
sequenceDiagram
    participant C as Cliente Desktop
    participant SC as Servidor Central
    participant N_A as Nodo Worker A (Origen)
    participant N_B as Nodo Worker B (Destino)

    C->>+SC: Iniciar Transferencia (RPC)
    Note over SC: 1. Recibe petición y genera un ID de transacción (tx_id)

    par Fase de Preparación (2PC)
        SC->>+N_A: PREPARE_TRANSFER(tx_id, from, to, amount)
        N_A-->>-SC: {status: "READY", tx_id: tx_id}
    and
        SC->>+N_B: PREPARE_TRANSFER(tx_id, from, to, amount)
        N_B-->>-SC: {status: "READY", tx_id: tx_id}
    end

    Note over SC: 2. Verifica que todos los nodos están listos.

    alt Si todos responden "READY"
        par Fase de Commit (2PC)
            SC->>N_A: COMMIT(tx_id)
        and
            SC->>N_B: COMMIT(tx_id)
        end
        SC-->>-C: {status: "OK", message: "Transferencia exitosa"}
    else Si algún nodo falla o no está listo
        par Fase de Abort (2PC)
            SC->>N_A: ABORT(tx_id)
        and
            SC->>N_B: ABORT(tx_id)
        end
        SC-->>-C: {status: "ERROR", error: "No se pudo completar..."}
    end
```
