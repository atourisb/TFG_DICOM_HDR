import pydicom
import numpy as np


class DicomData:
    """Atributos de tipo de dato usado para guardar la info extraida del DICOM"""

    ds: pydicom.dataset.FileDataset
    pixel_data_original: np.ndarray
    pixel_data_modified: np.ndarray
    min_pixel_value: np.uint16
    max_pixel_value: np.uint16
    window_center: pydicom.multival.MultiValue
    window_width: pydicom.multival.MultiValue
    rescale_slope: float = None
    rescale_intercept: float = None
    VOI_LUT_function: str = None
    photometric_interpretation: str = None

    def __init__(self, dicom: pydicom.dataset.FileDataset):
        self.ds = dicom
        self.pixel_data_original = dicom.pixel_array
        self.pixel_data_modified_16_bits = np.zeros(dicom.pixel_array.shape)
        self.pixel_data_modified_8_bits = np.zeros(dicom.pixel_array.shape)
        self.min_pixel_value = dicom.pixel_array.min()
        self.max_pixel_value = dicom.pixel_array.max()
        self.window_center = dicom.WindowCenter
        self.window_width = dicom.WindowWidth
        self.rescale_slope = float(dicom.RescaleSlope)
        self.rescale_intercept = float(dicom.RescaleIntercept)
        self.VOI_LUT_function = getattr(dicom, 'VOILUTFunction', None)
        self.photometric_interpretation = dicom.PhotometricInterpretation

    def get_ds(self):
        return self.ds

    def get_pixel_data_original(self):
        return self.pixel_data_original

    def get_pixel_data_modified_16_bits(self):
        return self.pixel_data_modified_16_bits

    def set_pixel_data_modified_16_bits(self, pixel_data_modified_16_bits):
        self.pixel_data_modified_16_bits = pixel_data_modified_16_bits

    def get_pixel_data_modified_8_bits(self):
        return self.pixel_data_modified_8_bits

    def set_pixel_data_modified_8_bits(self, pixel_data_modified_8_bits):
        self.pixel_data_modified_8_bits = pixel_data_modified_8_bits

    def get_min_pixel_value(self):
        return self.min_pixel_value

    def get_max_pixel_value(self):
        return self.max_pixel_value

    def get_window_center(self):
        return self.window_center

    def get_window_width(self):
        return self.window_width

    def get_rescale_slope(self):
        return self.rescale_slope

    def get_rescale_intercept(self):
        return self.rescale_intercept

    def get_voi_lut_function(self):
        return self.VOI_LUT_function

    def get_photometric_interpretation(self):
        return self.photometric_interpretation
