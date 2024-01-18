import pydicom
import io
from pathlib import Path

class DicomUtils:

    def read_dicom(path):
        """
        Carga un archivo DICOM desde la ruta especificada.

        Args:
        - path (str): Ruta al archivo DICOM.

        Returns:
        - pydicom.Dataset: Objeto DICOM cargado.
        """

        ruta = Path(path)
        if ruta.exists() is False:
            raise Exception(f"'{ruta}' no existe esta ruta")
        elif ruta.is_file() is False:
            raise Exception(f"'{ruta}' no es un archivo")
        elif ruta.suffix.lower() != '.dcm':
            raise Exception('El archivo de entrada deberia ser un DICOM')

        # Carga la informacion de la imagen leida y su pixel data

        #Igual tengo que poner path pero creo que asi tambien funcionara por si peta esta esto aqui apuntado
        ds = pydicom.dcmread(ruta, force=True)

        return ds

    # Otras funciones relacionadas con DICOM pueden ir aquí
