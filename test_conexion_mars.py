import sys
import os
from ctypes import *

# 1. Configuración de DLLs nativas de iCentral
RUTA_RUNTIMES = r"C:\Program Files\iCentral\iCentral\Runtime\x64"
if os.path.exists(RUTA_RUNTIMES):
    os.add_dll_directory(RUTA_RUNTIMES)

# 2. Indexar tu carpeta local MVSDK
sys.path.append(os.path.join(os.path.dirname(__file__), "MVSDK"))

from MVSDK.IMVApi import *
from MVSDK.IMVDefines import *

def conectar_mars_industrial_perfecto():
    print("=== INICIANDO CONEXIÓN DIRECTA EN BUS USB ===")
    
    # 1. Enumerar dispositivos en los puertos de la laptop
    deviceList = IMV_DeviceList()
    print("[1/4] Escaneando puertos USB...")
    nRet = MvCamera.IMV_EnumDevices(deviceList, IMV_EInterfaceType.interfaceTypeAll)
    
    if nRet != 0: 
        print(f" [ERROR]: El SDK rechazó el escaneo USB. Código: {nRet}")
        return

    if deviceList.nDevNum == 0:
        print("\n [ERROR]: No se detectó ninguna cámara Mars.")
        print(" Asegúrate de que el software oficial iCentral esté cerrado.")
        return

    # Extraemos las credenciales reales de la Mars5000S conectada
    devInfo = deviceList.pDevInfo[0]
    nombre_camara = devInfo.modelName.decode('utf-8')
    serial_camara = devInfo.serialNumber.decode('utf-8')
    print(f" -> ¡SISTEMA ENCONTRADO!: {nombre_camara} (S/N: {serial_camara})")

    # Instanciamos el objeto cámara
    cam = MvCamera()
    
    # 2. Crear el Handle por índice (0 para la primera cámara de la lista)
    # Este paso mapea internamente la Mars5000S al objeto de Python
    print("[2/4] Creando handle de comunicación para el índice 0...")
    nRet = cam.IMV_CreateHandle(IMV_ECreateHandleMode.modeByIndex, byref(c_void_p(0)))
    if nRet != 0:
        print(f" [ERROR]: No se pudo crear el handle. Código: {nRet}")
        return

    # 3. Abrir la cámara físicamente
    print("[3/4] Abriendo canal de datos USB directo...")
    nRet = cam.IMV_Open()
    
    if nRet == 0:
        print("\n=======================================================")
        print(" ¡CONEXIÓN EXITOSA! Tu Python controla la Mars5000S")
        print("=======================================================\n")
        
        # Validación de estado online
        if cam.IMV_IsOpen():
            print(" -> Estado del enlace: [ONLINE Y CONTROLADO]")
        
        # 4. Desconexión limpia y segura siguiendo el protocolo oficial
        print("\n[4/4] Cerrando y destruyendo descriptores seguros...")
        cam.IMV_Close()
        if cam.handle:
            cam.IMV_DestroyHandle()
        print("=== DIAGNÓSTICO FINALIZADO CON ÉXITO ===")
        print("El canal USB quedó libre y listo para producción.")
    else:
        print(f" [ERROR]: No se pudo abrir la cámara. Código de error del SDK: {nRet}")

if __name__ == "__main__":
    conectar_mars_industrial_perfecto()