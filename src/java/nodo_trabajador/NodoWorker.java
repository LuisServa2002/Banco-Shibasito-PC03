package nodo_trabajador;

import com.rabbitmq.client.*;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import org.json.JSONObject;

public class NodoWorker {
    private final int workerId;
    private final String queueName;
    private final Map<String, List<String>> preparedOps = new ConcurrentHashMap<>();

    private com.rabbitmq.client.Connection rabbitConnection;
    private Channel rabbitChannel;
    private static final String WORKER_EXCHANGE = "worker_exchange";

    // Configuración de la conexión a PostgreSQL
    private static final String DB_URL = "jdbc:postgresql://localhost:5432/bd1_banco";
    private static final String DB_USER = "postgres";
    private static final String DB_PASSWORD = "mysecretpassword";

    public NodoWorker(int workerId) throws IOException {
        this.workerId = workerId;
        this.queueName = "worker_queue_" + workerId;
        initRabbitMQ();
    }

    private Connection getDbConnection() throws SQLException {
        return DriverManager.getConnection(DB_URL, DB_USER, DB_PASSWORD);
    }

    private void initRabbitMQ() {
        try {
            ConnectionFactory factory = new ConnectionFactory();
            factory.setHost("localhost");
            this.rabbitConnection = factory.newConnection();
            this.rabbitChannel = rabbitConnection.createChannel();

            rabbitChannel.exchangeDeclare(WORKER_EXCHANGE, BuiltinExchangeType.DIRECT);
            rabbitChannel.queueDeclare(queueName, true, false, false, null);
            rabbitChannel.queueBind(queueName, WORKER_EXCHANGE, queueName);

            System.out.println("NodoWorker " + workerId + " escuchando en la cola " + queueName);
        } catch (Exception e) {
            throw new RuntimeException("Cannot initialize RabbitMQ", e);
        }
    }

    public void start() throws IOException {
        ExecutorService pool = Executors.newCachedThreadPool();
        DeliverCallback deliverCallback = (consumerTag, delivery) -> {
            pool.submit(() -> {
                AMQP.BasicProperties properties = delivery.getProperties();
                final String corrId = properties.getCorrelationId();
                final String replyTo = properties.getReplyTo();
                String message = new String(delivery.getBody(), StandardCharsets.UTF_8);

                System.out.println("[DEBUG NodoWorker " + workerId + "] Mensaje recibido: " + message);
                String response = handleRequest(message);

                if (replyTo != null && !response.isEmpty()) {
                    try {
                        AMQP.BasicProperties replyProps = new AMQP.BasicProperties.Builder().correlationId(corrId).build();
                        rabbitChannel.basicPublish("", replyTo, replyProps, response.getBytes(StandardCharsets.UTF_8));
                        System.out.println("[DEBUG NodoWorker " + workerId + "] Respuesta enviada: " + response);
                    } catch (IOException e) {
                        e.printStackTrace();
                    }
                }
            });
        };
        rabbitChannel.basicConsume(queueName, true, deliverCallback, consumerTag -> {});
    }

    private String handleRequest(String message) {
        JSONObject req = new JSONObject(message);
        String type = req.getString("type").toUpperCase();
        String response = "";

        try {
            switch (type) {
                case "CONSULTAR_CUENTA":
                    response = handleConsulta(req);
                    break;
                case "SUM_PARTITION":
                    response = handleSumPartition();
                    break;
                case "PREPARE_TRANSFER":
                    response = handlePrepareMsg(req);
                    break;
                case "COMMIT":
                    handleCommitMsg(req);
                    break;
                case "ABORT":
                    handleAbortMsg(req);
                    break;
                default:
                    response = new JSONObject().put("status", "ERROR").put("error", "TIPO_DESCONOCIDO").toString();
                    break;
            }
        } catch (Exception inner) {
            inner.printStackTrace();
            response = new JSONObject().put("status", "ERROR").put("error", "EXCEPCION_EN_OPERACION").toString();
        }
        return response;
    }

    private String handleConsulta(JSONObject req) {
        int accId = req.getInt("account");
        try (Connection conn = getDbConnection();
             PreparedStatement ps = conn.prepareStatement("SELECT saldo FROM Cuentas WHERE id_cuenta = ?")) {
            ps.setInt(1, accId);
            ResultSet rs = ps.executeQuery();
            if (rs.next()) {
                double balance = rs.getDouble("saldo");
                return new JSONObject().put("status", "OK").put("account", accId).put("balance", String.format("%.2f", balance)).toString();
            } else {
                return new JSONObject().put("status", "ERROR").put("error", "NO_EXISTE_CUENTA").toString();
            }
        } catch (SQLException e) {
            e.printStackTrace();
            return new JSONObject().put("status", "ERROR").put("error", "DB_ERROR").toString();
        }
    }

    private String handleSumPartition() {
        try (Connection conn = getDbConnection();
             PreparedStatement ps = conn.prepareStatement("SELECT SUM(saldo) AS total FROM Cuentas");
             ResultSet rs = ps.executeQuery()) {
            if (rs.next()) {
                double total = rs.getDouble("total");
                return new JSONObject().put("status", "OK").put("sum", String.format("%.2f", total)).toString();
            }
        } catch (SQLException e) {
            e.printStackTrace();
        }
        return new JSONObject().put("status", "ERROR").put("error", "DB_ERROR").toString();
    }

    private String handlePrepareMsg(JSONObject req) {
        String txId = req.getString("tx_id");
        boolean ok = handlePrepare(req, txId);
        return ok ? new JSONObject().put("status", "READY").put("tx_id", txId).toString()
                  : new JSONObject().put("status", "ERROR").put("tx_id", txId).put("error", "PREPARE_FAIL").toString();
    }

    private boolean handlePrepare(JSONObject req, String txId) {
        List<String> opsForTx = new ArrayList<>();
        String type = req.getString("type").toLowerCase();

        try (Connection conn = getDbConnection()) {
            if (type.contains("transfer")) {
                int fromId = req.getInt("from");
                int toId = req.getInt("to");
                double amount = req.getDouble("amount");

                try (PreparedStatement ps = conn.prepareStatement("SELECT saldo FROM Cuentas WHERE id_cuenta = ?")) {
                    ps.setInt(1, fromId);
                    ResultSet rs = ps.executeQuery();
                    if (rs.next()) {
                        if (rs.getDouble("saldo") < amount) {
                            return false; // Saldo insuficiente
                        }
                        opsForTx.add("debit," + fromId + "," + amount);
                    }
                }

                try (PreparedStatement ps = conn.prepareStatement("SELECT 1 FROM Cuentas WHERE id_cuenta = ?")) {
                    ps.setInt(1, toId);
                    if (ps.executeQuery().next()) {
                        opsForTx.add("credit," + toId + "," + amount);
                    }
                }
            }
            preparedOps.put(txId, opsForTx);
            return true;
        } catch (SQLException e) {
            e.printStackTrace();
            return false;
        }
    }

    private void handleCommitMsg(JSONObject req) {
        String txId = req.getString("tx_id");
        List<String> ops = preparedOps.remove(txId);
        if (ops == null) return;

        try (Connection conn = getDbConnection()) {
            conn.setAutoCommit(false);
            try {
                for (String op : ops) {
                    String[] p = op.split(",");
                    String cmd = p[0];
                    int accId = Integer.parseInt(p[1]);
                    double amount = Double.parseDouble(p[2]);

                    if ("debit".equals(cmd)) {
                        updateBalance(conn, accId, -amount);
                        insertTransaction(conn, accId, "DEBITO", -amount);
                    } else if ("credit".equals(cmd)) {
                        updateBalance(conn, accId, amount);
                        insertTransaction(conn, accId, "CREDITO", amount);
                    }
                }
                conn.commit();
            } catch (SQLException e) {
                conn.rollback();
                e.printStackTrace();
            }
        } catch (SQLException e) {
            e.printStackTrace();
        }
    }

    private void updateBalance(Connection conn, int accId, double amount) throws SQLException {
        try (PreparedStatement ps = conn.prepareStatement("UPDATE Cuentas SET saldo = saldo + ? WHERE id_cuenta = ?")) {
            ps.setDouble(1, amount);
            ps.setInt(2, accId);
            ps.executeUpdate();
        }
    }

    private void insertTransaction(Connection conn, int accId, String type, double amount) throws SQLException {
        try (PreparedStatement ps = conn.prepareStatement("INSERT INTO Transacciones (id_cuenta, tipo, monto) VALUES (?, ?, ?)")) {
            ps.setInt(1, accId);
            ps.setString(2, type);
            ps.setDouble(3, amount);
            ps.executeUpdate();
        }
    }

    private void handleAbortMsg(JSONObject req) {
        String txId = req.getString("tx_id");
        preparedOps.remove(txId);
    }

    public static void main(String[] args) throws Exception {
        if (args.length < 1) {
            System.out.println("Uso: java nodo_trabajador.NodoWorker <worker-id>");
            return;
        }
        int workerId = Integer.parseInt(args[0]);
        Class.forName("org.postgresql.Driver");
        NodoWorker n = new NodoWorker(workerId);
        n.start();
    }
}
