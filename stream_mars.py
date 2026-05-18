import sys
import os
from ctypes import *
import cv2
import numpy as np

# 1. Configuración de DLLs nativas de iCentral
RUTA_RUNTIMES = r"C:\Program Files\iCentral\iCentral\Runtime\x64"
if os.path.exists(RUTA_RUNTIMES):
    os.add_dll_directory(RUTA_RUNTIMES)

# 2. Indexar tu carpeta local MVSDK
sys.path.append(os.path.join(os.path.dirname(__file__), "MVSDK"))

from MVSDK.IMVApi import *
from MVSDK.IMVDefines import *

def video_en_vivo_mars():
    print("=== CONTROL DE VIDEO EN VIVO - MARS5000S ===")
    
    # [Paso 1] Enumerar y validar hardware
    deviceList = IMV_DeviceList()
    nRet = MvCamera.IMV_EnumDevices(deviceList, IMV_EInterfaceType.interfaceTypeAll)
    if nRet != 0 or deviceList.nDevNum == 0:
        print(" [ERROR]: No se encontró la cámara Mars.")
        return

    # [Paso 2] Inicializar y abrir el Handle
    cam = MvCamera()
    nRet = cam.IMV_CreateHandle(IMV_ECreateHandleMode.modeByIndex, byref(c_void_p(0)))
    if nRet != 0:
        print(f" [ERROR]: No se pudo crear el handle. Código: {nRet}")
        return

    nRet = cam.IMV_Open()
    if nRet != 0:
        print(f" [ERROR]: No se pudo abrir la cámara. Código: {nRet}")
        return
    
    print(" -> Conexión establecida de forma segura.")

    try:
        # [Paso 3] Configurar Modo Continuo (Trigger en OFF)
        cam.IMV_SetEnumFeatureSymbol("TriggerMode", "Off")
        
        # [Paso 4] Iniciar el streaming (Grabbing)
        nRet = cam.IMV_StartGrabbing()
        if nRet != 0:
            print(f" [ERROR]: No se pudo iniciar el streaming. Código: {nRet}")
            return
        
        print("\n=======================================================")
        print(" -> TRANSMITIENDO EN VIVO... Presiona 'q' para salir.")
        print("=======================================================\n")
        
        frame = IMV_Frame()
        stPixelConvertParam = IMV_PixelConvertParam()

        while True:
            # Capturar un frame de la cámara (timeout de 500ms)
            nRet = cam.IMV_GetFrame(frame, 500)
            if nRet != 0:
                # Si hay un pequeño delay o timeout, saltamos al siguiente ciclo sin romper el bucle
                continue

            # Reservar memoria para la conversión a BGR8 (3 canales: Azul, Verde, Rojo)
            ancho = frame.frameInfo.width
            alto = frame.frameInfo.height
            nConvertBufSize = ancho * alto * 3
            pConvertBuf = (c_ubyte * nConvertBufSize)()

            # Configurar los parámetros de conversión nativa del SDK
            memset(byref(stPixelConvertParam), 0, sizeof(stPixelConvertParam))
            stPixelConvertParam.nWidth = ancho
            stPixelConvertParam.nHeight = alto
            stPixelConvertParam.ePixelFormat = frame.frameInfo.pixelFormat
            stPixelConvertParam.pSrcData = frame.pData
            stPixelConvertParam.nSrcDataLen = frame.frameInfo.size
            stPixelConvertParam.nPaddingX = frame.frameInfo.paddingX
            stPixelConvertParam.nPaddingY = frame.frameInfo.paddingY
            stPixelConvertParam.eBayerDemosaic = IMV_EBayerDemosaic.demosaicNearestNeighbor
            stPixelConvertParam.eDstPixelFormat = IMV_EPixelType.gvspPixelBGR8  # Formato OpenCV
            stPixelConvertParam.pDstBuf = pConvertBuf
            stPixelConvertParam.nDstBufSize = nConvertBufSize

            # Ejecutar la conversión de formato en la DLL
            if cam.IMV_PixelConvert(stPixelConvertParam) == 0:
                # Convertir el buffer de c_ubytes a una matriz NumPy que OpenCV entiende
                img_buff = np.frombuffer(pConvertBuf, dtype=np.uint8)
                img_opencv = img_buff.reshape((alto, ancho, 3))

                # Mostrar el frame en una ventana interactiva de OpenCV
                # Puedes ajustar el tamaño si la resolución de la Mars5000S es muy alta para tu pantalla
                img_redimensionada = cv2.resize(img_opencv, (800, 600)) 
                cv2.imshow("Stream en Vivo - Mars5000S", img_redimensionada)
            
            # Liberar OBLIGATORIAMENTE el frame actual para que la cámara reciba el siguiente
            cam.IMV_ReleaseFrame(frame)

            # Romper el bucle si el usuario presiona la tecla 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except Exception as e:
        print(f"\n [ERROR durante la transmisión]: {e}")

    finally:
        # [Paso 5] Apagado seguro y liberación de descriptores
        print("\n=== CERRANDO TRANSMISIÓN ===")
        cv2.destroyAllWindows()
        cam.IMV_StopGrabbing()
        cam.IMV_Close()
        if cam.handle:
            cam.IMV_DestroyHandle()
        print("Canal USB liberado y limpio.")

if __name__ == "__main__":
    video_en_vivo_mars()