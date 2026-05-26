import struct
from pyModbusTCP.client import ModbusClient

# ─────────────────────────────────────────────
IP_ROBOT = "192.168.2.17"
# ─────────────────────────────────────────────

def escribir_float_gv(client, gv_number, valor_float):
    """Escribe un float de 32 bits en una variable global del robot."""
    raw_bytes = struct.pack('<f', float(valor_float))
    palabra_low  = struct.unpack('<H', raw_bytes[0:2])[0]
    palabra_high = struct.unpack('<H', raw_bytes[2:4])[0]
    registro_base = 2 * gv_number
    exito = client.write_multiple_registers(registro_base, [palabra_low, palabra_high])
    print(f"GV{gv_number} = {valor_float} → {'OK' if exito else 'FALLO'}")
    return exito

# ─── CONECTAR ───────────────────────────────
client = ModbusClient(host=IP_ROBOT, port=502, unit_id=1, auto_open=True)

if not client.open():
    print("No se pudo conectar")
    exit()

print("✓ Conectado\n")

# ─── ESCRIBIR COORDENADAS EN GV1, GV2, GV3 ──
# Estos son los offsets que tu programa POSE_OFFSET lee
# Cámbialos por los valores que necesites

escribir_float_gv(client, 0, 10.0)   # GV0 = offset X en mm
escribir_float_gv(client, 1, 10.0)   # GV1 = offset X en mm
escribir_float_gv(client, 2, 0.0)    # GV2 = offset Y en mm
escribir_float_gv(client, 3, 0.0)    # GV3 = offset Z en mm

print("\nCoordendas enviadas. El robot debería moverse si el programa está corriendo.")

client.close()