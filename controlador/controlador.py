from utils.dicom_utils import DicomUtils
from utils.image_converter import ImageConverter
from utils.indexTracker import IndexTracker
from modelo.dicom_data import DicomData
from vista.vista import Vista
import json
from excepciones.excepciones import *
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

# Controlador
#Puedo hacer una cola o una pila para ver y mostrar las imagenes y asi tener persistencia? una array y poder moverte borrar y tal despues de cargar las imagenes y leerlas o algo.
# Que haya una opcion de ver una sola imagen o la opcion de que cargue todas las imagenes y asi puedo usar lo del scroll una vez estan cargadas.
class Controlador:

    mensajes = None

    def __init__(self, modelo):
        self.modelo = modelo
        ruta_archivo = '/home/rainor/PycharmProjects/tfg/utils/archivo_de_mensajes.json'
        try:
            with open(ruta_archivo, 'r') as file:
                self.mensajes = json.load(file)
        except FileNotFoundError:
            raise ArchivoNoEncontradoError(ruta_archivo)

    # def mostrar_ventana(self):
    #     self.vista.mostrar_ventana()

#------------------------------------- Metodos para cargar dicom en el sistema ----------------------------------------#

    def cargar_unico_dicom(self, ruta):
        try:
            print(self.mensajes['cargar_imagen_unica'])
            self.modelo.crear_y_agreagar_a_la_lista_dicom_data(ruta)
        except (ArchivoNoEncontradoError, NoEsArchivoError, ExtensionIncorrectaError) as e:
            print("Error:", e)
            raise

    def cargar_multiples_dicom(self, ruta):
        try:
            print(self.mensajes['cargar_imagenes_multiples'])
            self.modelo.crear_y_agreagar_a_la_lista_multiples_dicom_data_(ruta)
        except (DirectorioNoExisteError, ArchivosDCMNoEncontradosError) as e:
            print("Error:", e)
            raise

#--------------------------------------- Metodos que probablemente se vayan -------------------------------------------#

    def visualizar_ultimo_dicom(self):
        try:
            print(self.mensajes['visualizar_ultimo_dicom'])
            data = self.modelo.devolver_ultimo_dicom_data_de_la_lista()
            #self.vista.mostrar_dicom_original_y_dicom_transformado(data)
        except ListaVaciaError as e:
            print("Error", e)
            raise

    def visualizar_dicom_en_posicion(self, posicion):
        try:
            print(self.mensajes['visualizar_dicom_en_posicion'])
            data = self.modelo.devolver_dicom_data_en_posicion_de_la_lista(posicion)
            #self.vista.mostrar_dicom_original_y_dicom_transformado(data)
        except (ListaVaciaError, PosicionInvalidaError) as e:
            print("Error", e)
            raise

    def visualizar_todos_los_dicom(self):
        try:
            print(self.mensajes['visualizar_todos_los_dicom'])
            lista = self.modelo.devolver_todos_los_dicom_data_de_la_lista()
            #for element in lista:
                #self.vista.mostrar_dicom_original_y_dicom_transformado(element)
        except ListaVaciaError as e:
            print("Error", e)
            raise

#---------------------------------- Metodos para transformar dicom en tiff 16 bits ------------------------------------#

    def transformar_ultimo_dicom_tiff_16_bits(self):
        try:
            print(self.mensajes['transformar_ultimo_dicom'])
            self.modelo.transformar_ultimo_dicom_data_de_la_lista_tiff_16_bits()
        except ListaVaciaError as e:
            print("Error", e)
            raise

    def transformar_dicom_en_posicion_tiff_16_bits(self, posicion):
        try:
            print(self.mensajes['transformar_dicom_en_posicion'])
            self.modelo.transformar_dicom_data_en_posicion_de_la_lista_tiff_16_bits(posicion)
        except (ListaVaciaError, PosicionInvalidaError) as e:
            print("Error", e)
            raise


    def transformar_todos_los_dicom_tiff_16_bits(self):
        try:
            print(self.mensajes['transformar_todos_los_dicom'])
            self.modelo.transformar_todos_los_dicom_data_de_la_lista_tiff_16_bits()
        except ListaVaciaError as e:
            print("Error", e)
            raise

    # ---------------------------------- Metodos para transformar dicom en tiff 8 bits ------------------------------------#

    def transformar_ultimo_dicom_tiff_8_bits(self):
        try:
            print(self.mensajes['transformar_ultimo_dicom'])
            self.modelo.transformar_ultimo_dicom_data_de_la_lista_tiff_8_bits()
        except ListaVaciaError as e:
            print("Error", e)
            raise

    def transformar_dicom_en_posicion_tiff_8_bits(self, posicion):
        try:
            print(self.mensajes['transformar_dicom_en_posicion'])
            self.modelo.transformar_dicom_data_en_posicion_de_la_lista_tiff_8_bits(posicion)
        except (ListaVaciaError, PosicionInvalidaError) as e:
            print("Error", e)
            raise

    def transformar_todos_los_dicom_tiff_8_bits(self):
        try:
            print(self.mensajes['transformar_todos_los_dicom'])
            self.modelo.transformar_todos_los_dicom_data_de_la_lista_tiff_8_bits()
        except ListaVaciaError as e:
            print("Error", e)
            raise

#---------------------------------------- Metodos para borrar dicom cargados ------------------------------------------#

    def borrar_ultimo_dicom_cargado(self):
        try:
            print(self.mensajes['borrar_ultimo_dicom_cargado'])
            self.modelo.borrar_ultimo_dicom_data_de_la_lista()
        except ListaVaciaError as e:
            print("Error", e)
            raise

    def borrar_dicom_cargado_en_posicion(self, posicion):
        try:
            print(self.mensajes['borrar_dicom_cargado_en_posicion'])
            self.modelo.borrar_dicom_data_en_posicion_de_la_lista(posicion)
        except (ListaVaciaError, PosicionInvalidaError) as e:
            print("Error", e)
            raise

    def borrar_todos_los_dicom_cargados_de_la_lista(self):
        try:
            print(self.mensajes['borrar_todos_los_dicom_cargados_de_la_lista'])
            self.modelo.borrar_todos_los_dicom_data_de_la_lista()
        except ListaVaciaError as e:
            print("Error", e)
            raise

    def mostrar_cantidad_de_dicom_cargados(self):
        print(self.mensajes['mostrar_cantidad_de_dicom_cargados'])
        lista = self.modelo.devolver_todos_los_dicom_data_de_la_lista()
        #self.vista.mostrar_cantidad_de_la_lista(lista)

#---------------------------------------- Metodos para guardar tiff 16 bits -------------------------------------------#

    def guardar_ultimo_dicom_tiff_16_bits(self):
        try:
            print(self.mensajes['guardar_ultimo_dicom'])
            output_path = self.modelo.guardar_ultimo_dicom_data_de_la_lista_16_bits()
            return output_path
        except ListaVaciaError as e:
            print("Error", e)
            raise

    def guardar_dicom_en_posicion_tiff_16_bits(self, posicion):
        try:
            print(self.mensajes['guardar_dicom_en_posicion'])
            output_path = self.modelo.guardar_dicom_data_en_posicion_de_la_lista_16_bits(posicion)
            return output_path
        except (ListaVaciaError, PosicionInvalidaError) as e:
            print("Error", e)
            raise


    def guardar_todos_los_dicom_tiff_16_bits(self):
        try:
            print(self.mensajes['guardar_todos_los_dicom'])
            self.modelo.guardar_todos_los_dicom_data_de_la_lista_16_bits()
        except ListaVaciaError as e:
            print("Error", e)
            raise

#---------------------------------------- Metodos para guardar tiff 8 bits -------------------------------------------#

    def guardar_ultimo_dicom_tiff_8_bits(self):
        try:
            print(self.mensajes['guardar_ultimo_dicom'])
            output_path =self.modelo.guardar_ultimo_dicom_data_de_la_lista_8_bits()
            return output_path
        except ListaVaciaError as e:
            print("Error", e)
            raise

    def guardar_dicom_en_posicion_tiff_8_bits(self, posicion):
        try:
            print(self.mensajes['guardar_dicom_en_posicion'])
            output_path = self.modelo.guardar_dicom_data_en_posicion_de_la_lista_8_bits(posicion)
            return output_path
        except (ListaVaciaError, PosicionInvalidaError) as e:
            print("Error", e)
            raise


    def guardar_todos_los_dicom_tiff_8_bits(self):
        try:
            print(self.mensajes['guardar_todos_los_dicom'])
            self.modelo.guardar_todos_los_dicom_data_de_la_lista_8_bits()
        except ListaVaciaError as e:
            print("Error", e)
            raise

#Metodos para la vista

    def transformacion_y_guardado_vista(self, ruta):
        self.cargar_unico_dicom(ruta)
        self.transformar_ultimo_dicom_tiff_8_bits()
        output_path_8bits = self.guardar_ultimo_dicom_tiff_8_bits()

        self.transformar_ultimo_dicom_tiff_16_bits()
        output_path_16bits = self.guardar_ultimo_dicom_tiff_16_bits()

        # Esta tupla contiene los paths de los dos archivos en 8 y en 16 bits
        tuple = (output_path_8bits, output_path_16bits)

        return tuple

