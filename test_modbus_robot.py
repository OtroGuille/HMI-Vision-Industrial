import struct
from pyModbusTCP.client import ModbusClient

def escribir_float_szgh(client, gv_number, valor_float):
    """
    Divide un float de 32 bits en dos registros de 16 bits (Low primero, High después)
    siguiendo la regla estricta del manual SZGH Betrun.
    """
    # 1. Convertir el float a bytes en formato IEEE 754 (Little Endian)
    # El manual dice: "low 16 bits first, high 16 bits last"
    raw_bytes = struct.pack('<f', float(valor_float))
    
    # 2. Desempaquetar en dos palabras de 16 bits (unsigned short)
    palabra_low = struct.unpack('<H', raw_bytes[0:2])[0]
    palabra_high = struct.unpack('<H', raw_bytes[2:4])[0]
    
    # 3. Calcular la dirección Modbus inicial (Registro base = 2 * Número de GV)
    registro_base = 2 * gv_number
    
    print(f"Escribiendo {valor_float} en GV{gv_number}:")
    print(f" -> Registro {registro_base} (Low): {palabra_low}")
    print(f" -> Registro {registro_base + 1} (High): {palabra_high}")
    
    # Escribimos de golpe ambos registros usando la función de múltiples registros (FC16)
    exito = client.write_multiple_registers(registro_base, [palabra_low, palabra_high])
    return exito

# --- EJECUCIÓN DE LA PRUEBA DEFINITIVA ---
IP_ROBOT = "192.168.2.17"
client = ModbusClient(host=IP_ROBOT, port=502, unit_id=1, auto_open=True)

if client.open():
    print("¡Conectado al canal Modbus!")
    
    # Vamos a enviar el valor 5.5 a la variable GV5 (Registros Modbus 10 y 11)
    # Si quieres usar otra variable, por ejemplo GV10, usaría los registros 20 y 21.
    numero_gv = 1
    valor_a_enviar = 700
    
    if escribir_float_szgh(client, numero_gv, valor_a_enviar):
        print("\n[ÉXITO]: ¡Estructura de memoria aceptada por el robot!")
        print(f"Ve al Teach Pendant, entra a 'Menu' -> 'Global Variables'.")
        print(f"Busca la fila GV{numero_gv} (si no cambia, sal del menú y vuelve a entrar para refrescar).")
        print(f"¡Ahí verás impreso el {valor_a_enviar}!")
    else:
        print("[ERROR]: El robot rechazó la escritura múltiple.")
        
    client.close()
else:
    print("No se pudo abrir la conexión.")