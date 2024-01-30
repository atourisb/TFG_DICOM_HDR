from utils.dicom_utils import DicomUtils
from utils.image_converter import ImageConverter
from utils.indexTracker import IndexTracker
from modelo.dicom_data import DicomData
from vista.vista import Vista
import json
from excepciones.excepciones import *

# Controlador
#Puedo hacer una cola o una pila para ver y mostrar las imagenes y asi tener persistencia? una array y poder moverte borrar y tal despues de cargar las imagenes y leerlas o algo.
# Que haya una opcion de ver una sola imagen o la opcion de que cargue todas las imagenes y asi puedo usar lo del scroll una vez estan cargadas.
class Controlador:

    mensajes = None

    def __init__(self, modelo, vista):
        self.modelo = modelo
        self.vista = vista
        ruta_archivo = '/home/rainor/PycharmProjects/tfg/utils/archivo_de_mensajes.json'
        try:
            with open(ruta_archivo, 'r') as file:
                self.mensajes = json.load(file)
        except FileNotFoundError:
            raise ArchivoNoEncontradoError(ruta_archivo)

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

    def visualizar_ultimo_dicom(self):
        try:
            print(self.mensajes['visualizar_ultimo_dicom'])
            data = self.modelo.devolver_ultimo_dicom_data_de_la_lista()
            self.vista.mostrar_dicom_original_y_dicom_transformado(data)
        except ListaVaciaError as e:
            print("Error", e)
            raise

    def visualizar_dicom_en_posicion(self, posicion):
        try:
            print(self.mensajes['visualizar_dicom_en_posicion'])
            data = self.modelo.devolver_dicom_data_en_posicion_de_la_lista(posicion)
            self.vista.mostrar_dicom_original_y_dicom_transformado(data)
        except (ListaVaciaError, PosicionInvalidaError) as e:
            print("Error", e)
            raise

    def visualizar_todos_los_dicom(self):
        try:
            print(self.mensajes['visualizar_todos_los_dicom'])
            lista = self.modelo.devolver_todos_los_dicom_data_de_la_lista()
            for element in lista:
                self.vista.mostrar_dicom_original_y_dicom_transformado(element)
        except ListaVaciaError as e:
            print("Error", e)
            raise

    def transformar_ultimo_dicom(self):
        try:
            print(self.mensajes['transformar_ultimo_dicom'])
            self.modelo.transformar_ultimo_dicom_data_de_la_lista()
        except ListaVaciaError as e:
            print("Error", e)
            raise

    def transformar_dicom_en_posicion(self, posicion):
        try:
            print(self.mensajes['transformar_dicom_en_posicion'])
            self.modelo.transformar_dicom_data_en_posicion_de_la_lista(posicion)
        except (ListaVaciaError, PosicionInvalidaError) as e:
            print("Error", e)
            raise


    def transformar_todos_los_dicom(self):
        try:
            print(self.mensajes['transformar_todos_los_dicom'])
            self.modelo.transformar_todos_los_dicom_data_de_la_lista()
        except ListaVaciaError as e:
            print("Error", e)
            raise

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
        self.vista.mostrar_cantidad_de_la_lista(lista)