from modelo.dicom_data import DicomData
from utils.dicom_utils import DicomUtils
from utils.image_converter import ImageConverter
from excepciones.excepciones import *

class Modelo():

    def __init__(self):
        self.lista_dicom = []
        self._dicom_data = None
        self.dicom_utils = DicomUtils()
        self.image_converter = ImageConverter()

    @property
    def dicom_data(self):
        # Lazy initialization: crea el objeto DicomData solo si es necesario
        if self._dicom_data is None:
            raise ValueError("No se ha proporcionado ningún dicom para inicializar DicomData")
        return self._dicom_data

    @dicom_data.setter
    def dicom_data(self, ds):
        # Establecer el dicom_data directamente (sin inicialización diferida)
        self._dicom_data = DicomData(ds)

    def crear_y_agreagar_a_la_lista_dicom_data(self, ruta):
        ds = self.dicom_utils.read_dicom(ruta)
        self.dicom_data = ds
        self.lista_dicom.append(self.dicom_data)

    def crear_y_agreagar_a_la_lista_multiples_dicom_data_(self, ruta):
        ds_multiple = self.dicom_utils.read_multiple_dicom(ruta)
        for element in ds_multiple:
            self.dicom_data = element
            self.lista_dicom.append(self.dicom_data)

    def devolver_ultimo_dicom_data_de_la_lista(self):
        if len(self.lista_dicom) == 0:
            raise ListaVaciaError()

        return self.lista_dicom[-1]

    def devolver_dicom_data_en_posicion_de_la_lista(self, posicion):
        if len(self.lista_dicom) == 0:
            raise ListaVaciaError()
        elif posicion < 0 or posicion > len(self.lista_dicom):
            raise PosicionInvalidaError(posicion)

        return self.lista_dicom[posicion]

    def devolver_todos_los_dicom_data_de_la_lista(self):
        if len(self.lista_dicom) == 0:
            raise ListaVaciaError()

        return self.lista_dicom

    def transformar_ultimo_dicom_data_de_la_lista(self):
        if len(self.lista_dicom) == 0:
            raise ListaVaciaError()

        data = self.lista_dicom[-1]
        self.lista_dicom[-1] = self.image_converter.dicom_converter_to_tiff(data)

    def transformar_dicom_data_en_posicion_de_la_lista(self, posicion):
        if len(self.lista_dicom) == 0:
            raise ListaVaciaError()
        elif posicion < 0 or posicion > len(self.lista_dicom):
            raise PosicionInvalidaError(posicion)

        data = self.lista_dicom[posicion]
        self.lista_dicom[posicion] = self.image_converter.dicom_converter_to_tiff(data)

    def transformar_todos_los_dicom_data_de_la_lista(self):
        if len(self.lista_dicom) == 0:
            raise ListaVaciaError()

        for i, element in enumerate(self.lista_dicom):
            if ((self.lista_dicom[i].get_pixel_data_modified()).sum() == 0):
                self.lista_dicom[i] = self.image_converter.dicom_converter_to_tiff(element)

    def borrar_ultimo_dicom_data_de_la_lista(self):
        if len(self.lista_dicom) == 0:
            raise ListaVaciaError()

        del self.lista_dicom[-1]

    def borrar_dicom_data_en_posicion_de_la_lista(self, posicion):
        if len(self.lista_dicom) == 0:
            raise ListaVaciaError()
        elif posicion < 0 or posicion > len(self.lista_dicom):
            raise PosicionInvalidaError(posicion)

        del self.lista_dicom[posicion]

    def borrar_todos_los_dicom_data_de_la_lista(self):
        if len(self.lista_dicom) == 0:
            raise ListaVaciaError()

        self.lista_dicom.clear()