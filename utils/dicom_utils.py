import os
import pydicom
import io
from pathlib import Path
import subprocess
import matplotlib.pyplot as plt
import glob
import imageio
import numpy as np
from utils.indexTracker import IndexTracker
from excepciones.excepciones import *

class DicomUtils:

    def read_dicom(self, path):
        """
        Carga un archivo DICOM desde la ruta especificada.

        Args:
        - path (str): Ruta al archivo DICOM.

        Returns:
        - pydicom.Dataset: Objeto DICOM cargado.
        """

        ruta = Path(path)
        if not ruta.exists():
            raise ArchivoNoEncontradoError(ruta)
        elif not ruta.is_file():
            raise NoEsArchivoError(ruta)
        elif ruta.suffix.lower() != '.dcm':
            raise ExtensionIncorrectaError(ruta.suffix.lower())

        # Carga la informacion de la imagen leida y su pixel data
        ds = pydicom.dcmread(ruta, force=True)

        return ds

    def read_multiple_dicom(self, path):
        """
        Carga un archivo DICOM desde la ruta especificada.

        Args:
        - path (str): Ruta al archivo DICOM.

        Returns:
        - pydicom.Dataset: Objeto DICOM cargado.
        """

        directorio, patron = os.path.split(path)
        print(directorio)
        directorio = Path(directorio)
        dcm_files = glob.glob(os.path.join(directorio, '*.dcm'))

        if not directorio.exists():
            raise DirectorioNoExisteError(directorio)
        elif not dcm_files:
            raise ArchivosDCMNoEncontradosError(directorio)

        #self.print_directory()
        plots = []
        for f in glob.glob(path):
            print(f.split("/")[-1])
            filename = f.split("/")[-1]
            ds = pydicom.dcmread(f)
            plots.append(ds)

        return plots

    #-------------------------------------------------------------------------------------------------------------------

    #Funcion que no se usa pero por lo que pueda ser, dejo aqui
    def print_directory(self):
        # Especifica el directorio que deseas listar
        directorio = "/home/rainor/PycharmProjects/tfg/ImagenesDICOM/"
        # Construye el comando
        comando = f"ls -l {directorio}"
        # Ejecuta el comando y captura la salida
        resultado = subprocess.run(comando, shell=True, check=True, stdout=subprocess.PIPE, text=True)
        # Imprime la salida del comando
        print(resultado.stdout)