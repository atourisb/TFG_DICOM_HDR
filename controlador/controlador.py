from utils.dicom_utils import DicomUtils
from utils.image_converter import ImageConverter
from utils.indexTracker import IndexTracker
from modelo.dicom_data import DicomData
from vista.vista import Vista

# Controlador
#Puedo hacer una cola o una pila para ver y mostrar las imagenes y asi tener persistencia? una array y poder moverte borrar y tal despues de cargar las imagenes y leerlas o algo.
# Que haya una opcion de ver una sola imagen o la opcion de que cargue todas las imagenes y asi puedo usar lo del scroll una vez estan cargadas.
class Controlador:

    def __init__(self, modelo, vista):
        self.modelo = modelo
        self.vista = vista

    #PROBADO
    def cargar_imagen(self, ruta = "/home/rainor/PycharmProjects/tfg/ImagenesDICOM/2-2.dcm"):
        self.modelo.crear_dicom_data(ruta)

    #PROBADO
    def cargar_multiples_imagen(self, ruta="/home/rainor/PycharmProjects/tfg/ImagenesDICOM/*.dcm"):
        self.modelo.crear_dicoms(ruta)

    #PROBADO
    def mostrar_imagen_la_ultima(self):
        data = self.modelo.devolver_ultimo_dicom()
        self.vista.mostrar_imagen(data)

    #PROBADO
    def mostrar_imagen_posicion(self, posicion):
        data = self.modelo.devolver_posicion_dicom(posicion)
        self.vista.mostrar_imagen(data)

    #PROBADO
    def mostrar_imagen_todos(self):
        lista = self.modelo.devolver_todos()
        for element in lista:
            self.vista.mostrar_imagen(element)

    #PROBADO
    def convertir_imagen_ultimo(self):
        self.modelo.actualizar_dicom_data_transformar_imagen_ultimo_de_la_lista()

    def convertir_imagen_posicion(self, posicion):
        self.modelo.actualizar_dicom_data_transformar_imagen_posicion(posicion)

    #PROBADO
    def convertir_imagen_todos(self):
        self.modelo.actualizar_dicom_data_transformar_imagen_todos()

    # PROBADO
    def borrar_ultimo(self):
        self.modelo.borrar_dicom_data_ultimo()

    #PROBADO
    def borrar_posicion(self, posicion):
        self.modelo.borrar_dicom_data_posicion(posicion)

    #PROBADO
    def borrar_toda_la_lista(self):
        self.modelo.borrar_dicom_data_todos()

    #PROBADO
    def show_lista(self):
        lista = self.modelo.devolver_todos()
        self.vista.mostrar_lista(lista)

    #def actualizar_vista(self):
    #    data = self.imagenes_cargadas[0]
    #    print (data.max_pixel_value)