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
    DICOM -> ndarray, in 8 bit integer; RGB format if it's color image
    origin: a .dcm file
    """

    return _dicom_to_img(origin, input_type='ds')


def _dicom_to_img(origin, input_type):
    """
    ds -> img (ndarray in 8 bit; RGB format if it's color image)
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

    pixel_array = pixel_array.astype('uint8')

    # Guardar como archivo TIFF
    #imageio.imwrite('output8.tiff', pixel_array)
    #if not imageio.imwrite(r'/home/rainor/PycharmProjects/tfg/output8.tiff', pixel_array):
    #    raise Exception("Could not write image")
    #imageio.imwrite(r'/home/rainor/PycharmProjects/tfg/output8.tiff', pixel_array)

    image_quality = [int(cv2.IMWRITE_JPEG_QUALITY), 90]  # 70, 55
    cv2.imwrite("/home/rainor/PycharmProjects/tfg/output8.jpg", pixel_array, image_quality)

    plt.figure()
    plt.imshow(pixel_array, cmap='gray')
    plt.show()

    return pixel_array


def _pixel_process(ds, pixel_array):
    """
    Process the images
    input image info and original pixeal_array
    applying LUTs: Modality LUT -> VOI LUT -> Presentation LUT
    return processed pixel_array, in 8bit; RGB if color
    """

    ## LUTs: Modality LUT -> VOI LUT -> Presentation LUT
    # Modality LUT, Rescale slope, Rescale Intercept
    if 'RescaleSlope' in ds and 'RescaleIntercept' in ds:
        # try applying rescale slope/intercept
        # cannot use INT, because rescale slope could be<1
        rescale_slope = float(ds.RescaleSlope)  # int(ds.RescaleSlope)
        rescale_intercept = float(ds.RescaleIntercept)  # int(ds.RescaleIntercept)
        pixel_array = (pixel_array) * rescale_slope + rescale_intercept
    else:
        # otherwise, try to apply modality
        pixel_array = apply_modality_lut(pixel_array, ds)

    # personally prefer sigmoid function than window/level
    # personally prefer LINEAR_EXACT than LINEAR (prone to err if small window/level, such as some MR images)
    if 'VOILUTFunction' in ds and ds.VOILUTFunction == 'SIGMOID':
        pixel_array = apply_voi_lut(pixel_array, ds)
    elif 'WindowCenter' in ds and 'WindowWidth' in ds:
        window_center = ds.WindowCenter
        window_width = ds.WindowWidth
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
    else:
        # if there is no window center, window width tag, try applying VOI LUT setting
        pixel_array = apply_voi_lut(pixel_array, ds)

    # Presentation VOI
    # normalize to 8 bit
    #original del codigo hermano
    #pixel_array = ((pixel_array - pixel_array.min()) / (pixel_array.max() - pixel_array.min())) * 255.0
    pixel_array = ((pixel_array - pixel_array.min()) / (pixel_array.max() - pixel_array.min())) * 255.0


    # if PhotometricInterpretation == "MONOCHROME1", then inverse; eg. xrays
    if 'PhotometricInterpretation' in ds and ds.PhotometricInterpretation == "MONOCHROME1":
        # NOT add minus directly
        pixel_array = np.max(pixel_array) - pixel_array

    # conver float -> 8-bit
    return pixel_array.astype('uint8')


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
    dicom2img(origin="/home/rainor/PycharmProjects/tfg/2-2.dcm")
    #dicom2img(origin= "/home/rainor/PycharmProjects/tfg/1-1001.dcm")

if __name__ == "__main__":
    main()