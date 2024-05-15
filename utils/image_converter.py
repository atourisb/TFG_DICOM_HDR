import matplotlib.pyplot as plt
import pydicom
from pydicom.pixel_data_handlers.util import apply_voi_lut, apply_modality_lut
import numpy as np
import modelo.dicom_data as dicom_data
from modelo.dicom_data import DicomData
from utils.dicom_utils import DicomUtils

class ImageConverter:

    #usar el ds y mirar con unique los valores del array
    #4 bits de profundidad y comprar con el mio

    def dicom_converter_to_tiff_16_bits(self, dicom: dicom_data):

        # Cargamos el pixel_array de la imagen original para ser procesada
        pixel_array = dicom.pixel_data_original

        # Esta linea es para comprobar si la imagen que nos llega es multiframe, si lo es nos da un error
        if len(pixel_array.shape) == 3 and pixel_array.shape[2] != 3:
            print('DICOM Multiframe no son soportados')
            return None

        # Procesamos la imagen
        dicom = self.process_dicom_16_bits(dicom)

        return dicom

    def dicom_converter_to_tiff_8_bits(self, dicom: dicom_data):

        # Cargamos el pixel_array de la imagen original para ser procesada
        pixel_array = dicom.pixel_data_original

        # Esta linea es para comprobar si la imagen que nos llega es multiframe, si lo es nos da un error
        if len(pixel_array.shape) == 3 and pixel_array.shape[2] != 3:
            print('DICOM Multiframe no son soportados')
            return None

        # Procesamos la imagen
        dicom = self.process_dicom_8_bits(dicom)

        return dicom

    #-------------------------------------------------------------------------------------------------------------------

    def aplicar_modalidad_lut(self, dicom):

        # Comprobamos si existen los valores rescale slope y rescale intercept
        # Rescale slope y rescale intercept permiten realizar una transformacion lineal a los valores originales de la imagen
        # Para ajustarlos a un rango adecuado segun como se operen con ellos, por ejemplo cambiar la visualizacion mediante un software.
        if dicom.get_rescale_slope() is not None and dicom.get_rescale_intercept() is not None:
            rescale_slope = dicom.get_rescale_slope()
            rescale_intercept = dicom.get_rescale_intercept()
            pixel_data_modified = (dicom.get_pixel_data_original()) * rescale_slope + rescale_intercept
        else:
            # La funcion apply_modality_lut toma como entrada la imagen del DICOM y aplica los valores de la tabla LUT para cada pixel
            # Ajustando el contraste, brillo y otras correcciones para visualizar la imagen.
            pixel_data_modified = apply_modality_lut(dicom.get_pixel_data_original(), dicom.get_ds())

        # Devuelve el array con los pixeles de la imagen modificados
        return pixel_data_modified

    #-------------------------------------------------------------------------------------------------------------------

    # Funcion que aplica la ventana de interes a los valores de la imagen DICOM, devolviendo un array con la imagen modificada
    def aplicar_voi_lut(self, pixel_data_modified_parameter, dicom):
        # Campo del DICOM que define la funcion que se utilizara para aplicar la ventana a la imagen, lineal o no lineal, para resaltar ciertos pixeles
        if dicom.get_voi_lut_function() is not None and dicom.get_voi_lut_function() == 'SIGMOID':
            pixel_data_modified = apply_voi_lut(pixel_data_modified_parameter, dicom.get_ds())

        elif dicom.get_window_center() is not None and dicom.get_window_width() is not None:
            window_center = dicom.get_window_center()
            window_width = dicom.get_window_width()

            # Checkeamos que si los valores vienen en un array, no aseguramos de conseguir el valor y convertirlo en float
            # Ya que la imagen tambien esta en valores float y asi no tenemos problemas al hacer las transformaciones
            if type(window_center) == pydicom.multival.MultiValue:
                window_center = float(window_center[0])
            else:
                window_center = float(window_center)
            if type(window_width) == pydicom.multival.MultiValue:
                window_width = float(window_width[0])
            else:
                window_width = float(window_width)
            pixel_data_modified = self.get_LUT_value_LINEAR(pixel_data_modified_parameter, window_width, window_center)
        else:
            # Si no existe ningun valor ni valores de la ventana el centro o el ancho de ventana aplicamos la configuracion VOI LUT
            pixel_data_modified = apply_voi_lut(pixel_data_modified_parameter, dicom.get_ds())

        # Devuelve una matriz de píxeles que representa la imagen después de aplicar la Ventana de Interés
        return pixel_data_modified

    #-------------------------------------------------------------------------------------------------------------------

    #Esta funcion se encarga de truncar los valores que se salga de nuestra ventana para que tomen los valores mas altos o mas bajos que tenemos disponibles
    def get_LUT_value_LINEAR(self, data, window, level):

        """
        Teniendo en cuenta el VOI LUT y los valores de anchura y centro
        """
        data_min = data.min()
        data_max = data.max()

        data_range = data_max - data_min
        data = np.piecewise(data,
            [data<=(level-(window)/2),
            data>(level+(window)/2)],
            [data_min, data_max, lambda data: ((data-level+window/2)/window*data_range)+data_min])
        return data


    #-------------------------------------------------------------------------------------------------------------------

    def process_dicom_16_bits(self, dicom: dicom_data):

        # Procesamos la imagen
        # Entrada dicom_data que contiene la info original cargada del DICOM y los campos que son necesarios para el procesado de la imagen
        # Aplicamos LUTs: modalidad LUT -> VOI LUT
        # Devuelve la imagen procesada, in 16bit

        # LUTs: Modality LUT -> VOI LUT -> Presentation LUT
        # Aplicamos la funcion apply_modality_lut teniendo en cuenta los valores Rescale slope, Rescale Intercept
        pixel_data_modified_16_bits = self.aplicar_modalidad_lut(dicom)

        # Duda sobre si esos valores se tienen que normalizar y no se como ya que al final pasa lo mismo que cuando usas los 255 es ir buscandolos a pelo
        # si los valores que usas de ventana son el centro 65535/2 y la anchura 65535 se ve la misma imagen que la inicial
        # Aplicamos la funcion apply_voi_lut para obtener la matriz con los valores de la ventana de interes segun el centro de la ventana y la anchura
        pixel_data_modified_16_bits = self.aplicar_voi_lut(pixel_data_modified_16_bits, dicom)

        # normalizamos a 16 bit
        pixel_data_modified_16_bits = ((pixel_data_modified_16_bits - dicom.get_min_pixel_value()) / (dicom.get_max_pixel_value() - dicom.get_min_pixel_value())) * 65535.0
        pixel_data_modified_16_bits = pixel_data_modified_16_bits.astype('uint16')

        dicom.set_pixel_data_modified_16_bits(pixel_data_modified_16_bits)

        #Devolvemos el objeto dicom_data con el campo pixel_data_modified con la imagen resultante del proceso
        return dicom


#----------------------------------------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------------------------------------------------#

    def process_dicom_8_bits(self, dicom: dicom_data):

        # Procesamos la imagen
        # Entrada dicom_data que contiene la info original cargada del DICOM y los campos que son necesarios para el procesado de la imagen
        # Aplicamos LUTs: modalidad LUT -> VOI LUT
        # Devuelve la imagen procesada, in 16bit


        # LUTs: Modality LUT -> VOI LUT -> Presentation LUT
        # Aplicamos la funcion apply_modality_lut teniendo en cuenta los valores Rescale slope, Rescale Intercept
        pixel_data_modified_8_bits = self.aplicar_modalidad_lut(dicom)

        # Duda sobre si esos valores se tienen que normalizar y no se como ya que al final pasa lo mismo que cuando usas los 255 es ir buscandolos a pelo
        # si los valores que usas de ventana son el centro 65535/2 y la anchura 65535 se ve la misma imagen que la inicial
        # Aplicamos la funcion apply_voi_lut para obtener la matriz con los valores de la ventana de interes segun el centro de la ventana y la anchura
        pixel_data_modified_8_bits = self.aplicar_voi_lut(pixel_data_modified_8_bits, dicom)

        # normalizamos a 16 bit
        pixel_data_modified_8_bits = ((pixel_data_modified_8_bits - dicom.get_min_pixel_value()) / (dicom.get_max_pixel_value() - dicom.get_min_pixel_value())) * 255.0

        pixel_data_modified_8_bits = pixel_data_modified_8_bits.astype('uint8')

        dicom.set_pixel_data_modified_8_bits(pixel_data_modified_8_bits)

        #Devolvemos el objeto dicom_data con el campo pixel_data_modified con la imagen resultante del proceso
        return dicom


def main():

    dicom_utils = DicomUtils()
    ds = dicom_utils.read_dicom("/home/rainor/PycharmProjects/tfg/ImagenesDICOM/2-1.dcm")

    #ds = pydicom.dcmread("/home/rainor/PycharmProjects/tfg/ImagenesDICOM/2-2.dcm", force=True)
    dicom = DicomData(ds)
    converter = ImageConverter()
    dicomfinal = converter.dicom_converter_to_tiff_16_bits(dicom)

    plt.figure()
    plt.imshow(dicomfinal.pixel_data_original, cmap='gray')
    plt.figure()
    plt.imshow(dicomfinal.pixel_data_modified_16_bits, cmap='gray')
    plt.show()

    dicomfinal = converter.dicom_converter_to_tiff_8_bits(dicom)

    plt.figure()
    plt.imshow(dicomfinal.pixel_data_original, cmap='gray')
    plt.figure()
    plt.imshow(dicomfinal.pixel_data_modified_8_bits, cmap='gray')
    plt.show()


if __name__ == "__main__":
    main()