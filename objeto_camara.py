import sys
import os
from ctypes import *
import cv2
import numpy as np

# Configuración de DLLs nativas de iCentral (necesario para cargar MVSDKmd.dll)
RUTA_RUNTIMES = r"C:\Program Files\iCentral\iCentral\Runtime\x64"
if os.path.exists(RUTA_RUNTIMES):
    os.add_dll_directory(RUTA_RUNTIMES)

# Indexar tu carpeta local MVSDK para las importaciones fijas
sys.path.append(os.path.join(os.path.dirname(__file__), "MVSDK"))
from MVSDK.IMVApi import *
from MVSDK.IMVDefines import *

class CamaraMarsIndustrial:
    def __init__(self):
        self.cam = None
        self.frame = None
        self.stPixelConvertParam = None
        self.inicializada = False

    def inicializar(self):
        """Escanea el bus USB, crea el handle y abre la cámara en modo continuo."""
        print("[Mars SDK] Buscando cámara en puertos USB...")
        deviceList = IMV_DeviceList()
        nRet = MvCamera.IMV_EnumDevices(deviceList, IMV_EInterfaceType.interfaceTypeAll)
        
        if nRet != 0 or deviceList.nDevNum == 0:
            print("[Mars SDK] ERROR: No se detectó la cámara Mars5000S.")
            return False

        # Configuración del objeto de cámara e inicialización de descriptores
        self.cam = MvCamera()
        nRet = self.cam.IMV_CreateHandle(IMV_ECreateHandleMode.modeByIndex, byref(c_void_p(0)))
        if nRet != 0:
            print(f"[Mars SDK] ERROR al crear el handle. Código: {nRet}")
            return False

        nRet = self.cam.IMV_Open()
        if nRet != 0:
            print(f"[Mars SDK] ERROR al abrir la cámara. Código: {nRet}")
            return False

        # Configurar modo de ráfaga libre continuo (Trigger Off)
        self.cam.IMV_SetEnumFeatureSymbol("TriggerMode", "Off")
        
        nRet = self.cam.IMV_StartGrabbing()
        if nRet != 0:
            print(f"[Mars SDK] ERROR al iniciar adquisición. Código: {nRet}")
            return False

        # Preparar estructuras de memoria fijas para el bucle
        self.frame = IMV_Frame()
        self.stPixelConvertParam = IMV_PixelConvertParam()
        self.inicializada = True
        print("[Mars SDK] ¡Cámara Mars lista y transmitiendo!")
        return True

    def obtener_frame(self):
        """Captura el frame crudo, lo transforma a matriz NumPy BGR y libera el buffer de la cámara."""
        if not self.inicializada:
            return False, None

        # Captura el cuadro de la memoria (timeout de 500ms)
        nRet = self.cam.IMV_GetFrame(self.frame, 500)
        if nRet != 0:
            return False, None

        ancho = self.frame.frameInfo.width
        alto = self.frame.frameInfo.height
        nConvertBufSize = ancho * alto * 3
        pConvertBuf = (c_ubyte * nConvertBufSize)()

        # Configuración del mapeo de memoria nativo a BGR8
        memset(byref(self.stPixelConvertParam), 0, sizeof(self.stPixelConvertParam))
        self.stPixelConvertParam.nWidth = ancho
        self.stPixelConvertParam.nHeight = alto
        self.stPixelConvertParam.ePixelFormat = self.frame.frameInfo.pixelFormat
        self.stPixelConvertParam.pSrcData = self.frame.pData
        self.stPixelConvertParam.nSrcDataLen = self.frame.frameInfo.size
        self.stPixelConvertParam.nPaddingX = self.frame.frameInfo.paddingX
        self.stPixelConvertParam.nPaddingY = self.frame.frameInfo.paddingY
        self.stPixelConvertParam.eBayerDemosaic = IMV_EBayerDemosaic.demosaicNearestNeighbor
        self.stPixelConvertParam.eDstPixelFormat = IMV_EPixelType.gvspPixelBGR8
        self.stPixelConvertParam.pDstBuf = pConvertBuf
        self.stPixelConvertParam.nDstBufSize = nConvertBufSize

        imagen_bgr = None
        if self.cam.IMV_PixelConvert(self.stPixelConvertParam) == 0:
            # Transformación ultra rápida a matriz NumPy para OpenCV / YOLO
            img_buff = np.frombuffer(pConvertBuf, dtype=np.uint8)
            imagen_bgr = img_buff.reshape((alto, ancho, 3))

        # Liberar el buffer obligatoriamente para no congelar el flujo de hardware
        self.cam.IMV_ReleaseFrame(self.frame)
        
        if imagen_bgr is not None:
            return True, imagen_bgr
        return False, None

    def liberar(self):
        """Apaga el streaming y destruye los handles de Windows limpiamente."""
        if self.cam:
            print("[Mars SDK] Liberando recursos de la cámara de forma segura...")
            self.cam.IMV_StopGrabbing()
            self.cam.IMV_Close()
            if self.cam.handle:
                self.cam.IMV_DestroyHandle()
            self.inicializada = False
            print("[Mars SDK] Hardware desconectado y bus USB limpio.")