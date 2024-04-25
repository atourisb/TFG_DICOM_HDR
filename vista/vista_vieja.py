import matplotlib.pyplot as plt
#from modelo.dicom_data import DicomData
from vista_vieja.vista_data import ModeloVista
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf, Gdk, GLib
import glob
import os
import numpy as np
import cv2
import matplotlib.pyplot as plt
from pathlib import Path

# Vista

class Vista(Gtk.Window):

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

        # Boton que elimina todas las imagenes que han sido cargadas
        self.button_delete = Gtk.Button()
        self.button_delete.connect("clicked", self.on_button_delete_lista_clicked)
        self.button_delete.hide()
        self.button_delete.set_image(Gtk.Image.new_from_icon_name("user-trash-symbolic", Gtk.IconSize.BUTTON))
        self.box_botones.pack_start(self.button_delete, False, False, 10)

        # Crear una barra de desplazamiento para window_center
        self.scale_center = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL)
        self.scale_center.set_range(0, 255)
        self.scale_center.set_value(127)  # Valor inicial
        self.scale_center.set_draw_value(False)
        self.scale_center.connect("value-changed", self.on_scale_changed)
        self.box_botones.pack_start(self.scale_center, True, True, 0)

        # Crear una barra de desplazamiento para window_width
        self.scale_width = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL)
        self.scale_width.set_range(0, 255)
        self.scale_width.set_value(255)  # Valor inicial
        self.scale_width.set_draw_value(False)
        self.scale_width.connect("value-changed", self.on_scale_changed)
        self.box_botones.pack_start(self.scale_width, True, True, 0)

        # ----------------------------------------- Anhadimos las imagenes --------------------------------------------#

        # Esta parte de la vista se agregaran los widgets necesarios para poder representar las imagenes

        # Crear una caja para visualizar la imagen
        self.box2 = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.box_principal.pack_start(self.box2, True, True, 0)
        self.box2.set_homogeneous(True)
        self.box2.set_spacing(0)

        # --------------------------------------------- Primera imagen ------------------------------------------------#

        self.imagecv_8_bits = None
        self.original_pixbuf_8_bits = None
        self.displayed_pixbuf_8_bits = None

        # Crear el widget para representar la imagen
        self.scrolledwindow = Gtk.ScrolledWindow()  # added
        self.viewport = Gtk.Viewport()  # added
        self.scrolledwindow.add(self.viewport)
        self.vadjustment1 = self.viewport.get_vadjustment()
        self.hadjustment1 = self.viewport.get_hadjustment()
        self.box2.pack_start(self.scrolledwindow, True, True, 0)

        # --------------------------------------------- Segunda imagen ------------------------------------------------#
        self.imagecv_16_bits = None
        self.original_pixbuf_16_bits = None
        self.displayed_pixbuf_16_bits = None

        # Crear el widget para representar la imagen
        self.scrolledwindow2 = Gtk.ScrolledWindow()  # added
        self.viewport2 = Gtk.Viewport()  # added
        self.scrolledwindow2.add(self.viewport2)
        self.vadjustment2 = self.viewport2.get_vadjustment()
        self.hadjustment2 = self.viewport2.get_hadjustment()
        self.box2.pack_start(self.scrolledwindow2, True, True, 0)

        #----- --------------------- Conexiones de los botones con las diferentes funciones ---------------------------#
        self.connect("destroy", Gtk.main_quit)

        # Conexiones para realizar el scroll el panning en la imagen y el zoom
        #Mirar cual es cual
        self.viewport.connect("scroll-event", self.on_viewport_scroll_event)
        self.viewport2.connect("scroll-event", self.on_viewport_scroll_event)
        self.connect("scroll-event", self.on_scroll_event_zoom)
        self.add_events(Gdk.EventMask.SCROLL_MASK)
        self.viewport.connect("button-press-event", self.on_viewport_button_press)
        self.viewport.connect("motion-notify-event", self.on_viewport_motion_notify)
        self.viewport2.connect("button-press-event", self.on_viewport_button_press)
        self.viewport2.connect("motion-notify-event", self.on_viewport_motion_notify)

        # Conectar el evento "value-changed" de la barra de desplazamiento del primer ScrolledWindow
        self.vadjustment1.connect("value-changed", self.on_vadjustment1_changed, self.vadjustment2)
        self.hadjustment1.connect("value-changed", self.on_hadjustment1_changed, self.hadjustment2)
        # Conectar el evento "value-changed" de la barra de desplazamiento del segundo ScrolledWindow
        self.vadjustment2.connect("value-changed", self.on_vadjustment1_changed, self.vadjustment1)
        self.hadjustment2.connect("value-changed", self.on_hadjustment1_changed, self.hadjustment1)
        # Esto es para intentar desactivar la sync de las barras anhadidas antes cuando hacemos panning
        self.scrolledwindow.connect("button-press-event", self.on_button_press_event)
        self.scrolledwindow.connect("button-release-event", self.on_button_release_event)

        # No se que es tengo que mirar
        self.viewport.set_events(Gdk.EventMask.BUTTON_PRESS_MASK | Gdk.EventMask.POINTER_MOTION_MASK)
        self.viewport2.set_events(Gdk.EventMask.BUTTON_PRESS_MASK | Gdk.EventMask.POINTER_MOTION_MASK)

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


#-------------------------------------------- METODOS DE LA NUEVA VISTA -----------------------------------------------#

#-------------------------------------------- METODOS DE CARGA DE IMAGENES --------------------------------------------#

    #Creamos el objeto del modelo vist_data llamando a los metodos del controlador
    def crear_vista_data(self, path):

        # Osea elegimos un dicom, la vista manda la orden al controlador de convertir el dicom a .tiff pero obtenemos 2 uno de 8 y otro de 16
        # Despues de esto la vista procede a cargarlo y obtener las modificaciones necesarias para poder

        #La tupla contiene los paths de la imagen en 8 bits y en 16 bits para poder representar y crear el objeto vista_data
        tuple = self.controlador.transformacion_y_guardado_vista(path)

        vista_data = ModeloVista(tuple[0], tuple[1])

        return vista_data




    # Metodos para cargar imagenes y carpetas que contengan imagenes

    # Metodo para cargar una imagen
    def load_image(self, file_path):
        try:
            self.imagecv_8_bits = cv2.imread(file_path)
            self.original_pixbuf_8_bits = GdkPixbuf.Pixbuf.new_from_file(file_path)
            self.displayed_pixbuf_8_bits = GdkPixbuf.Pixbuf.new_from_file(file_path)
            self.image_8_bits = Gtk.Image.new_from_pixbuf(self.displayed_pixbuf_8_bits)  # added

            self.imagecv_16_bits = cv2.imread(file_path)
            self.original_pixbuf_16_bits = GdkPixbuf.Pixbuf.new_from_file(file_path)
            self.displayed_pixbuf_16_bits = GdkPixbuf.Pixbuf.new_from_file(file_path)
            self.image_16_bits = Gtk.Image.new_from_pixbuf(self.displayed_pixbuf_16_bits)  # added
            # scaled_pixbuf = pixbufdelaimagen.scale_simple(600, 400, GdkPixbuf.InterpType.BILINEAR)
            # image.set_from_pixbuf(scaled_pixbuf)
        except Exception as e:
            print("Error al cargar la imagen:", e)


    # Metodo que nos permite cargar una carpeta y todas las imagenes a la vez que contenga
    def load_image_vista_data(self, vista_data):
        try:
            self.imagecv_8_bits = vista_data.get_image_numpy_8_bits()
            self.original_pixbuf_8_bits = vista_data.get_original_pixbuf_8_bits()
            self.displayed_pixbuf_8_bits = vista_data.get_displayed_pixbuf_8_bits()
            self.image_8_bits = vista_data.get_image_8_bits()

            print(type(self.imagecv_8_bits))
            print(self.imagecv_8_bits)

            print("SeparacionNNNNNNNNNNNNNNNNN")

            self.imagecv_16_bits = vista_data.get_image_numpy_16_bits()
            self.original_pixbuf_16_bits = vista_data.get_original_pixbuf_16_bits()
            self.displayed_pixbuf_16_bits = vista_data.get_displayed_pixbuf_16_bits()
            self.image_16_bits = vista_data.get_image_16_bits()

            print(type(self.imagecv_16_bits))
            print(self.imagecv_16_bits)

            print("Numero elementos de la lista: ", len(self.lista_imagenes))
            print("Posicion de la Lista: ", self.posicion_lista)

            #Lo aplica en ambas imagenes
            self.scale_image()

            # image_cv = self.imagecv_16_bits
            #
            # # Verificar si la imagen se cargó correctamente
            # if image_cv is not None:
            #     # Obtener las dimensiones de la imagen
            #     height, width, channels = image_cv.shape
            #
            #     # Iterar sobre los píxeles y mostrar sus valores
            #     for y in range(height):
            #         for x in range(width):
            #             pixel_value = tuple(image_cv[y, x])
            #             print(f"Pixel en ({x}, {y}): {pixel_value}")
            # else:
            #     print("Error: No se pudo cargar la imagen con cv2.")

            self.viewport.set_size_request(self.displayed_pixbuf_8_bits.get_width(), self.displayed_pixbuf_8_bits.get_height())
            self.viewport.add(self.image_8_bits)
            self.viewport.show_all()

            self.viewport2.set_size_request(self.displayed_pixbuf_16_bits.get_width(), self.displayed_pixbuf_16_bits.get_height())
            self.viewport2.add(self.image_16_bits)
            self.viewport2.show_all()

        except Exception as e:
            print("Error al cargar la imagen:", e)

    # Funcion usada
    def scale_image(self):
        self.displayed_pixbuf_8_bits = self.original_pixbuf_8_bits.scale_simple(self.original_pixbuf_8_bits.get_width() * self.ratio,
                                                                  self.original_pixbuf_8_bits.get_height() * self.ratio, 2)

        self.displayed_pixbuf_16_bits = self.original_pixbuf_16_bits.scale_simple(self.original_pixbuf_16_bits.get_width() * self.ratio,
                                                                  self.original_pixbuf_16_bits.get_height() * self.ratio, 2)

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

        elif response == Gtk.ResponseType.CANCEL:
            print("Cancel clicked")

        dialog.destroy()

    # AUXILIAR CARGA MULTIPLE IMAGENES
    def cargar_image_multiple_lista(self, vista_data):
        try:
            #objetoFoto = ModeloVista(file_path)
            self.lista_imagenes.append(vista_data)

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
                vista_data = self.crear_vista_data(f)
                self.cargar_image_multiple_lista(vista_data)

            self.posicion_lista = len(self.lista_imagenes) - 1
            self.load_image_vista_data(self.lista_imagenes[self.posicion_lista])

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

#----------------------------------------------- METODOS PARA EL SCROLL -----------------------------------------------#

    #Funciones para sincronizar las barras de scroll cuando se haga algun cambio entre ellas

    # Función de callback para el evento "value-changed" de la barra de desplazamiento del primer ScrolledWindow
    def on_vadjustment1_changed(self, adjustment1, adjustment2):
        if self.panning == False:
            # Obtener el valor de la barra de desplazamiento del primer ScrolledWindow
            value = adjustment1.get_value()

            # Establecer el mismo valor en la barra de desplazamiento del segundo ScrolledWindow
            adjustment2.set_value(value)

    def on_hadjustment1_changed(self, adjustment1, adjustment2):
        if self.panning == False:
            # Obtener el valor de la barra de desplazamiento del primer ScrolledWindow
            value = adjustment1.get_value()

            # Establecer el mismo valor en la barra de desplazamiento del segundo ScrolledWindow
            adjustment2.set_value(value)

    def on_viewport_scroll_event(self, viewport, event):
        # Calcular el desplazamiento relativo
        delta = event.get_scroll_deltas()[2]

        scroll_scale_factor = 10

        # Obtener el ajuste de desplazamiento de ambos viewports
        adjustment1 = self.viewport.get_vadjustment()
        adjustment2 = self.viewport2.get_vadjustment()

        # Aplicar el desplazamiento relativo a ambos ajustes de desplazamiento
        adjustment1.set_value(adjustment1.get_value() + delta * scroll_scale_factor)
        adjustment2.set_value(adjustment2.get_value() + delta * scroll_scale_factor)

        return True

#----------------------------------------------------------------------------------------------------------------------#

#---------------------------------------------- METODOS DE PARA EL ZOOM -----------------------------------------------#

    # Funcion para actualizar la imagen en el viewport despues de modificar el zoom de la imagen
    def update_image(self):
        # Cargar la imagen original

        # Escalar la imagen según el factor de zoom
        scaled_width = int(self.displayed_pixbuf_8_bits.get_width() * self.zoom_factor)
        scaled_height = int(self.displayed_pixbuf_8_bits.get_height() * self.zoom_factor)
        displayed_pixbuf_8_bits = self.displayed_pixbuf_8_bits.scale_simple(scaled_width, scaled_height, GdkPixbuf.InterpType.BILINEAR)

        # Escalar la imagen según el factor de zoom
        scaled_width = int(self.displayed_pixbuf_16_bits.get_width() * self.zoom_factor)
        scaled_height = int(self.displayed_pixbuf_16_bits.get_height() * self.zoom_factor)
        displayed_pixbuf_16_bits = self.displayed_pixbuf_16_bits.scale_simple(scaled_width, scaled_height, GdkPixbuf.InterpType.BILINEAR)

        # Mostrar la imagen actualizada
        self.image_8_bits.set_from_pixbuf(displayed_pixbuf_8_bits)
        self.image_16_bits.set_from_pixbuf(displayed_pixbuf_16_bits)

    def zoom_in(self):
        self.zoom_factor *= 1.1  # Factor de aumento del zoom
        self.update_image()

    def zoom_out(self):
        self.zoom_factor /= 1.1  # Factor de reducción del zoom
        self.update_image()

    def on_scroll_event_zoom(self, widget, event):
        # Verificar si se ha movido la rueda del ratón y si la tecla Ctrl está presionada
        if event.state & Gdk.ModifierType.CONTROL_MASK and event.direction in [Gdk.ScrollDirection.UP,
                                                                               Gdk.ScrollDirection.DOWN]:
            #self.viewport.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.NEVER)
            if event.direction == Gdk.ScrollDirection.UP:
                self.zoom_in()
            elif event.direction == Gdk.ScrollDirection.DOWN:
                self.zoom_out()

    #Este no se usa
    def on_scroll_eventctrl(self, widget, event):
        # Handles zoom in / zoom out on Ctrl+mouse wheel
        accel_mask = Gtk.accelerator_get_default_mod_mask()
        if event.state & accel_mask == Gdk.ModifierType.CONTROL_MASK:
            direction = event.get_scroll_deltas()[2]
            if direction > 0:  # scrolling down -> zoom out
                self.zoom_out()
            else:
                self.zoom_in()

#----------------------------------------------------------------------------------------------------------------------#

#----------------------------------------------- METODOS PARA EL PANNING ----------------------------------------------#

    #movida para probar a ver si se puede desactivar temporalmente la sync de barras cuando hacemos paning
    def on_button_press_event(self, widget, event):
        if event.button == Gdk.BUTTON_PRIMARY:
            self.panning = True

    def on_button_release_event(self, widget, event):
        if event.button == Gdk.BUTTON_PRIMARY:
            self.panning = False

    def on_viewport_button_press(self, widget, event):
        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 1:
            self.prev_x = event.x
            self.prev_y = event.y

    def on_viewport_motion_notify(self, widget, event):
        if self.panning:
            if hasattr(self, 'prev_x') and hasattr(self, 'prev_y'):
                if event.is_hint:
                    x, y, state = event.window.get_device_position(event.device)
                else:
                    x = event.x
                    y = event.y
                    state = event.state
                if state & Gdk.ModifierType.BUTTON1_MASK:
                    h_adjustment = self.viewport.get_hadjustment()
                    v_adjustment = self.viewport.get_vadjustment()
                    h_adjustment2 = self.viewport2.get_hadjustment()
                    v_adjustment2 = self.viewport2.get_vadjustment()
                    h_adjustment.set_value(h_adjustment.get_value() + (self.prev_x - x))
                    v_adjustment.set_value(v_adjustment.get_value() + (self.prev_y - y))
                    h_adjustment2.set_value(h_adjustment2.get_value() + (self.prev_x - x))
                    v_adjustment2.set_value(v_adjustment2.get_value() + (self.prev_y - y))
                    self.prev_x = x
                    self.prev_y = y

#----------------------------------------------------------------------------------------------------------------------#

#-------------------------------------- METODOS PARA LAS SCROLL BARS WINDOWING ----------------------------------------#

    def on_scale_changed(self, scale):
        # Reiniciar el temporizador si ya estaba activo
        if self.timeout_id:
            GLib.source_remove(self.timeout_id)

        # Activar el temporizador para aplicar el windowing después de un breve retraso
        self.timeout_id = GLib.timeout_add(200, self.apply_windowing_delayed)

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
        #cambiar esto tambien tienes que poner el 65535 para que falle y calcule un rango fuera de 255
        windowed_image = np.clip((image - min_value) / window_width * 255, 0, 255).astype(np.uint8)
        return windowed_image

    def apply_windowing_delayed(self):
        # Obtener los valores de window_center y window_width de las barras de desplazamiento
        window_center = self.scale_center.get_value()
        print(window_center)
        window_width = self.scale_width.get_value()
        print(window_width)

        # Aplicar windowing a la imagen cargada
        if hasattr(self, 'image_8_bits'):
            print("entra")
            windowed_image_8 = self.apply_windowing_8_bits(self.imagecv_8_bits, window_center, window_width)
            windowed_image_16 = self.apply_windowing_16_bits(self.imagecv_16_bits, window_center, window_width)

            self.displayed_pixbuf_8_bits = self.show_image(windowed_image_8)
            self.displayed_pixbuf_16_bits = self.show_image_16(windowed_image_16)
            self.image_8_bits.set_from_pixbuf(self.displayed_pixbuf_8_bits)
            self.image_16_bits.set_from_pixbuf(self.displayed_pixbuf_16_bits)

        # Reiniciar el ID del temporizador
        self.timeout_id = None

        # Detener la propagación del evento
        return False

    def show_image(self, image):
        # Convertir la imagen a formato Pixbuf para mostrarla en el área de dibujo
        height, width, channels = image.shape
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        print("show 8 mvodio")
        pixbuf = GdkPixbuf.Pixbuf.new_from_data(rgb_image.flatten(), GdkPixbuf.Colorspace.RGB, False, 8, width, height, width * channels, None, None)

        return pixbuf

    def show_image_16(self, image):
        # Convertir la imagen a formato Pixbuf para mostrarla en el área de dibujo
        #Poner el quitar el channel si pruebo a convertir la de 16 a 8 cargandola mal para ensenharle lo que hice

        height, width, channels = image.shape

        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        print("show 16 mvodio")
        pixbuf = GdkPixbuf.Pixbuf.new_from_data(rgb_image.flatten(), GdkPixbuf.Colorspace.RGB, False, 8, width, height, width * channels, None, None)

        return pixbuf

#----------------------------------------------------------------------------------------------------------------------#

#-------------------------------------------- METODOS DE PARA LOS BOTONES ---------------------------------------------#

    def on_button_anterior_clicked(self, widget):

        if len(self.lista_imagenes) == 0:
            raise Exception("La lista esta vacia")

        if (self.posicion_lista-1) < 0:
            self.posicion_lista = len(self.lista_imagenes)-1
        else:
            self.posicion_lista -= 1

        for child in self.viewport.get_children():
            self.viewport.remove(child)
            for child in self.viewport2.get_children():
                self.viewport2.remove(child)
        self.load_image_vista_data(self.lista_imagenes[self.posicion_lista])

    def on_button_siguiente_clicked(self, widget):

        if len(self.lista_imagenes) == 0:
            raise Exception("La lista esta vacia")

        if (self.posicion_lista+1) > (len(self.lista_imagenes)-1):
            self.posicion_lista = 0
        else:
            self.posicion_lista += 1

        for child in self.viewport.get_children():
            self.viewport.remove(child)
        for child in self.viewport2.get_children():
            self.viewport2.remove(child)
        self.load_image_vista_data(self.lista_imagenes[self.posicion_lista])

    def on_button_delete_foto_actual_clicked(self, widget):
        if len(self.lista_imagenes) == 0:
            raise Exception("La lista esta vacia")

        del self.lista_imagenes[self.posicion_lista]
        for child in self.viewport.get_children():
            self.viewport.remove(child)
        for child in self.viewport2.get_children():
            self.viewport2.remove(child)

        if len(self.lista_imagenes) == 0:
            self.button3.hide()
            self.button4.hide()
            self.button5.hide()
            self.button_delete.hide()
        else:
            if len(self.lista_imagenes) == 1:
                self.posicion_lista = 0
            self.load_image_vista_data(self.lista_imagenes[self.posicion_lista])

    #Hacer boton de borrar la lista y boton de borrar una foto
    def on_button_delete_lista_clicked(self, widget):
        if len(self.lista_imagenes) == 0:
            raise Exception("La lista esta vacia")

        for child in self.viewport.get_children():
            self.viewport.remove(child)
        for child in self.viewport2.get_children():
            self.viewport2.remove(child)
        self.lista_imagenes.clear()

        self.button3.hide()
        self.button4.hide()
        self.button5.hide()
        self.button_delete.hide()
        return True

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

    # -----------------------------------------------------------------------------------------------------------------------

    # def mostrar_ejemplo(self):
    #     win = Gtk.Window()
    #     win.connect("destroy", Gtk.main_quit)
    #     win.show_all()
    #     Gtk.main()