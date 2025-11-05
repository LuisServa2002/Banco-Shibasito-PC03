package servidor_central;

import com.rabbitmq.client.*;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.util.*;
import java.util.concurrent.*;
import java.util.stream.Collectors;
import org.json.JSONObject;
import org.json.JSONArray;

public class ServidorCentral {

    private int partitions;
    private final Map<Integer, List<NodeInfo>> partitionsMap = new HashMap<>();
    private final ExecutorService pool = Executors.newCachedThreadPool();

    private com.rabbitmq.client.Connection rabbitConnection;
    private Channel rabbitChannel;

    private static final String CLIENT_REQUEST_QUEUE = "client_requests_queue";
    private static final String WORKER_EXCHANGE = "worker_exchange";
    private static final String RENIEC_QUEUE = "reniec_queue";

    private static final String DB_URL = "jdbc:postgresql://localhost:5432/bd1_banco";
    private static final String DB_USER = "postgres";
    private static final String DB_PASSWORD = "mysecretpassword";

    static class NodeInfo {
        int id;
        String queueName;
        String host;
        int port;

        NodeInfo(int id, String host, int port) {
            this.id = id;
            this.host = host;
            this.port = port;
            this.queueName = "worker_queue_" + id;
        }

        @Override
        public String toString() {
            return String.format("Node{id=%d, queue=%s, host=%s, port=%d}", id, queueName, host, port);
        }

        @Override
        public boolean equals(Object o) {
            if (this == o) return true;
            if (o == null || getClass() != o.getClass()) return false;
            NodeInfo nodeInfo = (NodeInfo) o;
            return id == nodeInfo.id;
        }

        @Override
        public int hashCode() {
            return Objects.hash(id);
        }
    }

    public ServidorCentral(String configFile) throws Exception {
        loadConfig(configFile);
        initRabbitMQ();
    }

    private void initRabbitMQ() throws Exception {
        System.out.println("Inicializando conexión con RabbitMQ...");
        ConnectionFactory factory = new ConnectionFactory();
        factory.setHost("localhost");
        this.rabbitConnection = factory.newConnection();
        this.rabbitChannel = rabbitConnection.createChannel();
        
        this.rabbitChannel.queueDeclare(CLIENT_REQUEST_QUEUE, true, false, false, null);
        System.out.println("  ✓ Cola de clientes declarada: " + CLIENT_REQUEST_QUEUE);
        
        this.rabbitChannel.exchangeDeclare(WORKER_EXCHANGE, "direct");
        System.out.println("  ✓ Exchange de workers declarado: " + WORKER_EXCHANGE);
        
        this.rabbitChannel.queueDeclare(RENIEC_QUEUE, true, false, false, null);
        System.out.println("  ✓ Cola de RENIEC declarada: " + RENIEC_QUEUE);
        
        System.out.println("✓ RabbitMQ inicializado correctamente");
        System.out.println("Servidor Central esperando mensajes de clientes en la cola: " + CLIENT_REQUEST_QUEUE);
    }

    private void loadConfig(String configPath) throws IOException {
        System.out.println("========================================");
        System.out.println("Cargando configuración desde: " + configPath);
        System.out.println("========================================");
        
        String content = new String(java.nio.file.Files.readAllBytes(java.nio.file.Paths.get(configPath)));
        JSONObject config = new JSONObject(content);
        
        this.partitions = config.getInt("partitions");
        System.out.println("Número de particiones configuradas: " + this.partitions);
        
        JSONObject partitionsMapJson = config.getJSONObject("partitions_map");
        
        int totalNodes = 0;
        for (String partitionKey : partitionsMapJson.keySet()) {
            int partitionId = Integer.parseInt(partitionKey);
            JSONArray nodesArray = partitionsMapJson.getJSONArray(partitionKey);
            
            List<NodeInfo> nodesList = new ArrayList<>();
            for (int i = 0; i < nodesArray.length(); i++) {
                JSONObject nodeJson = nodesArray.getJSONObject(i);
                int nodeId = nodeJson.getInt("id");
                String host = nodeJson.getString("host");
                int port = nodeJson.getInt("port");
                
                NodeInfo node = new NodeInfo(nodeId, host, port);
                nodesList.add(node);
                totalNodes++;
                
                System.out.println("  [Partición " + partitionId + "] Registrado: " + node);
            }
            
            partitionsMap.put(partitionId, nodesList);
        }
        
        System.out.println("========================================");
        System.out.println("✓ Configuración cargada exitosamente:");
        System.out.println("  - Particiones: " + this.partitions);
        System.out.println("  - Nodos totales: " + totalNodes);
        System.out.println("========================================");
    }

    public void start() throws IOException {
        System.out.println("[ServidorCentral] Escuchando en cola " + CLIENT_REQUEST_QUEUE);
        DeliverCallback deliverCallback = (consumerTag, delivery) -> {
            pool.submit(() -> handleMessage(delivery));
        };
        rabbitChannel.basicConsume(CLIENT_REQUEST_QUEUE, true, deliverCallback, consumerTag -> {});
    }

    private void handleMessage(Delivery delivery) {
        AMQP.BasicProperties properties = delivery.getProperties();
        String response = "";
        try {
            String message = new String(delivery.getBody(), StandardCharsets.UTF_8);
            System.out.println("\n[>>>] Mensaje recibido del cliente: '" + message + "'");
            JSONObject req = new JSONObject(message);
            String type = req.getString("type").toUpperCase();

            switch (type) {
                case "LOGIN":
                    response = handleLogin(req);
                    break;
                case "CONSULTAR_CUENTA":
                    int acc = req.getInt("account");
                    int partition = getActivePartitionForAccount(acc);
                    response = forwardToPartition(partition, message);
                    break;
                case "TRANSFERIR_CUENTA":
                    response = handleTransferencia(req);
                    break;
                case "VALIDAR_DNI":
                    response = callRpc("", RENIEC_QUEUE, message);
                    break;
                case "SOLICITAR_PRESTAMO":
                    response = handleSolicitarPrestamo(req);
                    break;
                case "CONSULTAR_HISTORIAL":
                    response = handleConsultarHistorial(req);
                    break;
                default:
                    response = new JSONObject().put("status", "ERROR").put("error", "Tipo desconocido: " + type).toString();
            }
            
            System.out.println("[<<<] Respuesta al cliente: " + response);
        } catch (Exception e) {
            System.err.println("[ERROR] Error procesando mensaje: " + e.getMessage());
            e.printStackTrace();
            response = new JSONObject().put("status", "ERROR").put("error", e.getMessage()).toString();
        } finally {
            try {
                AMQP.BasicProperties replyProps = new AMQP.BasicProperties.Builder()
                    .correlationId(properties.getCorrelationId()).build();
                rabbitChannel.basicPublish("", properties.getReplyTo(), replyProps, response.getBytes(StandardCharsets.UTF_8));
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }

    private String handleTransferencia(JSONObject req) {
        String txId = UUID.randomUUID().toString();
        try {
            int fromAccount = req.getInt("from_account");
            int toAccount = req.getInt("to_account");
            double amount = req.getDouble("amount");

            System.out.println("[2PC] Iniciando transferencia: " + fromAccount + " -> " + toAccount + " ($" + amount + ")");
            
            int fromPartition = getActivePartitionForAccount(fromAccount);
            int toPartition = getActivePartitionForAccount(toAccount);
            
            NodeInfo fromNode = partitionsMap.get(fromPartition).get(0);
            NodeInfo toNode = partitionsMap.get(toPartition).get(0);

            Set<NodeInfo> involvedNodes = new HashSet<>(Arrays.asList(fromNode, toNode));
            System.out.println("[2PC] Nodos involucrados: " + involvedNodes);

            JSONObject prepareMessage = new JSONObject()
                .put("type", "PREPARE_TRANSFER")
                .put("tx_id", txId)
                .put("from", fromAccount)
                .put("to", toAccount)
                .put("amount", amount);

            System.out.println("[2PC] FASE 1: PREPARE");
            List<CompletableFuture<String>> prepareFutures = involvedNodes.stream()
                .map(node -> CompletableFuture.supplyAsync(() -> {
                    try {
                        return callRpc(WORKER_EXCHANGE, node.queueName, prepareMessage.toString());
                    } catch (Exception e) {
                        throw new RuntimeException(e);
                    }
                }))
                .collect(Collectors.toList());

            CompletableFuture.allOf(prepareFutures.toArray(new CompletableFuture[0])).join();

            boolean allReady = true;
            for (CompletableFuture<String> future : prepareFutures) {
                JSONObject responseMap = new JSONObject(future.get());
                String status = responseMap.optString("status");
                System.out.println("[2PC] Respuesta PREPARE: " + status);
                if (!"READY".equals(status)) {
                    allReady = false;
                    System.out.println("[2PC] Nodo NO listo: " + responseMap.optString("error"));
                    break;
                }
            }

            JSONObject finalMessage = new JSONObject().put("tx_id", txId);
            if (allReady) {
                System.out.println("[2PC] FASE 2: COMMIT");
                finalMessage.put("type", "COMMIT");
                for (NodeInfo node : involvedNodes) {
                    rabbitChannel.basicPublish(WORKER_EXCHANGE, node.queueName, null, finalMessage.toString().getBytes(StandardCharsets.UTF_8));
                }
                System.out.println("[2PC] ✓ Transferencia completada exitosamente");
                return new JSONObject().put("status", "OK").put("message", "Transferencia completada exitosamente.").toString();
            } else {
                System.out.println("[2PC] FASE 2: ABORT");
                finalMessage.put("type", "ABORT");
                for (NodeInfo node : involvedNodes) {
                    rabbitChannel.basicPublish(WORKER_EXCHANGE, node.queueName, null, finalMessage.toString().getBytes(StandardCharsets.UTF_8));
                }
                System.out.println("[2PC] ✗ Transferencia abortada");
                return new JSONObject().put("status", "ERROR").put("error", "No se pudo completar la transferencia. Uno de los nodos no estaba listo (ej. saldo insuficiente).").toString();
            }

        } catch (Exception e) {
            System.err.println("[2PC] Error fatal: " + e.getMessage());
            e.printStackTrace();
            return new JSONObject().put("status", "ERROR").put("error", "Error fatal durante la transferencia.").toString();
        }
    }

    private String handleLogin(JSONObject req) { 
        try {
            String dni = req.getString("dni");
            int accountId = req.getInt("account");

            System.out.println("[LOGIN] Validando DNI: " + dni + " para cuenta: " + accountId);

            String expectedDni = getDniForCuenta(accountId);
            if (expectedDni == null) {
                System.out.println("[LOGIN] ✗ Cuenta no encontrada: " + accountId);
                return new JSONObject().put("status", "ERROR").put("error", "Cuenta no encontrada").toString();
            }
            
            if (!expectedDni.equals(dni)) {
                System.out.println("[LOGIN] ✗ DNI no coincide. Esperado: " + expectedDni + ", Recibido: " + dni);
                return new JSONObject().put("status", "ERROR").put("error", "La cuenta no corresponde al DNI proporcionado").toString();
            }

            JSONObject validationRequest = new JSONObject().put("type", "VALIDAR_DNI").put("dni", dni);
            String reniecResponseStr = callRpc("", RENIEC_QUEUE, validationRequest.toString());
            JSONObject reniecResponse = new JSONObject(reniecResponseStr);

            if (!"OK".equals(reniecResponse.optString("status"))) {
                System.out.println("[LOGIN] ✗ RENIEC rechazó el DNI");
                return new JSONObject().put("status", "ERROR").put("error", "DNI no encontrado en RENIEC: " + reniecResponse.optString("error")).toString();
            }

            JSONObject personaData = reniecResponse.getJSONObject("data");
            String nombre = personaData.optString("nombres", "") + " " +
                           personaData.optString("apellido_paterno", "") + " " +
                           personaData.optString("apellido_materno", "");
            System.out.println("[LOGIN] ✓ Login exitoso para: " + nombre.trim());
            
            return new JSONObject()
                .put("status", "OK")
                .put("account", accountId)
                .put("nombre", nombre.trim())
                .put("dni", dni)
                .toString();

        } catch (Exception e) {
            System.err.println("[LOGIN] Error: " + e.getMessage());
            e.printStackTrace();
            return new JSONObject().put("status", "ERROR").put("error", "Error en el proceso de login: " + e.getMessage()).toString();
        }
    }
    
    private String forwardToPartition(int partition, String message) {
        try {
            if (partition < 0 || partition >= partitions) {
                System.err.println("[FORWARD] ✗ Partición inválida: " + partition);
                return new JSONObject()
                    .put("status", "ERROR")
                    .put("error", "Partición inválida: " + partition)
                    .toString();
            }
            
            List<NodeInfo> nodes = partitionsMap.get(partition);
            if (nodes == null || nodes.isEmpty()) {
                System.err.println("[FORWARD] ✗ No hay nodos para partición: " + partition);
                return new JSONObject()
                    .put("status", "ERROR")
                    .put("error", "No hay nodos disponibles para la partición " + partition)
                    .toString();
            }
            
            NodeInfo primaryNode = nodes.get(0);
            System.out.println("[FORWARD] Reenviando a partición " + partition + " -> " + primaryNode.queueName);
            
            return callRpc(WORKER_EXCHANGE, primaryNode.queueName, message);
            
        } catch (Exception e) {
            System.err.println("[FORWARD] Error: " + e.getMessage());
            e.printStackTrace();
            return new JSONObject()
                .put("status", "ERROR")
                .put("error", "Error al reenviar: " + e.getMessage())
                .toString();
        }
    }
    
    private String callRpc(String exchange, String routingKey, String message) throws IOException, InterruptedException, TimeoutException {
        final CompletableFuture<String> response = new CompletableFuture<>();
        
        String replyQueueName = rabbitChannel.queueDeclare().getQueue();
        String corrId = UUID.randomUUID().toString();
        
        AMQP.BasicProperties props = new AMQP.BasicProperties
                .Builder()
                .correlationId(corrId)
                .replyTo(replyQueueName)
                .build();
        
        if (exchange.isEmpty()) {
            rabbitChannel.basicPublish("", routingKey, props, message.getBytes(StandardCharsets.UTF_8));
            System.out.println("  [RPC->] Cola: " + routingKey);
        } else {
            rabbitChannel.basicPublish(exchange, routingKey, props, message.getBytes(StandardCharsets.UTF_8));
            System.out.println("  [RPC->] Exchange: " + exchange + ", Routing: " + routingKey);
        }
        
        String ctag = rabbitChannel.basicConsume(replyQueueName, true, (consumerTag, delivery) -> {
            if (delivery.getProperties().getCorrelationId().equals(corrId)) {
                response.complete(new String(delivery.getBody(), StandardCharsets.UTF_8));
            }
        }, consumerTag -> {});
        
        try {
            String result = response.get(10, TimeUnit.SECONDS);
            rabbitChannel.basicCancel(ctag);
            System.out.println("  [RPC<-] Respuesta recibida");
            return result;
        } catch (ExecutionException e) {
            rabbitChannel.basicCancel(ctag);
            throw new IOException("Error esperando respuesta RPC", e);
        } catch (java.util.concurrent.TimeoutException e) {
            rabbitChannel.basicCancel(ctag);
            System.err.println("  [RPC<-] ✗ TIMEOUT esperando respuesta de " + routingKey);
            throw new TimeoutException("Timeout esperando respuesta RPC de " + routingKey);
        }
    }
    
    private String handleSolicitarPrestamo(JSONObject req) { 
        try {
            int accountId = req.getInt("account");
            String dni = req.getString("dni");
            double amount = req.getDouble("monto");
            int term = req.getInt("plazo_meses");

            System.out.println("[PRESTAMO] Solicitud de préstamo: $" + amount + " para cuenta " + accountId);

            JSONObject validationRequest = new JSONObject().put("type", "VALIDAR_DNI").put("dni", dni);
            String reniecResponseStr = callRpc("", RENIEC_QUEUE, validationRequest.toString());
            JSONObject reniecResponse = new JSONObject(reniecResponseStr);

            if (!"OK".equals(reniecResponse.optString("status"))) {
                System.out.println("[PRESTAMO] ✗ Validación RENIEC falló");
                return new JSONObject().put("status", "ERROR").put("error", "Validación de identidad fallida: " + reniecResponse.optString("error")).toString();
            }

            try (Connection c = DriverManager.getConnection(DB_URL, DB_USER, DB_PASSWORD)) {
                c.setAutoCommit(false);
                
                try {
                    // 1. Registrar el préstamo
                    PreparedStatement insertPs = c.prepareStatement(
                        "INSERT INTO Prestamos (id_cuenta, dni, monto, monto_pendiente, estado, plazo_meses) " +
                        "VALUES (?, ?, ?, ?, ?, ?)",
                        PreparedStatement.RETURN_GENERATED_KEYS
                    );
                    insertPs.setInt(1, accountId);
                    insertPs.setString(2, dni);
                    insertPs.setDouble(3, amount);
                    insertPs.setDouble(4, amount);
                    insertPs.setString(5, "activo");
                    insertPs.setInt(6, term);
                    insertPs.executeUpdate();
                    
                    ResultSet generatedKeys = insertPs.getGeneratedKeys();
                    int prestamoId = 0;
                    if (generatedKeys.next()) {
                        prestamoId = generatedKeys.getInt(1);
                    }
                    
                    // 2. Desembolsar: sumar el monto al saldo de la cuenta
                    PreparedStatement updateSaldo = c.prepareStatement(
                        "UPDATE Cuentas SET saldo = saldo + ? WHERE id_cuenta = ?"
                    );
                    updateSaldo.setDouble(1, amount);
                    updateSaldo.setInt(2, accountId);
                    updateSaldo.executeUpdate();
                    
                    // 3. Registrar la transacción de desembolso
                    PreparedStatement insertTx = c.prepareStatement(
                        "INSERT INTO Transacciones (id_cuenta, tipo, monto) VALUES (?, ?, ?)"
                    );
                    insertTx.setInt(1, accountId);
                    insertTx.setString(2, "CREDITO");
                    insertTx.setDouble(3, amount);
                    insertTx.executeUpdate();
                    
                    c.commit();
                    
                    System.out.println("[PRESTAMO] ✓ Préstamo aprobado, registrado y desembolsado");
                    System.out.println("[PRESTAMO] ✓ Monto S/ " + amount + " acreditado en cuenta " + accountId);
                    
                    JSONObject data = new JSONObject();
                    data.put("id_prestamo", prestamoId);
                    data.put("monto_desembolsado", amount);
                    
                    return new JSONObject()
                        .put("status", "OK")
                        .put("message", "Préstamo aprobado y desembolsado exitosamente")
                        .put("data", data)
                        .toString();
                        
                } catch (Exception e) {
                    c.rollback();
                    throw e;
                }
            } catch (Exception e) {
                System.err.println("[PRESTAMO] Error en BD: " + e.getMessage());
                e.printStackTrace();
                return new JSONObject().put("status", "ERROR").put("error", "Error al registrar el préstamo: " + e.getMessage()).toString();
            }

        } catch (Exception e) {
            System.err.println("[PRESTAMO] Error: " + e.getMessage());
            e.printStackTrace();
            return new JSONObject().put("status", "ERROR").put("error", "Petición de préstamo inválida: " + e.getMessage()).toString();
        }
    }
    
    private String handleConsultarHistorial(JSONObject req) {
        try {
            int accountId = req.getInt("account");
            int limit = req.optInt("limit", 20);

            System.out.println("[HISTORIAL] Consultando historial para cuenta: " + accountId);

            try (Connection conn = DriverManager.getConnection(DB_URL, DB_USER, DB_PASSWORD)) {
                String query = "SELECT id_transaccion, tipo, monto, fecha " +
                              "FROM Transacciones " +
                              "WHERE id_cuenta = ? " +
                              "ORDER BY fecha DESC " +
                              "LIMIT ?";
                
                PreparedStatement ps = conn.prepareStatement(query);
                ps.setInt(1, accountId);
                ps.setInt(2, limit);
                
                ResultSet rs = ps.executeQuery();
                
                JSONArray transacciones = new JSONArray();
                while (rs.next()) {
                    JSONObject tx = new JSONObject();
                    tx.put("id", rs.getInt("id_transaccion"));
                    tx.put("tipo", rs.getString("tipo"));
                    tx.put("monto", rs.getDouble("monto"));
                    tx.put("fecha", rs.getTimestamp("fecha").toString());
                    transacciones.put(tx);
                }
                
                System.out.println("[HISTORIAL] ✓ Encontradas " + transacciones.length() + " transacciones");

                JSONObject data = new JSONObject();
                data.put("transacciones", transacciones);

                return new JSONObject()
                    .put("status", "OK")
                    .put("data", data)
                    .toString();               
                    
            } catch (Exception e) {
                System.err.println("[HISTORIAL] Error en BD: " + e.getMessage());
                e.printStackTrace();
                return new JSONObject()
                    .put("status", "ERROR")
                    .put("error", "Error al consultar historial: " + e.getMessage())
                    .toString();
            }
            
        } catch (Exception e) {
            System.err.println("[HISTORIAL] Error: " + e.getMessage());
            e.printStackTrace();
            return new JSONObject()
                .put("status", "ERROR")
                .put("error", "Petición de historial inválida: " + e.getMessage())
                .toString();
        }
    }
    
    private String getDniForCuenta(int accountId) {
        try (Connection conn = DriverManager.getConnection(DB_URL, DB_USER, DB_PASSWORD)) {
            PreparedStatement ps = conn.prepareStatement("SELECT dni FROM Cuentas WHERE id_cuenta = ?");
            ps.setInt(1, accountId);
            ResultSet rs = ps.executeQuery();
            
            if (rs.next()) {
                return rs.getString("dni");
            }
            return null;
        } catch (Exception e) {
            System.err.println("[BD] Error consultando DNI para cuenta " + accountId + ": " + e.getMessage());
            return null;
        }
    }
    
    private int getActivePartitionForAccount(int account) {
        List<Integer> activePartitions = partitionsMap.entrySet().stream()
            .filter(entry -> !entry.getValue().isEmpty())
            .map(Map.Entry::getKey)
            .sorted()
            .collect(Collectors.toList());
        
        if (activePartitions.isEmpty()) {
            System.err.println("[PARTITION] ✗ No hay particiones activas");
            return 0;
        }
        
        int partition = activePartitions.get(account % activePartitions.size());
        System.out.println("[PARTITION] Cuenta " + account + " -> Partición " + partition);
        return partition;
    }

    public static void main(String[] args) throws Exception {
        System.out.println("========================================");
        System.out.println("   SERVIDOR CENTRAL - BANCO SHIBASITO");
        System.out.println("========================================");
        
        if (args.length < 1) {
            System.out.println("Uso: java servidor_central.ServidorCentral <config.json>");
            return;
        }
        
        String cfg = args[0];
        Class.forName("org.postgresql.Driver");
        ServidorCentral sc = new ServidorCentral(cfg);
        sc.start();
        
        System.out.println("\n✓ Servidor Central operativo y esperando peticiones...\n");
    }
}
