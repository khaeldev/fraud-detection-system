# Datos de Clientes (Customer Behavior)
CUSTOMERS = {
    "CU-001": {"usual_amount_avg": 500.00, "usual_hours": [8, 20], "usual_countries": ["PE"], "usual_devices": ["D-01"]},
    "CU-002": {"usual_amount_avg": 1200.00, "usual_hours": [9, 22], "usual_countries": ["PE"], "usual_devices": ["D-02"]}
}

# Políticas de Fraude para RAG
FRAUD_POLICIES = [
    {"policy_id": "FP-01", "rule": "Monto > 3x promedio habitual y horario fuera de rango → CHALLENGE", "version": "2025.1", "text": "Si el monto de la transacción supera 3 veces el promedio histórico del cliente y se realiza fuera de su horario habitual, se debe emitir un CHALLENGE."},
    {"policy_id": "FP-02", "rule": "Transacción internacional y dispositivo nuevo → ESCALATE_TO_HUMAN", "version": "2025.1", "text": "Cualquier transacción realizada desde un país diferente al habitual y usando un dispositivo no registrado previamente debe ser escalada inmediatamente a revisión humana (ESCALATE_TO_HUMAN)."},
    {"policy_id": "FP-03", "rule": "Comportamiento normal → APPROVE", "version": "2025.1", "text": "Si la transacción coincide con los patrones de monto, horario y dispositivo, debe ser aprobada (APPROVE)."},
    {"policy_id": "FP-04", "rule": "Reporte de amenaza externa confirmada → BLOCK", "version": "2025.1", "text": "Si existe inteligencia externa confirmando fraude reciente en el comercio, bloquear inmediatamente (BLOCK)."}
]

# Transacciones de ejemplo (para pruebas)
TRANSACTIONS = [
    {"transaction_id": "T-1001", "customer_id": "CU-001", "amount": 1800.00, "currency": "PEN", "country": "PE", "channel": "web", "device_id": "D-01", "timestamp": "2025-12-17T03:15:00", "merchant_id": "M-001"},
    {"transaction_id": "T-1002", "customer_id": "CU-002", "amount": 9500.00, "currency": "PEN", "country": "PE", "channel": "mobile", "device_id": "D-02", "timestamp": "2025-12-17T23:45:00", "merchant_id": "M-002"},
    {"transaction_id": "T-LEGIT-001", "customer_id": "CU-001", "amount": 300.50, "currency": "PEN", "country": "PE", "channel": "web", "device_id": "D-01", "timestamp": "2025-12-18T10:15:00", "merchant_id": "M-SAFE"},
    {"transaction_id": "T-FRAUD-999", "customer_id": "CU-001", "amount": 500000.00, "currency": "PEN", "country": "RU", "channel": "web", "device_id": "D-HACKER", "timestamp": "2025-12-18T03:00:00", "merchant_id": "M-DANGER"},
    {"transaction_id": "T-HUMAN-999", "customer_id": "CU-001", "amount": 800.00, "currency": "USD", "country": "COL", "channel": "web", "device_id": "D-05", "timestamp": "2025-12-08T09:00:00", "merchant_id": "M-001"}
]

def get_customer_profile(customer_id):
    return CUSTOMERS.get(customer_id, {})