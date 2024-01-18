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


def dicom2img(origin):
    """
    DICOM -> ndarray, in 16 bit integer; RGB format if it's color image
    origin: a .dcm file
    """

    return _dicom_to_img(origin, input_type='ds')


def _dicom_to_img(origin, input_type):
    """
    ds -> img (ndarray in 16 bit; RGB format if it's color image)
    oirigin: dicomIO or dicom file path
    input_type: either ds or io
    """

    if input_type == 'ds':
        origin = Path(origin)
        if origin.exists() is False:
            raise Exception(f"'{origin}' does not exist")
        elif origin.is_file() is False:
            raise Exception(f"'{origin}' is not a file")
        elif origin.suffix.lower() != '.dcm':
            raise Exception('Input file type should be a DICOM file')
    else:
        if type(origin) != io.BytesIO:
            raise TypeError("BytesIO is expected")

    # read images and their pixel data
    ds = pydicom.dcmread(origin, force=True)
    print("tipe ds", type(ds))

    print("tipe pixel_data", type(ds.pixel_array))

    resolution = (ds.Rows, ds.Columns)
    print(resolution)
    min_pixel_value = ds.pixel_array.min()
    print("tipe de min pixel value", type(min_pixel_value))
    max_pixel_value = ds.pixel_array.max()
    print("Minimo valor ", min_pixel_value, " Maximo valor ", max_pixel_value)
    plt.figure()
    plt.imshow(ds.pixel_array, cmap='gray')


    # to exclude unsupported SOP class by its UID
    is_unsupported = _is_unsupported(ds)
    if is_unsupported:
        print(is_unsupported())
        return None

    # load pixel_array
    # *** This is one of the time-limited step  ***
    pixel_array = ds.pixel_array.astype(float)  # preparing for scaling

    # if pixel_array.shape[2]==3 -> means color files [x,x,3]
    # [o,x,x] means multiframe
    if len(pixel_array.shape) == 3 and pixel_array.shape[2] != 3:
        print('Multiframe images are currently not supported')
        return None

    #################
    # Process image #
    #################
    pixel_array = _pixel_process(ds, pixel_array)

    pixel_array = pixel_array.astype('uint16')


    plt.figure()
    plt.imshow(pixel_array, cmap='gray')
    plt.show()

    #Para el de 8bits
    #imageio.imwrite('output.tiff', pixel_array)
    # Guardar como archivo TIFF
    imageio.imwrite('output16.tiff', pixel_array)

    return pixel_array


def _pixel_process(ds, pixel_array):
    """
    Process the images
    input image info and original pixel_array
    applying LUTs: Modality LUT -> VOI LUT -> Presentation LUT
    return processed pixel_array, in 16bit; RGB if color
    """

    #Este codigo sirve para poder obtener o checkear si existe un valor dadod el DICOM puede ayudar si necesito checkear alguna cosa
    if '0028' in ds and '3000' in ds[0x0028]:
        lut_descriptor = ds[0x0028, 0x3000].value
        print("LUT Descriptor:", lut_descriptor)
    else:
        print("El atributo (0028, 3000) no está presente en el conjunto de datos.")


    # LUTs: Modality LUT -> VOI LUT -> Presentation LUT
    # Modality LUT, Rescale slope, Rescale Intercept
    if 'RescaleSlope' in ds and 'RescaleIntercept' in ds:
        # try applying rescale slope/intercept
        # cannot use INT, because rescale slope could be<1
        rescale_slope = float(ds.RescaleSlope)  # int(ds.RescaleSlope)
        rescale_intercept = float(ds.RescaleIntercept)  # int(ds.RescaleIntercept)
        print ("Rescale_slope ", rescale_slope, type(rescale_slope))
        print("Rescale_intercept ", rescale_intercept, type(rescale_slope))
        pixel_array = (pixel_array) * rescale_slope + rescale_intercept
        #print("pixel array despues de la multiplicacion del rescale slope y lo otro ", pixel_array)
    else:
        # otherwise, try to apply modality
        pixel_array = apply_modality_lut(pixel_array, ds)
        #print("pixel array despues apply_modality_lut ", pixel_array)

    pixel_array = apply_modality_lut(pixel_array, ds)
    print("movidon")
    print("Tipo de pixel_array:", (pixel_array.dtype))

    # personally prefer sigmoid function than window/level
    # personally prefer LINEAR_EXACT than LINEAR (prone to err if small window/level, such as some MR images)
    if 'VOILUTFunction' in ds and ds.VOILUTFunction == 'SIGMOID':
        pixel_array = apply_voi_lut(pixel_array, ds)
        #print("pixel array despues apply_voi_lut ", pixel_array)
    elif 'WindowCenter' in ds and 'WindowWidth' in ds:
        window_center = ds.WindowCenter
        print("WindowCenter ", type(window_center))
        window_width = ds.WindowWidth
        print("WindowWidth ", type(window_width))
        # some values may be stored in an array
        if type(window_center) == pydicom.multival.MultiValue:
            window_center = float(window_center[0])
        else:
            window_center = float(window_center)
        if type(window_width) == pydicom.multival.MultiValue:
            window_width = float(window_width[0])
        else:
            window_width = float(window_width)
        pixel_array = _get_LUT_value_LINEAR_EXACT(pixel_array, window_width, window_center)
        #print("aplicar toda la movida de ifs y pixel array despues _get_LUT_value_LINEAR_EXACT ", pixel_array)
    else:
        # if there is no window center, window width tag, try applying VOI LUT setting
        pixel_array = apply_voi_lut(pixel_array, ds)

    pixel_array = apply_voi_lut(pixel_array, ds)
    print("Tipo de pixel_array apply voi lut:", (pixel_array.dtype))
    #print("vuelve a aplicar el apply_voi_lut", pixel_array)


    # Presentation VOI
    # normalize to 16 bit
    pixel_array = ((pixel_array - pixel_array.min()) / (pixel_array.max() - pixel_array.min())) * 65535.0


    # if PhotometricInterpretation == "MONOCHROME1", then inverse; eg. xrays
    #Esto es probable que se vaya del codigo ya que la idea es elegir que opcion queremos de alguna forma y con cambiar el signo al normalizar ya llega
    print("Tipo de PhotometricInterpretation:", (ds.PhotometricInterpretation))
    if 'PhotometricInterpretation' in ds and ds.PhotometricInterpretation == "MONOCHROME1":
        #Este valor de PhotometricInterpretation se usa para saber si los valores mas altos de la imagen representan el blanco o el negro.
        #MONOCHROME1 representa que los valores mas altos son los valores oscuros. Por tanto lo que hacemos aqui es invertirlos.
        # NOT add minus directly
        pixel_array = np.max(pixel_array) - pixel_array

    # conver float -> 16-bit
    pixel_array = pixel_array.astype('uint16')
    print("pixel_array final ", type(pixel_array))

    return pixel_array.astype('uint16')


#Esta funcion se encarga de truncar los valores que se salga de nuestra ventana para que tomen los valores mas altos o mas bajos que tenemos disponibles
def _get_LUT_value_LINEAR_EXACT(data, window, level):
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

def _is_unsupported(ds):
    """
    input ds
    if unsupported, return SOP class name
    if supported, return False
    """
    # to exclude unsupported SOP class by its UID
    # PDF
    try:
        if ds.SOPClassUID == '1.2.840.10008.5.1.4.1.1.104.1':
            return 'Encapsulated PDF Storage'
        # exclude object selection document
        elif ds.SOPClassUID=='1.2.840.10008.5.1.4.1.1.88.59':
            return 'Key Object Selection Document'
    except:
        pass
    return False

def main():

    #dicom2img(origin="/home/rainor/PycharmProjects/tfg/ImagenesDICOM/1-1001.dcm")
    #dicom2img(origin= "/home/rainor/PycharmProjects/tfg/ImagenesDICOM/2-1.dcm")
    dicom2img(origin= "/home/rainor/PycharmProjects/tfg/ImagenesDICOM/2-2.dcm")

if __name__ == "__main__":
    main()