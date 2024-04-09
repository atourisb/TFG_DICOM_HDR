import cv2
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf, Gdk, GLib

class ModeloVista:

    """Atributos de tipo de dato usado para guardar la info extraida del DICOM"""
    original_pixbuf_8_bits: GdkPixbuf.Pixbuf
    displayed_pixbuf_8_bits: GdkPixbuf.Pixbuf
    image_8_bits: Gtk.Image

    original_pixbuf_16_bits: GdkPixbuf.Pixbuf
    displayed_pixbuf_16_bits: GdkPixbuf.Pixbuf
    image_16_bits: Gtk.Image

    def __init__(self, file_path_8_bits, file_path_16_bits):
        self.imagecv_8_bits = cv2.imread(file_path_8_bits)
        self.original_pixbuf_8_bits = GdkPixbuf.Pixbuf.new_from_file(file_path_8_bits)
        self.displayed_pixbuf_8_bits = GdkPixbuf.Pixbuf.new_from_file(file_path_8_bits)
        self.image_8_bits = Gtk.Image.new_from_pixbuf(self.displayed_pixbuf_8_bits)

        self.imagecv_16_bits = cv2.imread(file_path_16_bits)
        self.original_pixbuf_16_bits = GdkPixbuf.Pixbuf.new_from_file(file_path_16_bits)
        self.displayed_pixbuf_16_bits = GdkPixbuf.Pixbuf.new_from_file(file_path_16_bits)
        self.image_16_bits = Gtk.Image.new_from_pixbuf(self.displayed_pixbuf_16_bits)

    def get_image_numpy_8_bits(self):
        return self.imagecv_8_bits

    def get_original_pixbuf_8_bits(self):
        return self.original_pixbuf_8_bits

    def get_displayed_pixbuf_8_bits(self):
        return self.displayed_pixbuf_8_bits

    def get_image_8_bits(self):
        return self.image_8_bits


    def get_image_numpy_16_bits(self):
        return self.imagecv_16_bits

    def get_original_pixbuf_16_bits(self):
        return self.original_pixbuf_16_bits

    def get_displayed_pixbuf_16_bits(self):
        return self.displayed_pixbuf_16_bits

    def get_image_16_bits(self):
        return self.image_16_bits