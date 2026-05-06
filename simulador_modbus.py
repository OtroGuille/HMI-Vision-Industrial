from pymodbus.server.sync import StartTcpServer
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext
import threading
import time

# Función que lee los registros y los imprime
def monitor_plc(context):
    print("Iniciando monitoreo de registros...")
    while True:
        # Leemos los registros 0 al 4 (X, Y, Angulo, Color, Tipo)
        #count=5 porque queremos leer 5 registros (0, 1, 2, 3 y 4)
        # slave=0 es el primer esclavo
        valores = context[0].getValues(3, 0, count=5)
        
        # Solo imprimimos si hay algo diferente de cero para no saturar la consola
        print(f"LECTURA PLC: {valores}")
        
        time.sleep(1) # Revisa cada segundo

# --- Configuración igual a la anterior ---
store = ModbusSlaveContext(hr=ModbusSequentialDataBlock(0, [0]*10))
context = ModbusServerContext(slaves=store, single=True)

# Iniciamos el hilo de monitoreo ANTES de arrancar el servidor
hilo_monitor = threading.Thread(target=monitor_plc, args=(context,), daemon=True)
hilo_monitor.start()

print("Simulador PLC (v2.5.3) listo en 127.0.0.1:502...")
StartTcpServer(context=context, address=("127.0.0.1", 502))