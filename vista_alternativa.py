from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg as FigureCanvas
#from modelo.dicom_data import DicomData
from vista.vista_data import ModeloVista
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
import glob
import os
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from matplotlib.backends.backend_gtk3 import (
    NavigationToolbar2GTK3 as NavigationToolbar)


# Vista

class Vistaesperimento(Gtk.Window):

    def __init__(self, controlador):

        self.start_window_center = None
        self.start_window_width = None
        self.start_y = None
        self.start_x = None

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
        self.fig8, axs = plt.subplots(nrows=1, ncols=2, figsize=(10, 6), sharex=True, sharey=True, frameon=False)
        self.fig8.tight_layout()
        self.fig8.subplots_adjust(wspace=0, hspace=0, left=0, right=1, bottom=0, top=1)

        self.ax8 = axs[0]
        self.ax8.axis('off')
        self.ax16 = axs[1]
        self.ax16.axis('off')

        #Valores de zoom y posicion de la imagen
        self.xlim8 = None
        self.ylim8 = None
        self.xlim16 = None
        self.ylim16 = None

        self.canvas8 = FigureCanvas(self.fig8)

        self.toolbar = NavigationToolbar(self.canvas8, self)
        self.box_botones.pack_start(self.toolbar, False, False, 10)

        # Agregar el lienzo al viewport
        self.viewport.add(self.canvas8)

        self.scrolledwindow.add(self.viewport)
        self.vadjustment1 = self.viewport.get_vadjustment()
        self.hadjustment1 = self.viewport.get_hadjustment()
        self.box2.pack_start(self.scrolledwindow, True, True, 0)

        # --------------------------------------------- Segunda imagen ------------------------------------------------#
        self.imagecv_16_bits = None
        self.imagecv_16_bits_dsplayed = None

        #----- --------------------- Conexiones de los botones con las diferentes funciones ---------------------------#
        self.connect("destroy", Gtk.main_quit)

        # Conexiones para realizar el scroll el panning en la imagen y el zoom
        self.add_events(Gdk.EventMask.SCROLL_MASK)

        # Viewport donde estan las figuras donde representamos al imagen
        self.viewport.set_events(Gdk.EventMask.BUTTON_PRESS_MASK | Gdk.EventMask.POINTER_MOTION_MASK)

        # Variables para rastrear si el botón del ratón está presionado
        self.mouse_pressed = False
        #Para reconocer el movimiento en vertical y que funque el cambio de window center
        self.viewport.connect("motion-notify-event", self.on_motion_notify_center)
        self.viewport.connect("motion-notify-event", self.on_motion_notify_width)
        self.viewport.connect("button-press-event", self.on_button_press)
        self.viewport.connect("button-release-event", self.on_button_release)

        # Configurar eventos de teclado
        self.connect("key-press-event", self.on_key_press_z_zoom)
        self.connect("key-press-event", self.on_key_press_x_paning)

        # Evento zoom con el raton secundario
        self.connect("button-press-event", self.on_button_press_zoom_mouse)
        self.connect("button-release-event", self.on_button_release_zoom_mouse)
        self.click_derecho_pulsado = False

        # Evento panning con el raton secundario
        self.connect("button-press-event", self.on_button_press_panning_mouse)
        self.connect("button-release-event", self.on_button_release_panning_mouse)

        # Evento windowing con el raton secundario
        self.connect("button-press-event", self.on_button_press_windowing_mouse)
        self.connect("button-release-event", self.on_button_release_windowing_mouse)

        # Boton primario de raton para poder hacer zoom y asi
        self.add_events(Gdk.EventMask.SCROLL_MASK)

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

#-------------------------------------------- METODOS DE LA NUEVA VISTA -----------------------------------------------#

#-------------------------------------------- METODOS DE CARGA DE IMAGENES --------------------------------------------#

    def show_image_8_bits(self, image):
        self.ax8.clear()
        self.ax8.imshow(image, cmap='gray')
        self.ax8.set_title("Version 8 Bits")
        self.ax8.axis('off')
        self.canvas8.draw()

    def show_image_8_bits_mantiene_zoom(self, image, xlim8, ylim8):
        self.ax8.clear()
        self.ax8.imshow(image, cmap='gray')
        self.ax8.set_title("Version 8 Bits")
        self.ax8.axis('off')
        self.ax8.set_xlim(xlim8)
        self.ax8.set_ylim(ylim8)
        self.canvas8.draw()

    def show_image_16_bits(self, image):
        print(image)
        self.ax16.clear()
        self.ax16.imshow(image, cmap='gray')
        self.ax16.set_title("Version 16 Bits")
        self.ax16.axis('off')
        self.canvas8.draw()

    def show_image_16_bits_mantiene_zoom(self, image, xlim16, ylim16):
        print(image)
        self.ax16.clear()
        self.ax16.imshow(image, cmap='gray')
        self.ax16.set_title("Version 16 Bits")
        self.ax16.axis('off')
        self.ax16.set_xlim(xlim16)
        self.ax16.set_ylim(ylim16)
        self.canvas8.draw()

    #Creamos el objeto del modelo vist_data llamando a los metodos del controlador
    def crear_vista_data(self, path):

        # Osea elegimos un dicom, la vista manda la orden al controlador de convertir el dicom a .tiff pero obtenemos 2 uno de 8 y otro de 16
        # Despues de esto la vista procede a cargarlo y obtener las modificaciones necesarias para poder

        #La tupla contiene los paths de la imagen en 8 bits y en 16 bits para poder representar y crear el objeto vista_data
        tuple = self.controlador.transformacion_y_guardado_vista(path)

        vista_data = ModeloVista(tuple[0], tuple[1])
        self.lista_imagenes.append(vista_data)

        return vista_data

    # Metodos para cargar imagenes y carpetas que contengan imagenes

    # Metodo que nos permite cargar una carpeta y todas las imagenes a la vez que contenga
    def load_image_vista_data(self, vista_data):
        try:
            self.imagecv_8_bits = vista_data.get_image_numpy_8_bits()
            self.imagecv_8_bits_dsplayed = vista_data.get_image_numpy_8_bits()
            #self.image_8_bits = vista_data.get_image_8_bits()

            self.imagecv_16_bits = vista_data.get_image_numpy_16_bits()
            self.imagecv_16_bits_dsplayed = vista_data.get_image_numpy_16_bits()
            #self.image_16_bits = vista_data.get_image_16_bits()

            print("Numero elementos de la lista: ", len(self.lista_imagenes))
            print("Posicion de la Lista: ", self.posicion_lista)

            self.show_image_8_bits(self.imagecv_8_bits_dsplayed)
            self.show_image_16_bits(self.imagecv_16_bits_dsplayed)

            print(self.imagecv_16_bits_dsplayed)

        except Exception as e:
            print("Error al cargar la imagen:", e)

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

        elif response == Gtk.ResponseType.CANCEL:
            print("Cancel clicked")

        dialog.destroy()

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

            for f in glob.glob(path):
                print(f)
                print(f.split("/")[-1])
                self.crear_vista_data(f)

            self.posicion_lista = len(self.lista_imagenes) - 1
            self.load_image_vista_data(self.lista_imagenes[self.posicion_lista])
            self.show_image_8_bits(self.imagecv_8_bits_dsplayed)
            self.show_image_16_bits(self.imagecv_16_bits_dsplayed)

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

    def apply_windowing_8_bits(self, image, window_center, window_width):
        # Calcular los límites del rango de píxeles
        min_value = window_center - (window_width / 2)
        max_value = window_center + (window_width / 2)

        print("movido8")
        # Aplicar windowing a la imagen
        windowed_image = np.clip((image - min_value) / window_width * 255, 0, 255).astype(np.uint8)
        return windowed_image

    def apply_windowing_16_bits(self, image, window_center, window_width):
        # Calcular los límites del rango de píxeles
        min_value = window_center - (window_width / 2)
        max_value = window_center + (window_width / 2)

        print("movido16")
        # Aplicar windowing a la imagen
        windowed_image = np.clip((image - min_value) / window_width * 65535, 0, 65535).astype(np.uint16)
        return windowed_image

#----------------------------------------------------------------------------------------------------------------------#

#-------------------------------------------- METODOS DE PARA LOS BOTONES ---------------------------------------------#

    def on_button_anterior_clicked(self, widget):
        self.ax8.clear()
        self.ax16.clear()
        self.ax8.axis('off')
        self.ax16.axis('off')
        self.canvas8.draw()

        self.windowing_center_8_bits = 127
        self.windowing_width_8_bits = 255
        self.windowing_center_16_bits = 32767
        self.windowing_width_16_bits = 65535

        if len(self.lista_imagenes) == 0:
            raise Exception("La lista esta vacia")

        if (self.posicion_lista-1) < 0:
            self.posicion_lista = len(self.lista_imagenes)-1
        else:
            self.posicion_lista -= 1

        self.load_image_vista_data(self.lista_imagenes[self.posicion_lista])

        self.show_image_8_bits(self.imagecv_8_bits_dsplayed)
        self.show_image_16_bits(self.imagecv_16_bits_dsplayed)

    def on_key_press_z_zoom(self, widget, event):
        if event.keyval == Gdk.KEY_z:
            print("ENTRAMOS EN EL ZOOM")
            self.toolbar.zoom()

    def on_key_press_x_paning(self, widget, event):
        if event.keyval == Gdk.KEY_x:
            print("ENTRAMOS EN EL PANNING")
            self.toolbar.pan()

    def on_button_press_windowing_mouse(self, widget, event):
        if event.button == Gdk.BUTTON_SECONDARY:
            print("ENTRAMOS EN EL WINDOWING")
            self.value_windowing_active = True

    def on_button_release_windowing_mouse(self, widget, event):
        if event.button == Gdk.BUTTON_SECONDARY:
            print("SALIMOS EN EL WINDOWING")
            self.value_windowing_active = False

    # --------------- PANNING RATON EVENTOS RATON ---------------
    def on_button_press_panning_mouse(self, widget, event):
        # BOTON ANTERIOR DEL RATON
        if event.button == 8:
            print("ENTRAMOS EN EL PANNING")
            self.panning = False
            self.toolbar.pan()

    def on_button_release_panning_mouse(self, widget, event):
        # BOTON ANTERIOR DEL RATON
        #if event.button == Gdk.BUTTON_SECONDARY and event.button == Gdk.BUTTON_PRIMARY:
        if event.button == 8:
            print("SALIMOS EN EL PANNING")
            self.panning = False
            self.toolbar.pan()

    def on_button_press_zoom_mouse(self, widget, event):
        # BOTON SIGUIENTE DEL RATON
        if event.button == 9:
            print("ENTRAMOS EN EL ZOOM")
            self.toolbar.zoom()


    def on_button_release_zoom_mouse(self, widget, event):
        # BOTON SIGUIENTE DEL RATON
        if event.button == 9:
            print("ENTRAMOS EN EL ZOOM")
            self.toolbar.zoom()

    def on_button_siguiente_clicked(self, widget):

        self.windowing_center_8_bits = 127
        self.windowing_width_8_bits = 255
        self.windowing_center_16_bits = 32767
        self.windowing_width_16_bits = 65535

        if len(self.lista_imagenes) == 0:
            raise Exception("La lista esta vacia")

        if (self.posicion_lista+1) > (len(self.lista_imagenes)-1):
            self.posicion_lista = 0
        else:
            self.posicion_lista += 1

        self.load_image_vista_data(self.lista_imagenes[self.posicion_lista])
        self.show_image_8_bits(self.imagecv_8_bits_dsplayed)
        self.show_image_16_bits(self.imagecv_16_bits_dsplayed)

    def on_button_delete_foto_actual_clicked(self, widget):

        self.windowing_center_8_bits = 127
        self.windowing_width_8_bits = 255
        self.windowing_center_16_bits = 32767
        self.windowing_width_16_bits = 65535

        if len(self.lista_imagenes) == 0:
            raise Exception("La lista esta vacia")

        if self.posicion_lista < len(self.lista_imagenes):
            del self.lista_imagenes[self.posicion_lista]

            # Verificar si la lista tiene elementos después de borrar
            if self.lista_imagenes:
                # Ajustar la posición si es necesario
                if self.posicion_lista >= len(self.lista_imagenes):
                    self.posicion_lista -= 1

                # Mostrar la siguiente foto
                self.load_image_vista_data(self.lista_imagenes[self.posicion_lista])
                self.show_image_8_bits(self.imagecv_8_bits_dsplayed)
                self.show_image_16_bits(self.imagecv_16_bits_dsplayed)
            else:
                self.ax8.clear()
                self.ax16.clear()
                self.ax8.axis('off')
                self.ax16.axis('off')
                self.canvas8.draw()
                self.button3.hide()
                self.button4.hide()
                self.button5.hide()
                self.button_delete.hide()

        return True

    def on_button_delete_lista_clicked(self, widget):
        if len(self.lista_imagenes) == 0:
            raise Exception("La lista esta vacia")

        self.windowing_center_8_bits = 127
        self.windowing_width_8_bits = 255
        self.windowing_center_16_bits = 32767
        self.windowing_width_16_bits = 65535

        self.lista_imagenes.clear()
        self.posicion_lista = 0
        self.ax8.clear()
        self.ax16.clear()
        self.ax8.axis('off')
        self.ax16.axis('off')
        self.canvas8.draw()

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
        print(self.windowing_center_8_bits)
        print(self.windowing_width_8_bits)

        # Aplicar windowing a la imagen cargada
        if hasattr(self, 'imagecv_8_bits'):
            print("entra")
            self.imagecv_8_bits_dsplayed = self.apply_windowing_8_bits(self.imagecv_8_bits, self.windowing_center_8_bits, self.windowing_width_8_bits)

            self.xlim8 = self.ax8.get_xlim()
            self.ylim8 = self.ax8.get_ylim()
            self.show_image_8_bits_mantiene_zoom(self.imagecv_8_bits_dsplayed, self.xlim8, self.ylim8)

        print("LLEGA AQUI ESPROPIESE apply_windowing_viewport_8_bits")

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
        if hasattr(self, 'imagecv_16_bits'):
            print("entra")
            self.imagecv_16_bits_dsplayed = self.apply_windowing_16_bits(self.imagecv_16_bits, window_center, window_width)

            self.xlim16 = self.ax16.get_xlim()
            self.ylim16 = self.ax16.get_ylim()

            self.show_image_16_bits_mantiene_zoom(self.imagecv_16_bits_dsplayed, self.xlim16, self.ylim16)

        self.sincronizar_valores_8_bits()

        # Reiniciar el ID del temporizador
        self.timeout_id = None

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

    def on_motion_notify_center(self, widget, event):
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
                fraction = 4  # Fracción del movimiento del ratón que se aplicará al cambio en window_width
                delta_window_width = int(delta_x * fraction)

                # Calcula el nuevo valor de window_center basado en el cambio en el eje X
                self.windowing_width_16_bits = self.start_window_width - delta_window_width

                # Asegúrate de que el valor de window_center esté dentro del rango válido (0 a 65535)
                self.windowing_width_16_bits = max(0, min(65535, self.windowing_width_16_bits))

                print("New window_width:", self.windowing_width_16_bits)

