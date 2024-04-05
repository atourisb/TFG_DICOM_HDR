import cv2
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf, Gdk, GLib

class ModeloVista:

    """Atributos de tipo de dato usado para guardar la info extraida del DICOM"""
    original_pixbuf: GdkPixbuf.Pixbuf
    displayed_pixbuf: GdkPixbuf.Pixbuf
    image: Gtk.Image

    def __init__(self, file_path):
        self.imagecv = cv2.imread(file_path)
        self.original_pixbuf = GdkPixbuf.Pixbuf.new_from_file(file_path)
        self.displayed_pixbuf = GdkPixbuf.Pixbuf.new_from_file(file_path)
        self.image = Gtk.Image.new_from_pixbuf(self.displayed_pixbuf)

    def get_image_numpy(self):
        return self.imagecv

    def get_original_pixbuf(self):
        return self.original_pixbuf

    def get_displayed_pixbuf(self):
        return self.displayed_pixbuf

    def get_image(self):
        return self.image