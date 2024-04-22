import matplotlib.pyplot as plt
from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg as FigureCanvas
#from modelo.dicom_data import DicomData
from vista.vista_data import ModeloVista
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf, Gdk, GLib
import glob
import os
import numpy as np
import cv2
import matplotlib.pyplot as plt
from pathlib import Path
from matplotlib.backends.backend_gtk3 import (
    NavigationToolbar2GTK3 as NavigationToolbar)


# Vista

class Vistaesperimento(Gtk.Window):

    def __init__(self, controlador):

        self.controlador = controlador

        # Creacion de la ventana principal de la vista

        # Lista que contendra las imagenes que carguemos, si elegimos cargar
        self.lista_imagenes = []
        Gtk.Window.__init__(self, title="Aplicacion")
        self.set_default_size(1600, 1000)
        self.set_border_width(20)

        # Crear una caja principal en la crearemos dos cajas a su vez dentro cada una para diferentes widgets
        self.box_principal = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.add(self.box_principal)  # Agregar la caja a la ventana
        self.box_principal.set_homogeneous(False)
        self.box_principal.set_spacing(20)

        # Crear una caja en sentido horizontal para los botones
        self.box_botones = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.box_principal.pack_start(self.box_botones, False, False, 0)
        self.box_botones.set_homogeneous(True)
        self.box_botones.set_spacing(0)

        #------------------------------------- Anhadimos los diferentes botones ---------------------------------------#

        # Crear una barra de desplazamiento para window_center
        self.scale_center = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL)
        self.scale_center.set_range(0, 255)
        self.scale_center.set_value(127)  # Valor inicial
        self.scale_center.set_draw_value(False)
        self.scale_center.connect("value-changed", self.on_scale_changed_8_bits)
        self.box_botones.pack_start(self.scale_center, True, True, 0)

        # Crear una barra de desplazamiento para window_width
        self.scale_width = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL)
        self.scale_width.set_range(0, 255)
        self.scale_width.set_value(255)  # Valor inicial
        self.scale_width.set_draw_value(False)
        self.scale_width.connect("value-changed", self.on_scale_changed_8_bits)
        self.box_botones.pack_start(self.scale_width, True, True, 0)

        self.scale_center_16_bits = 32767
        self.scale_width_16_bits = 65535

        self.windowing_center_8_bits = 127
        self.windowing_width_8_bits = 255
        self.windowing_center_16_bits = 32767
        self.windowing_width_16_bits = 65535

        # Boton para cargar una imagen
        self.button1 = Gtk.Button(label="Elegir Fichero")
        self.button1.connect("clicked", self.on_file_clicked)
        self.box_botones.pack_start(self.button1, False, False, 10)

        # Boton para cargar una carpeta con multiples imagenes, podremos pasar a la siguiente foto o a la anterior
        self.button2 = Gtk.Button(label="Elegir Carpeta")
        self.button2.connect("clicked", self.on_folder_clicked)
        self.box_botones.pack_start(self.button2, False, False, 10)

        # Este boton y el siguiente nos permite cambiar entre imagenes ya cargadas
        self.button3 = Gtk.Button(label="Anterior Foto")
        self.button3.connect("clicked", self.on_button_anterior_clicked)
        self.button3.hide()
        self.box_botones.pack_start(self.button3, False, False, 10)

        self.button5 = Gtk.Button(label="Siguiente Foto")
        self.button5.connect("clicked", self.on_button_siguiente_clicked)
        self.button5.hide()
        self.box_botones.pack_start(self.button5, False, False, 10)

        # Boton para eliminar la imagen que se esta representando en la aplicacion
        self.button4 = Gtk.Button(label="Eliminar Foto Actual")
        self.button4.connect("clicked", self.on_button_delete_foto_actual_clicked)
        self.button4.hide()
        self.box_botones.pack_start(self.button4, False, False, 10)

        # CheckBox para activar y desactivar el windowing
        self.check_button = Gtk.CheckButton(label="Activar Windowing")
        self.check_button.connect("toggled", self.on_button_toggled)
        self.box_botones.pack_start(self.check_button, False, False, 10)
        self.value_windowing_active = False

        # Boton que elimina todas las imagenes que han sido cargadas
        self.button_delete = Gtk.Button()
        self.button_delete.connect("clicked", self.on_button_delete_lista_clicked)
        self.button_delete.hide()
        self.button_delete.set_image(Gtk.Image.new_from_icon_name("user-trash-symbolic", Gtk.IconSize.BUTTON))
        self.box_botones.pack_start(self.button_delete, False, False, 10)

        # ----------------------------------------- Anhadimos las imagenes --------------------------------------------#

        # Esta parte de la vista se agregaran los widgets necesarios para poder representar las imagenes

        # Crear una caja para visualizar la imagen
        self.box2 = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.box_principal.pack_start(self.box2, True, True, 0)
        self.box2.set_homogeneous(True)
        self.box2.set_spacing(0)

        # --------------------------------------------- Primera imagen ------------------------------------------------#

        self.imagecv_8_bits = None
        self.imagecv_8_bits_dsplayed = None

        # Crear el widget para representar la imagen
        self.scrolledwindow = Gtk.ScrolledWindow()  # added
        self.viewport = Gtk.Viewport()  # added

        # Agregacion para el canvas
        #self.fig8 = plt.figure()
        self.fig8, axs = plt.subplots(nrows=1, ncols=2, figsize=(10, 6), sharex=True, sharey=True, frameon=False)
        self.fig8.tight_layout()
        self.fig8.subplots_adjust(wspace=0, hspace=0, left=0, right=1, bottom=0, top=1)
        # self.fig8.subplots_adjust(bottom=0)
        # self.fig8.subplots_adjust(top=0.00001)  # This value should be very small so that marginal axes of subplot would not overlay on the main figure
        # self.fig8.subplots_adjust(right=1)
        # self.fig8.subplots_adjust(left=0)

        self.ax8 = axs[0]
        #self.ax8.autoscale(enable=True)
        self.ax8.axis('off')
        self.ax16 = axs[1]
        #self.ax16.autoscale(enable=True)
        self.ax16.axis('off')

        self.canvas8 = FigureCanvas(self.fig8)

        self.toolbar = NavigationToolbar(self.canvas8, self)
        self.box_botones.pack_start(self.toolbar, False, False, 10)

        # Agregar el lienzo al viewport
        self.viewport.add(self.canvas8)

        # Crear la barra de herramientas de navegación
        #toolbar8 = NavigationToolbar(self.canvas8, self.fig8)
        # Agregar la barra de herramientas a la interfaz gráfica
        #self.fig8.addWidget(toolbar8)

        self.scrolledwindow.add(self.viewport)
        self.vadjustment1 = self.viewport.get_vadjustment()
        self.hadjustment1 = self.viewport.get_hadjustment()
        self.box2.pack_start(self.scrolledwindow, True, True, 0)

        # --------------------------------------------- Segunda imagen ------------------------------------------------#
        self.imagecv_16_bits = None
        self.imagecv_16_bits_dsplayed = None

        # Crear el widget para representar la imagen
        self.scrolledwindow2 = Gtk.ScrolledWindow()  # added
        self.viewport2 = Gtk.Viewport()  # added

        #Agregacion para el canvas
        self.fig16 = plt.figure()
        self.canvas16 = FigureCanvas(self.fig16)

        # Agregar el lienzo al viewport
        self.viewport2.add(self.canvas16)

        # Crear la barra de herramientas de navegación
        #toolbar16 = NavigationToolbar(self.canvas16, self.fig16)
        # Agregar la barra de herramientas a la interfaz gráfica
        #self.fig16.addWidget(toolbar16)

        self.scrolledwindow2.add(self.viewport2)
        self.vadjustment2 = self.viewport2.get_vadjustment()
        self.hadjustment2 = self.viewport2.get_hadjustment()
        #self.box2.pack_start(self.scrolledwindow2, True, True, 0)

        #----- --------------------- Conexiones de los botones con las diferentes funciones ---------------------------#
        self.connect("destroy", Gtk.main_quit)

        # Conexiones para realizar el scroll el panning en la imagen y el zoom
        #Mirar cual es cual
        self.add_events(Gdk.EventMask.SCROLL_MASK)

        # No se que es tengo que mirar
        self.viewport.set_events(Gdk.EventMask.BUTTON_PRESS_MASK | Gdk.EventMask.POINTER_MOTION_MASK)
        self.viewport2.set_events(Gdk.EventMask.BUTTON_PRESS_MASK | Gdk.EventMask.POINTER_MOTION_MASK)

        # Variables para rastrear si el botón del ratón está presionado
        self.mouse_pressed = False
        #Para reconocer el movimiento en vertical y que funque el cambio de window center
        self.viewport.connect("motion-notify-event", self.on_motion_notify)
        self.viewport.connect("motion-notify-event", self.on_motion_notify_width)
        self.viewport.connect("button-press-event", self.on_button_press)
        self.viewport.connect("button-release-event", self.on_button_release)

        # Factor de zoom inicial
        self.zoom_factor = 1.0
        self.ratio = 3.

        # Posicion inical para mostrar la primera imagen cuando cargamos multiples imagenes
        self.posicion_lista = 0
        self.panning = False

        # Variable utilizada para dormir la funcion que llama las barras de desplazamineto para modificar el
        # width o el center de la imagen
        self.timeout_id = None

        # Mostrar todos los elementos de la ventana
        self.show_all()

        # Ocultamos los botones que no se utilizan hasta que cargamos alguna imagen en la aplicacion
        self.button3.hide()
        self.button4.hide()
        self.button5.hide()
        self.button_delete.hide()

        # Mirar lo que hice mal de la imagen i la imagencv y checkear que este todo correcto


#utilizar el viewport y el codigo del panning para mover de alguna manera el windowing center y el width center vertical y el width en horizontal de esa manera
# se podra llamar a la funcion que cambie la imagen

#-------------------------------------------- METODOS DE LA NUEVA VISTA -----------------------------------------------#

#-------------------------------------------- METODOS DE CARGA DE IMAGENES --------------------------------------------#

    def show_image_8_bits(self, image):
        self.ax8.clear()
        self.ax8.imshow(image, cmap='gray')
        self.ax8.set_title("Version 8 Bits")
        #self.ax8.savefig(image, bbox_inches='tight', transparent=True, pad_inches=0)
        self.ax8.axis('off')
        self.canvas8.draw()

    def show_image_8_bits_mantiene_zoom(self, image, xlim8, ylim8):
        self.ax8.clear()
        self.ax8.imshow(image, cmap='gray')
        #self.ax8.savefig(image, bbox_inches='tight', transparent=True, pad_inches=0)
        self.ax8.axis('off')
        self.ax8.set_xlim(xlim8)
        self.ax8.set_ylim(ylim8)
        self.canvas8.draw()

    def show_image_16_bits(self, image):
        print(image)
        self.ax16.clear()
        self.ax16.imshow(image, cmap='gray')
        #self.ax16.savefig(image, bbox_inches='tight', transparent=True, pad_inches=0)
        self.ax16.axis('off')
        self.canvas16.draw()

    def show_image_16_bits_mantiene_zoom(self, image, xlim16, ylim16):
        print(image)
        self.ax16.clear()
        self.ax16.imshow(image, cmap='gray')
        #self.ax16.savefig(image, bbox_inches='tight', transparent=True, pad_inches=0)
        self.ax16.axis('off')
        self.ax16.set_xlim(xlim16)
        self.ax16.set_ylim(ylim16)
        self.canvas16.draw()

    #Creamos el objeto del modelo vist_data llamando a los metodos del controlador
    def crear_vista_data(self, path):

        # Osea elegimos un dicom, la vista manda la orden al controlador de convertir el dicom a .tiff pero obtenemos 2 uno de 8 y otro de 16
        # Despues de esto la vista procede a cargarlo y obtener las modificaciones necesarias para poder

        #La tupla contiene los paths de la imagen en 8 bits y en 16 bits para poder representar y crear el objeto vista_data
        tuple = self.controlador.transformacion_y_guardado_vista(path)

        vista_data = ModeloVista(tuple[0], tuple[1])
        self.lista_imagenes.append(vista_data)

        return vista_data

    def queue_redraw(self):
        # Queue a redraw of the window
        Gtk.Window.queue_draw(self)
        #return False  # Remove the callback after the first redraw

    # Metodos para cargar imagenes y carpetas que contengan imagenes

    # Metodo que nos permite cargar una carpeta y todas las imagenes a la vez que contenga
    def load_image_vista_data(self, vista_data):
        try:
            self.imagecv_8_bits = vista_data.get_image_numpy_8_bits()
            self.imagecv_8_bits_dsplayed = vista_data.get_image_numpy_8_bits()
            self.image_8_bits = vista_data.get_image_8_bits()

            self.imagecv_16_bits = vista_data.get_image_numpy_16_bits()
            self.imagecv_16_bits_dsplayed = vista_data.get_image_numpy_16_bits()
            self.image_16_bits = vista_data.get_image_16_bits()

            print("Numero elementos de la lista: ", len(self.lista_imagenes))
            print("Posicion de la Lista: ", self.posicion_lista)

            #Lo aplica en ambas imagenes
            #self.scale_image()

            #self.viewport.set_size_request(self.displayed_pixbuf_8_bits.get_width(), self.displayed_pixbuf_8_bits.get_height())
            # plt.imshow(self.image_8_bits, cmap='gray')  # Mostrar la imagen en el lienzo
            # Actualizar la visualización
            # self.canvas8.draw()

            #self.ax8 = self.fig8.add_subplot(211)

            # COMENTARIO PARECE QUE SI NO HACEMOS AQUI EL SHOW FUNCIONA BIEN
            self.show_image_8_bits(self.imagecv_8_bits_dsplayed)

            #self.viewport.add(self.image_8_bits)
            #self.viewport.show_all()

            #self.viewport2.set_size_request(self.displayed_pixbuf_16_bits.get_width(), self.displayed_pixbuf_16_bits.get_height())
            # plt.imshow(self.image_16_bits, cmap='gray')  # Mostrar la imagen en el lienzo
            # Actualizar la visualización
            # self.canvas16.draw()
            #self.ax16 = self.fig8.add_subplot(212)

            #COMENTARIO PARECE QUE SI NO HACEMOS AQUI EL SHOW FUNCIONA BIEN
            self.show_image_16_bits(self.imagecv_16_bits_dsplayed)

            # while Gtk.events_pending():
            #     Gtk.main_iteration_do()

            #self.canvas8.queue_draw()

            # self.fullscreen()
            # self.unfullscreen()
            # self.resize(1600, 1000)

            #width, height = self.get_size()
            #self.resize(width, height)

            # Schedule the redraw callback using GLib.idle_add()
            #GLib.idle_add(self.viewport.queue_draw(), Gtk.Window)

            print(self.imagecv_16_bits_dsplayed)

            #self.viewport2.add(self.image_16_bits)
            #self.viewport2.show_all()

        except Exception as e:
            print("Error al cargar la imagen:", e)

    # Funcion usada
    def scale_image(self):
        # Obtener las dimensiones de las imágenes originales
        height_8, width_8 = self.imagecv_8_bits.shape[:2]
        height_16, width_16 = self.imagecv_16_bits.shape[:2]

        # Escalar las imágenes utilizando Matplotlib
        scaled_image_8 = cv2.resize(self.imagecv_8_bits, (int(width_8 * self.ratio), int(height_8 * self.ratio)))
        scaled_image_16 = cv2.resize(self.imagecv_16_bits, (int(width_16 * self.ratio), int(height_16 * self.ratio)))

        # Limpiar las figuras existentes
        self.fig8.clear()
        self.fig16.clear()

        # Mostrar las imágenes escaladas en las figuras utilizando Matplotlib
        self.ax8 = self.fig8.add_subplot(111)
        self.ax8.imshow(scaled_image_8, cmap='gray', extent=[0, width_8, 0, height_8])
        self.ax8.axis('off')

        self.ax16 = self.fig16.add_subplot(111)
        self.ax16.imshow(scaled_image_16, cmap='gray', extent=[0, width_16, 0, height_16])
        self.ax16.axis('off')

        # Actualizar las visualizaciones de las figuras
        self.canvas8.draw()
        self.canvas16.draw()

#----------------------------------------------------------------------------------------------------------------------#

#--------------------------------------- METODOS DE PARA LOS BOTONES DE CARGA -----------------------------------------#

    def add_filters(self, dialog):
        filter_any = Gtk.FileFilter()
        filter_any.set_name("Any files")
        filter_any.add_pattern("*")
        dialog.add_filter(filter_any)

        filter_text = Gtk.FileFilter()
        filter_text.set_name("Text files")
        filter_text.add_mime_type("text/plain")
        dialog.add_filter(filter_text)

        filter_py = Gtk.FileFilter()
        filter_py.set_name("Python files")
        filter_py.add_mime_type("text/x-python")
        dialog.add_filter(filter_py)

    # METODO DEL BOTON PARA CARGAR UNA SOLA IMAGEN
    def on_file_clicked(self, widget):
        dialog = Gtk.FileChooserDialog(
            title="Please choose a file", parent=self, action=Gtk.FileChooserAction.OPEN
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL,
            Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN,
            Gtk.ResponseType.OK,
        )

        self.add_filters(dialog)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            print("Open clicked")
            print("File selected: " + dialog.get_filename())

            vista_data = self.crear_vista_data(dialog.get_filename())

            self.load_image_vista_data(vista_data)
            self.show_image_8_bits(self.imagecv_8_bits_dsplayed)
            self.show_image_16_bits(self.imagecv_16_bits_dsplayed)
            #self.viewport.queue_draw()
            self.viewport.draw()

        elif response == Gtk.ResponseType.CANCEL:
            print("Cancel clicked")

        dialog.destroy()

    # AUXILIAR CARGA MULTIPLE IMAGENES
    def cargar_image_multiple_lista(self, file_path):
        try:
            objetoFoto = ModeloVista(file_path)
            self.lista_imagenes.append(objetoFoto)

        except Exception as e:
            print("Error al cargar la imagen:", e)

    # METODO DEL BOTON PARA CARGAR UNA CARPETA
    def on_folder_clicked(self, widget):
        dialog = Gtk.FileChooserDialog(
            title="Please choose a folder",
            parent=self,
            action=Gtk.FileChooserAction.SELECT_FOLDER,
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, "Select", Gtk.ResponseType.OK
        )
        dialog.set_default_size(800, 400)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            print("Select clicked")
            print("Folder selected: " + dialog.get_filename())

            path = dialog.get_filename() + ("/*.dcm")
            print(path)

            directorio, patron = os.path.split(path)
            print(directorio)
            directorio = Path(directorio)
            tiff_files = glob.glob(os.path.join(directorio, '*.dcm'))

            if not directorio.exists():
                raise print("funca pochillon no existe directorio")
            elif not tiff_files:
                raise print("Funca pocho no hay dcm")

            # self.print_directory()
            plots = []
            for f in glob.glob(path):
                print(f)
                print(f.split("/")[-1])
                filename = f.split("/")[-1]
                #self.cargar_image_multiple_lista(f)
                self.crear_vista_data(f)

            self.posicion_lista = len(self.lista_imagenes) - 1
            self.load_image_vista_data(self.lista_imagenes[self.posicion_lista])
            self.show_image_8_bits(self.imagecv_8_bits_dsplayed)
            self.show_image_16_bits(self.imagecv_16_bits_dsplayed)
            #self.viewport.queue_draw()

            self.button3.show()
            self.button4.show()
            self.button5.show()
            self.button_delete.show()

            dialog.get_filename()
        elif response == Gtk.ResponseType.CANCEL:
            print("Cancel clicked")
            self.button3.hide()
            self.button4.hide()
            self.button5.hide()
            self.button_delete.hide()

        dialog.destroy()

#----------------------------------------------------------------------------------------------------------------------#

#----------------------------------------------------------------------------------------------------------------------#

#-------------------------------------- METODOS PARA LAS SCROLL BARS WINDOWING ----------------------------------------#

    def on_scale_changed_8_bits(self, scale):

        # Reiniciar el temporizador si ya estaba activo
        if self.timeout_id:
            GLib.source_remove(self.timeout_id)

        # Activar el temporizador para aplicar el windowing después de un breve retraso
        self.timeout_id = GLib.timeout_add(200, self.apply_windowing_delayed_8_bits(scale))

    def apply_windowing_8_bits(self, image, window_center, window_width):
        # Calcular los límites del rango de píxeles
        min_value = window_center - (window_width / 2)
        max_value = window_center + (window_width / 2)

        print("movido8")
        # Aplicar windowing a la imagen
        windowed_image = np.clip((image - min_value) / window_width * 255, 0, 255).astype(np.uint8)
        return windowed_image

    def sincronizar_barras_16_bits(self, scale):
        value = scale.get_value()
        if scale == self.scale_center:
            percentage = value / 255 * 100
            print("Porcentaje de la barra 1:", percentage)
            self.scale_center_16_bits = percentage * 65535 / 100
            self.apply_windowing_delayed_16_bits(round(self.scale_center_16_bits))

        if scale == self.scale_width:
            percentage = value / 255 * 100
            print("Porcentaje de la barra 2:", percentage)
            self.scale_width_16_bits = percentage * 65535 / 100
            self.apply_windowing_delayed_16_bits(round(self.scale_width_16_bits))

    def apply_windowing_delayed_8_bits(self, scale):
        # Obtener los valores de window_center y window_width de las barras de desplazamiento
        window_center = self.scale_center.get_value()
        print(window_center)
        window_width = self.scale_width.get_value()
        print(window_width)

        # Aplicar windowing a la imagen cargada
        if hasattr(self, 'image_8_bits'):
            print("entra")
            self.imagecv_8_bits_dsplayed = self.apply_windowing_8_bits(self.imagecv_8_bits, window_center, window_width)

            #windowed_image_8

            #self.ax8 = self.fig8.add_subplot(111)
            self.show_image_8_bits(self.imagecv_8_bits_dsplayed)


        self.sincronizar_barras_16_bits(scale)

            # Reiniciar el ID del temporizador
        self.timeout_id = None

        # Detener la propagación del evento
        #return False

    def apply_windowing_16_bits(self, image, window_center, window_width):
        # Calcular los límites del rango de píxeles
        min_value = window_center - (window_width / 2)
        max_value = window_center + (window_width / 2)

        print("movido16")
        # Aplicar windowing a la imagen
        windowed_image = np.clip((image - min_value) / window_width * 65535, 0, 65535).astype(np.uint16)
        return windowed_image

    def apply_windowing_delayed_16_bits(self, value):
        # Obtener los valores de window_center y window_width de las barras de desplazamiento
        #self.window_center_16_bits
        print(self.scale_center_16_bits)
        #self.window_width16 = self.scale_width16.get_value()
        print(self.scale_width_16_bits)

        # Aplicar windowing a la imagen cargada
        if hasattr(self, 'image_16_bits'):
            print("entra")
            self.imagecv_16_bits_dsplayed = self.apply_windowing_16_bits(self.imagecv_16_bits, self.scale_center_16_bits, self.scale_width_16_bits)
            #windowed_image_16

            #self.ax16 = self.fig16.add_subplot(222)
            self.show_image_16_bits(self.imagecv_16_bits_dsplayed)

        print("LLEGA AQUI ESPROPIESE")

        # Detener la propagación del evento
        return False


#----------------------------------------------------------------------------------------------------------------------#

#-------------------------------------------- METODOS DE PARA LOS BOTONES ---------------------------------------------#

    def on_button_anterior_clicked(self, widget):

        #Reiniciar el valore de windowing ambos cada vez que se cambia de foto o se elimina una foto
        #Y arreglar el delete que funciona mal
        #Por ultimo limpiar el codigo
        #Quitar de la interfaz los elementos que se usen

        if len(self.lista_imagenes) == 0:
            raise Exception("La lista esta vacia")

        if (self.posicion_lista-1) < 0:
            self.posicion_lista = len(self.lista_imagenes)-1
        else:
            self.posicion_lista -= 1

        # for child in self.viewport.get_children():
        #     self.viewport.remove(child)
        #     for child in self.viewport2.get_children():
        #         self.viewport2.remove(child)

        self.load_image_vista_data(self.lista_imagenes[self.posicion_lista])

        #vista_objeto = self.lista_imagenes[self.posicion_lista]

        self.show_image_8_bits(self.imagecv_8_bits_dsplayed)
        self.show_image_16_bits(self.imagecv_16_bits_dsplayed)

        # self.resize(1919, 1079)
        # self.resize(1920, 1080)
        #self.viewport.queue_draw()
        #self.viewport.queue_draw()
        #self.show_image_8_bits(self.imagecv_8_bits_dsplayed)
        #self.show_image_16_bits(self.imagecv_16_bits_dsplayed)

    def on_button_siguiente_clicked(self, widget):

        if len(self.lista_imagenes) == 0:
            raise Exception("La lista esta vacia")

        if (self.posicion_lista+1) > (len(self.lista_imagenes)-1):
            self.posicion_lista = 0
        else:
            self.posicion_lista += 1

        # for child in self.viewport.get_children():
        #     self.viewport.remove(child)
        # for child in self.viewport2.get_children():
        #     self.viewport2.remove(child)
        self.load_image_vista_data(self.lista_imagenes[self.posicion_lista])
        self.show_image_8_bits(self.imagecv_8_bits_dsplayed)
        self.show_image_16_bits(self.imagecv_16_bits_dsplayed)

        # self.resize(1919, 1079)
        # self.resize(1920, 1080)
        #self.viewport.queue_draw()
        #self.viewport.queue_draw()

    def on_button_delete_foto_actual_clicked(self, widget):
        if len(self.lista_imagenes) == 0:
            raise Exception("La lista esta vacia")

        del self.lista_imagenes[self.posicion_lista]

        if len(self.lista_imagenes)-1 ==  self.posicion_lista:
            self.posicion_lista = self.posicion_lista - 1

        #del self.lista_imagenes[self.posicion_lista]

        # for child in self.viewport.get_children():
        #     self.viewport.remove(child)
        # for child in self.viewport2.get_children():
        #     self.viewport2.remove(child)

        if len(self.lista_imagenes) == 0:
            self.ax8.clear()
            self.ax16.clear()
            self.button3.hide()
            self.button4.hide()
            self.button5.hide()
            self.button_delete.hide()
        else:
            if len(self.lista_imagenes) == 1:
                self.posicion_lista = 0

            print(self.posicion_lista)
            self.load_image_vista_data(self.lista_imagenes[self.posicion_lista])
            self.show_image_8_bits(self.imagecv_8_bits_dsplayed)
            self.show_image_16_bits(self.imagecv_16_bits_dsplayed)

    #Hacer boton de borrar la lista y boton de borrar una foto
    def on_button_delete_lista_clicked(self, widget):
        if len(self.lista_imagenes) == 0:
            raise Exception("La lista esta vacia")

        # for child in self.viewport.get_children():
        #     self.viewport.remove(child)
        # for child in self.viewport2.get_children():
        #     self.viewport2.remove(child)
        self.lista_imagenes.clear()

        self.button3.hide()
        self.button4.hide()
        self.button5.hide()
        self.button_delete.hide()
        return True

    def on_button_toggled(self, button):
        if button.get_active():
            self.value_windowing_active = True
        else:
            self.value_windowing_active = False
        print("CheckButton state is", self.value_windowing_active)

    def apply_windowing_viewport_8_bits(self):
        # Obtener los valores de window_center y window_width de las barras de desplazamiento
        #self.window_center_16_bits
        print(self.windowing_center_8_bits)
        #self.window_width16 = self.scale_width16.get_value()
        print(self.windowing_width_8_bits)

        # Aplicar windowing a la imagen cargada
        if hasattr(self, 'image_8_bits'):
            print("entra")
            self.imagecv_8_bits_dsplayed = self.apply_windowing_8_bits(self.imagecv_8_bits, self.windowing_center_8_bits, self.windowing_width_8_bits)
            #windowed_image_16

            self.xlim = self.ax8.get_xlim()
            self.ylim = self.ax8.get_ylim()
            #self.ax16 = self.fig16.add_subplot(222)
            self.show_image_8_bits_mantiene_zoom(self.imagecv_8_bits_dsplayed, self.xlim, self.ylim)

        print("LLEGA AQUI ESPROPIESE")

        # Detener la propagación del evento
        return False

    def sincronizar_valores_8_bits(self):
        value_center_16_bits = self.windowing_center_16_bits
        value_width_16_bits = self.windowing_width_16_bits

        percentage = value_center_16_bits / 65535 * 100
        print("Porcentaje de la barra 1:", percentage)
        self.windowing_center_8_bits = round(percentage * 255 / 100)
        self.apply_windowing_viewport_8_bits()

        percentage = value_width_16_bits / 65535 * 100
        print("Porcentaje de la barra 2:", percentage)
        self.windowing_width_8_bits = round(percentage * 255 / 100)
        self.apply_windowing_viewport_8_bits()

    def apply_windowing_viewport_16(self):
        # Obtener los valores de window_center y window_width de las barras de desplazamiento
        window_center = self.windowing_center_16_bits
        print(window_center)
        window_width = self.windowing_width_16_bits
        print(window_width)

        # Aplicar windowing a la imagen cargada
        if hasattr(self, 'image_16_bits'):
            print("entra")
            self.imagecv_16_bits_dsplayed = self.apply_windowing_16_bits(self.imagecv_16_bits, window_center, window_width)

            #windowed_image_8
            self.xlim16 = self.ax16.get_xlim()
            self.ylim16 = self.ax16.get_ylim()

            #self.ax8 = self.fig8.add_subplot(111)
            self.show_image_16_bits_mantiene_zoom(self.imagecv_16_bits_dsplayed, self.xlim16, self.ylim16)

        self.sincronizar_valores_8_bits()

        # self.xlim16 = self.ax16.get_xlim()
        # self.ylim16 = self.ax16.get_ylim()
        #
        # self.ax16.set_xlim(self.xlim16)
        # self.ax16.set_ylim(self.ylim16)
        #
        # self.ax8.set_xlim(self.xlim8)
        # self.ax8.set_ylim(self.ylim8)

        # self.scale_center_16_bits = self.windowing_center_16_bits
        # self.scale_width_16_bits = self.windowing_width_16_bits
        # self.scale_center.set_value(self.windowing_center_8_bits)
        # self.scale_width.set_value(self.windowing_width_8_bits)

            # Reiniciar el ID del temporizador
        self.timeout_id = None

        # Detener la propagación del evento
        return False


    def on_button_press(self, viewport, event):
        if self.value_windowing_active:
            if event.button == Gdk.BUTTON_PRIMARY:  # Botón izquierdo del ratón
                self.start_y = event.y
                self.start_x = event.x
                self.start_window_center = self.windowing_center_16_bits
                self.start_window_width = self.windowing_width_16_bits
                self.mouse_pressed = True

    def on_button_release(self, viewport, event):
        if self.value_windowing_active:
            if event.button == Gdk.BUTTON_PRIMARY:  # Botón izquierdo del ratón
                self.apply_windowing_viewport_16()
                self.mouse_pressed = False

    # def on_mouse_motion(self, viewport, event):
    #     if self.mouse_pressed:
    #         if event.is_hint:
    #             _, x, y, _ = event.window.get_pointer()
    #         else:
    #             x = event.x
    #             y = event.y
    #
    #         # Calcular el nuevo valor de window_center basado en la posición vertical del ratón
    #         # Aquí puedes ajustar la lógica según tus necesidades
    #         window_center = 32767 - (y - 150) * 100
    #         print("Window Center:", window_center)
    #
    #         # Actualizar la imagen con el nuevo window_center
    #         # Aquí llamarías a la función que actualiza la imagen con el nuevo window_center
    #         # Por ahora, simplemente imprimimos el valor

    def on_motion_notify(self, widget, event):
        if self.value_windowing_active:
            if self.mouse_pressed:
                delta_y = self.start_y - event.y  # Calcula el cambio en la posición vertical del ratón

                # Ajusta la velocidad del cambio en función de la distancia recorrida por el ratón
                fraction = 4  # Fracción del movimiento del ratón que se aplicará al cambio en window_center
                delta_window_center = int(delta_y * fraction)

                # Calcula el nuevo valor de window_center basado en el cambio en el eje Y
                self.windowing_center_16_bits = self.start_window_center + delta_window_center

                # Asegúrate de que el valor de window_center esté dentro del rango válido (0 a 65535)
                self.windowing_center_16_bits = max(0, min(65535, self.windowing_center_16_bits))

                print("New window_center:", self.windowing_center_16_bits)

    def on_motion_notify_width(self, widget, event):
        if self.value_windowing_active:
            if self.mouse_pressed:
                delta_x = self.start_x - event.x  # Calcula el cambio en la posición vertical del ratón

                # Ajusta la velocidad del cambio en función de la distancia recorrida por el ratón
                fraction = 4  # Fracción del movimiento del ratón que se aplicará al cambio en window_center
                delta_window_width = int(delta_x * fraction)

                # Calcula el nuevo valor de window_center basado en el cambio en el eje Y
                self.windowing_width_16_bits = self.start_window_width - delta_window_width

                # Asegúrate de que el valor de window_center esté dentro del rango válido (0 a 65535)
                self.windowing_width_16_bits = max(0, min(65535, self.windowing_width_16_bits))

                print("New window_width:", self.windowing_width_16_bits)

    # def on_motion_notify(self, widget, event):
    #     if self.mouse_pressed:
    #         delta_y = self.start_y - event.y  # Calcula el cambio en la posición vertical del ratón
    #
    #         # Calcula el nuevo valor de window_center basado en el cambio en el eje Y
    #         self.scale_center_16_bits = self.scale_center_16_bits + delta_y * 100
    #
    #         # Asegúrate de que el valor de window_center esté dentro del rango válido (0 a 65535)
    #         #self.scale_center_16_bits = max(min(65535, self.scale_center_16_bits), 0)
    #
    #         #self.scale_center_16_bits = 0 if self.scale_center_16_bits < 0 else 65535 if self.scale_center_16_bits > 65535 else self.scale_center_16_bits
    #
    #         # if self.scale_center_16_bits < 0:
    #         #     self.scale_center_16_bits = 0
    #         #     print("POCHO:", self.scale_center_16_bits)
    #         # elif self.scale_center_16_bits > 65535:
    #         #     self.scale_center_16_bits = 65535
    #         #else:
    #             #return self.scale_center_16_bits
    #
    #
    #         print("New window_center:", self.scale_center_16_bits)

#-----------------------------------METODOS DEL MODELO ANTES DE IMPLEMENTAR LA VISTA BUENA-----------------------------#

#-----------------------------------------------------------------------------------------------------------------------

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

#-----------------------------------------------------------------------------------------------------------------------

    # def mostrar_ejemplo(self):
    #     win = Gtk.Window()
    #     win.connect("destroy", Gtk.main_quit)
    #     win.show_all()
    #     Gtk.main()