from modelo.dicom_data import DicomData
from utils.dicom_utils import DicomUtils
from utils.image_converter import ImageConverter

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

    def crear_dicom_data(self, ruta):
        ds = self.dicom_utils.read_dicom(ruta)
        print("ENTRO AQUI DE PANA SOLO UNO MODELO")
        self.dicom_data = ds
        self.lista_dicom.append(self.dicom_data)

    def crear_dicoms(self, ruta):
        ds_multiple = self.dicom_utils.read_multiple_dicom(ruta)
        print("ENTRO AQUI DE PANA MULTIPLE LOCOOOOOOO MODELO")
        for element in ds_multiple:
            self.dicom_data = element
            self.lista_dicom.append(self.dicom_data)

    def devolver_ultimo_dicom(self):
        return self.lista_dicom[-1]

    def devolver_posicion_dicom(self, posicion):
        return self.lista_dicom[posicion]

    def devolver_todos(self):
        return self.lista_dicom

    def actualizar_dicom_data_transformar_imagen_ultimo_de_la_lista(self):
        data = self.lista_dicom[-1]
        self.lista_dicom[-1] = self.image_converter.dicom_converter_to_tiff(data)

    def actualizar_dicom_data_transformar_imagen_posicion(self, posicion):
        data = self.lista_dicom[posicion]
        self.lista_dicom[posicion] = self.image_converter.dicom_converter_to_tiff(data)

    def actualizar_dicom_data_transformar_imagen_todos(self):
        for i, element in enumerate(self.lista_dicom):
            # Modifica cada elemento según sea necesario
            self.lista_dicom[i] = self.image_converter.dicom_converter_to_tiff(element)

    def borrar_dicom_data_ultimo(self):
        del self.lista_dicom[-1]

    def borrar_dicom_data_posicion(self, posicion):
        del self.lista_dicom[posicion]

    def borrar_dicom_data_todos(self):
        self.lista_dicom.clear()