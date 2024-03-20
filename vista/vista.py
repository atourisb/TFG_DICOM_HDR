import matplotlib.pyplot as plt
Aimport gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

# Vista

class Vista(Gtk.Window):

    def __init__(self):
        super().__init__(title="Hello World")

        self.button = Gtk.Button(label="Mostrar Imagenes")
        self.button.connect("clicked", self.on_button_clicked)
        self.add(self.button)



    def mostrar_cantidad_de_la_lista(self, lista):
        print(len(lista))

    # Método para mostrar la ventana
    # def mostrar_ventana(self):
    #     self.show_all()
    #     Gtk.main()

    def mostrar_dicom_original_y_dicom_transformado(self, dicom):

        plt.figure()
        plt.imshow(dicom.pixel_data_original, cmap='gray')
        plt.figure()
        plt.imshow(dicom.pixel_data_modified, cmap='gray')
        plt.show()

    def on_button_clicked(self, widget):
        self.mostrar_dicom_original_y_dicom_transformado()



    # def mostrar_ejemplo(self):
    #     win = Gtk.Window()
    #     win.connect("destroy", Gtk.main_quit)
    #     win.show_all()
    #     Gtk.main()