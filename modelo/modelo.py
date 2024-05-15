import os

import imageio

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

        dir_actual = os.path.dirname(__file__)
        dir_padre_actual = os.path.dirname(dir_actual)
        self.dir_salida = os.path.join(dir_padre_actual, "salida")

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

#----------------------------------------- Metodos para crear el dicom_data -------------------------------------------#

    def crear_y_agregar_a_la_lista_dicom_data(self, ruta):
        ds = self.dicom_utils.read_dicom(ruta)
        self.dicom_data = ds
        self.lista_dicom.append(self.dicom_data)

    def crear_y_agregar_a_la_lista_multiples_dicom_data_(self, ruta):
        ds_multiple = self.dicom_utils.read_multiple_dicom(ruta)
        for element in ds_multiple:
            self.dicom_data = element
            self.lista_dicom.append(self.dicom_data)

#----------------------------------- Metodos para devolver dicom_data de la lista -------------------------------------#

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

#---------------------------------- Metodos para transformar dicom en tiff 8 bits -------------------------------------#

    def transformar_ultimo_dicom_data_de_la_lista_tiff_8_bits(self):
        if len(self.lista_dicom) == 0:
            raise ListaVaciaError()

        data = self.lista_dicom[-1]
        self.lista_dicom[-1] = self.image_converter.dicom_converter_to_tiff_8_bits(data)

    def transformar_dicom_data_en_posicion_de_la_lista_tiff_8_bits(self, posicion):
        if len(self.lista_dicom) == 0:
            raise ListaVaciaError()
        elif posicion < 0 or posicion > len(self.lista_dicom):
            raise PosicionInvalidaError(posicion)

        data = self.lista_dicom[posicion]
        self.lista_dicom[posicion] = self.image_converter.dicom_converter_to_tiff_8_bits(data)

    def transformar_todos_los_dicom_data_de_la_lista_tiff_8_bits(self):
        if len(self.lista_dicom) == 0:
            raise ListaVaciaError()

        for i, element in enumerate(self.lista_dicom):
            if ((self.lista_dicom[i].get_pixel_data_modified()).sum() == 0):
                self.lista_dicom[i] = self.image_converter.dicom_converter_to_tiff_8_bits(element)

#---------------------------------- Metodos para transformar dicom en tiff 16 bits ------------------------------------#

    def transformar_ultimo_dicom_data_de_la_lista_tiff_16_bits(self):
        if len(self.lista_dicom) == 0:
            raise ListaVaciaError()

        data = self.lista_dicom[-1]
        self.lista_dicom[-1] = self.image_converter.dicom_converter_to_tiff_16_bits(data)

    def transformar_dicom_data_en_posicion_de_la_lista_tiff_16_bits(self, posicion):
        if len(self.lista_dicom) == 0:
            raise ListaVaciaError()
        elif posicion < 0 or posicion > len(self.lista_dicom):
            raise PosicionInvalidaError(posicion)

        data = self.lista_dicom[posicion]
        self.lista_dicom[posicion] = self.image_converter.dicom_converter_to_tiff_16_bits(data)

    def transformar_todos_los_dicom_data_de_la_lista_tiff_16_bits(self):
        if len(self.lista_dicom) == 0:
            raise ListaVaciaError()

        for i, element in enumerate(self.lista_dicom):
            if ((self.lista_dicom[i].get_pixel_data_modified()).sum() == 0):
                self.lista_dicom[i] = self.image_converter.dicom_converter_to_tiff_16_bits(element)

#------------------------------------ Metodos para borrar dicom_data de la lista --------------------------------------#

    def borrar_ultimo_dicom_data_de_la_lista(self):
        if len(self.lista_dicom) == 0:
            raise ListaVaciaError()

        del self.lista_dicom[-1]
        return True

    def borrar_dicom_data_en_posicion_de_la_lista(self, posicion):
        if len(self.lista_dicom) == 0:
            raise ListaVaciaError()
        elif posicion < 0 or posicion > len(self.lista_dicom):
            raise PosicionInvalidaError(posicion)

        del self.lista_dicom[posicion]
        return True

    def borrar_todos_los_dicom_data_de_la_lista(self):
        if len(self.lista_dicom) == 0:
            raise ListaVaciaError()

        self.lista_dicom.clear()
        return True

#---------------------------------- Metodos para transformar dicom en tiff 16 bits ------------------------------------#

    def guardar_ultimo_dicom_data_de_la_lista_16_bits(self):
        if len(self.lista_dicom) == 0:
            raise ListaVaciaError()

        data = self.lista_dicom[-1]

        output_name = f"output_image_16_bits_{len(self.lista_dicom)}.tiff"
        output_path = os.path.join(self.dir_salida, output_name)
        imageio.imsave(output_path, data.get_pixel_data_modified_16_bits(), format='tiff')
        print(f"Imagen TIFF guardada en: {output_path}")
        return output_path

    def guardar_dicom_data_en_posicion_de_la_lista_16_bits(self, posicion):
        if len(self.lista_dicom) == 0:
            raise ListaVaciaError()
        elif posicion < 0 or posicion > len(self.lista_dicom):
            raise PosicionInvalidaError(posicion)

        data = self.lista_dicom[posicion]

        output_name = f"output_image_16_bits_{posicion}.tiff"
        output_path = os.path.join(self.dir_salida, output_name)
        imageio.imsave(output_path, data.get_pixel_data_modified_16_bits(), format='tiff')
        print(f"Imagen TIFF guardada en: {output_path}")
        return output_path

    def guardar_todos_los_dicom_data_de_la_lista_16_bits(self):
        if len(self.lista_dicom) == 0:
            raise ListaVaciaError()

        for i, element in enumerate(self.lista_dicom):
            if ((self.lista_dicom[i].get_pixel_data_modified_16_bits()).sum() != 0):

                data = self.lista_dicom[i]

                output_name = f"output_image_16_bits_{i}.tiff"
                output_path = os.path.join(self.dir_salida, output_name)
                imageio.imsave(output_path, data.get_pixel_data_modified_16_bits(), format='tiff')
                print(f"Imagen TIFF guardada en: {output_path}")

#---------------------------------- Metodos para transformar dicom en tiff 8 bits ------------------------------------#

    def guardar_ultimo_dicom_data_de_la_lista_8_bits(self):
        if len(self.lista_dicom) == 0:
            raise ListaVaciaError()

        data = self.lista_dicom[-1]

        output_name = f"output_image_8_bits_{len(self.lista_dicom)}.tiff"
        output_path = os.path.join(self.dir_salida, output_name)
        imageio.imsave(output_path, data.get_pixel_data_modified_8_bits(), format='tiff')
        print(f"Imagen TIFF guardada en: {output_path}")
        return output_path

    def guardar_dicom_data_en_posicion_de_la_lista_8_bits(self, posicion):
        if len(self.lista_dicom) == 0:
            raise ListaVaciaError()
        elif posicion < 0 or posicion > len(self.lista_dicom):
            raise PosicionInvalidaError(posicion)

        data = self.lista_dicom[posicion]

        output_name = f"output_image_8_bits_{posicion}.tiff"
        output_path = os.path.join(self.dir_salida, output_name)
        imageio.imsave(output_path, data.get_pixel_data_modified_8_bits(), format='tiff')
        print(f"Imagen TIFF guardada en: {output_path}")
        return output_path

    def guardar_todos_los_dicom_data_de_la_lista_8_bits(self):
        if len(self.lista_dicom) == 0:
            raise ListaVaciaError()

        for i, element in enumerate(self.lista_dicom):
            if ((self.lista_dicom[i].get_pixel_data_modified_8_bits()).sum() != 0):

                data = self.lista_dicom[i]

                output_name = f"output_image_8_bits_{i}.tiff"
                output_path = os.path.join(self.dir_salida, output_name)
                imageio.imsave(output_path, data.get_pixel_data_modified_8_bits(), format='tiff')
                print(f"Imagen TIFF guardada en: {output_path}")