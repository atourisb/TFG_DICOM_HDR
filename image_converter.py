import matplotlib.pyplot as plt
import pydicom
from pydicom.pixel_data_handlers.util import apply_voi_lut, apply_modality_lut
import cv2
import numpy as np
from pathlib import Path
import os
import time
import io
import concurrent.futures
import imageio
import dicom_data
from dicom_data import DicomData
from dicom_utils import DicomUtils

class ImageConverter:

    def dicom_converter_to_tiff(self, dicom: dicom_data):

        # load pixel_array
        # *** This is one of the time-limited step  ***
        pixel_array = dicom.pixel_data_original  # preparing for scaling

        # if pixel_array.shape[2]==3 -> means color files [x,x,3]
        # [o,x,x] means multiframe
        if len(pixel_array.shape) == 3 and pixel_array.shape[2] != 3:
            print('DICOM Multiframe no son soportados')
            return None

        #################
        # Process image #
        #################

        dicom = self.process_dicom(dicom)

        return dicom



    def process_dicom(self, dicom: dicom_data):

        """
        Process the images
        input image info and original pixel_array
        applying LUTs: Modality LUT -> VOI LUT -> Presentation LUT
        return processed pixel_array, in 16bit; RGB if color
        """

        # LUTs: Modality LUT -> VOI LUT -> Presentation LUT
        # Modality LUT, Rescale slope, Rescale Intercept
        if dicom.get_rescale_slope() is not None and dicom.get_rescale_intercept() is not None:
            # try applying rescale slope/intercept
            # cannot use INT, because rescale slope could be<1
            rescale_slope = dicom.get_rescale_slope()  # int(ds.RescaleSlope)
            rescale_intercept = dicom.get_rescale_intercept()  # int(ds.RescaleIntercept)
            pixel_data_modified = (dicom.get_pixel_data_original()) * rescale_slope + rescale_intercept
            # print("pixel array despues de la multiplicacion del rescale slope y lo otro ", pixel_array)
        else:
            # otherwise, try to apply modality
            pixel_data_modified = apply_modality_lut(dicom.get_pixel_data_original(), dicom.get_ds())

        pixel_data_modified = apply_modality_lut(dicom.get_pixel_data_original(), dicom.get_ds())

        # ---------------------------------------------------------------------------------------------------------------

        #PENSAR SI EN LUGAR DE LOS NONE PONGO LO QUE ESTABA ORIGINALMENTE mirando directamente en el ds del dicom

        # personally prefer sigmoid function than window/level
        # personally prefer LINEAR_EXACT than LINEAR (prone to err if small window/level, such as some MR images)
        if dicom.get_voi_lut_function() is not None and dicom.get_voi_lut_function() == 'SIGMOID':
            pixel_data_modified = apply_voi_lut(pixel_data_modified, dicom.get_ds())

        elif dicom.get_window_center() is not None and dicom.get_window_width() is not None:
            window_center = dicom.get_window_center()
            window_width = dicom.get_window_width()
            # some values may be stored in an array
            if type(window_center) == pydicom.multival.MultiValue:
                window_center = float(window_center[0])
            else:
                window_center = float(window_center)
            if type(window_width) == pydicom.multival.MultiValue:
                window_width = float(window_width[0])
            else:
                window_width = float(window_width)
            pixel_data_modified = self._get_LUT_value_LINEAR_EXACT(pixel_data_modified, window_width, window_center)
        else:
            # if there is no window center, window width tag, try applying VOI LUT setting
            pixel_data_modified = apply_voi_lut(pixel_data_modified, dicom.get_ds())

        pixel_data_modified = apply_voi_lut(pixel_data_modified, dicom.get_ds())

        #---------------------------------------------------------------------------------------------------------------

        # Presentation VOI
        # normalize to 16 bit
        pixel_data_modified = ((pixel_data_modified - dicom.get_min_pixel_value()) / (dicom.get_max_pixel_value() - dicom.get_min_pixel_value())) * 65535.0

        # ---------------------------------------------------------------------------------------------------------------

        # if PhotometricInterpretation == "MONOCHROME1", then inverse; eg. xrays
        # Esto es probable que se vaya del codigo ya que la idea es elegir que opcion queremos de alguna forma y con cambiar el signo al normalizar ya llega

        if dicom.get_photometric_interpretation() is not None and dicom.get_photometric_interpretation() == "MONOCHROME1":
            # Este valor de PhotometricInterpretation se usa para saber si los valores mas altos de la imagen representan el blanco o el negro.
            # MONOCHROME1 representa que los valores mas altos son los valores oscuros. Por tanto lo que hacemos aqui es invertirlos.
            # NOT add minus directly
            pixel_data_modified = np.max(pixel_data_modified) - pixel_data_modified

        # ---------------------------------------------------------------------------------------------------------------

        # conver float -> 16-bit
        pixel_data_modified = pixel_data_modified.astype('uint16')

        dicom.set_pixel_data_modified(pixel_data_modified)

        #return pixel_data_modified.astype('uint16')

        return dicom

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    #Esta funcion se encarga de truncar los valores que se salga de nuestra ventana para que tomen los valores mas altos o mas bajos que tenemos disponibles
    def _get_LUT_value_LINEAR_EXACT(self, data, window, level):
        """
        Adjust according to VOI LUT, window center(level) and width values
        not normalized
        """
        data_min = data.min()
        data_max = data.max()
        data_range = data_max - data_min
        data = np.piecewise(data,
            [data<=(level-(window)/2),
            data>(level+(window)/2)],
            [data_min, data_max, lambda data: ((data-level+window/2)/window*data_range)+data_min])
        return data

def main():

    ds = DicomUtils.read_dicom("/home/rainor/PycharmProjects/tfg/ImagenesDICOM/2-2.dcm")

    ds = pydicom.dcmread("/home/rainor/PycharmProjects/tfg/ImagenesDICOM/2-2.dcm", force=True)
    dicom = DicomData(ds)
    converter = ImageConverter()
    dicomfinal = converter.dicom_converter_to_tiff(dicom)

    plt.figure()
    plt.imshow(dicomfinal.pixel_data_original, cmap='gray')
    plt.figure()
    plt.imshow(dicomfinal.pixel_data_modified, cmap='gray')
    plt.show()


if __name__ == "__main__":
    main()