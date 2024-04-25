from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg as FigureCanvas
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

class Vista(Gtk.Window):

    def __init__(self, controlador):

        self.start_window_center = None
        self.start_window_width = None
        self.start_y = None
        self.start_x = None

        self.controlador = controlador

        # Creacion de la ventana principal de la vista

        # Lista que contendra las imagenes que carguemos, si elegimos cargar
        self.lista_imagenes = []
        # Posicion inical para mostrar la primera imagen cuando cargamos multiples imagenes
        self.posicion_lista = 0

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
        self.boton_cargar_fichero = Gtk.Button(label="Elegir Fichero")
        self.boton_cargar_fichero.connect("clicked", self.logica_boton_elegir_fichero)
        self.box_botones.pack_start(self.boton_cargar_fichero, False, False, 10)

        # Boton para cargar una carpeta con multiples imagenes, podremos pasar a la siguiente foto o a la anterior
        self.boton_cargar_carpeta = Gtk.Button(label="Elegir Carpeta")
        self.boton_cargar_carpeta.connect("clicked", self.logica_boton_elegir_directorio)
        self.box_botones.pack_start(self.boton_cargar_carpeta, False, False, 10)

        # Boton para movernos a la imagen anterior de las imagenes cargadas
        self.boton_anterior = Gtk.Button(label="Anterior Foto")
        self.boton_anterior.connect("clicked", self.logica_boton_anterior)
        self.boton_anterior.hide()
        self.box_botones.pack_start(self.boton_anterior, False, False, 10)

        # Boton para movernos a la imagen siguiente de las imagenes cargadas
        self.boton_siguiente = Gtk.Button(label="Siguiente Foto")
        self.boton_siguiente.connect("clicked", self.logica_boton_siguiente)
        self.boton_siguiente.hide()
        self.box_botones.pack_start(self.boton_siguiente, False, False, 10)

        # Boton para eliminar la imagen que se esta representando en la aplicacion
        self.boton_eliminar_foto = Gtk.Button(label="Eliminar Foto Actual")
        self.boton_eliminar_foto.connect("clicked", self.logica_boton_eliminar_foto_actual)
        self.boton_eliminar_foto.hide()
        self.box_botones.pack_start(self.boton_eliminar_foto, False, False, 10)

        # CheckBox para activar y desactivar el windowing
        self.check_button = Gtk.CheckButton(label="Activar Windowing")
        self.check_button.connect("toggled", self.checkbutton_windowing)
        self.box_botones.pack_start(self.check_button, False, False, 10)
        self.value_windowing_active = False

        # Boton que elimina todas las imagenes que han sido cargadas
        self.boton_eliminar_todas_fotos = Gtk.Button()
        self.boton_eliminar_todas_fotos.connect("clicked", self.logica_boton_eliminar_lista_fotos)
        self.boton_eliminar_todas_fotos.hide()
        self.boton_eliminar_todas_fotos.set_image(Gtk.Image.new_from_icon_name("user-trash-symbolic", Gtk.IconSize.BUTTON))
        self.box_botones.pack_start(self.boton_eliminar_todas_fotos, False, False, 10)

        # ----------------------------------------- Anhadimos las imagenes --------------------------------------------#

        # Esta parte de la vista se agregaran los widgets necesarios para poder representar las imagenes

        # Crear una caja para visualizar la imagen
        self.box_imagenes = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.box_principal.pack_start(self.box_imagenes, True, True, 0)
        self.box_imagenes.set_homogeneous(True)
        self.box_imagenes.set_spacing(0)

        # --------------------------------------------- Primera imagen ------------------------------------------------#

        self.imagecv_8_bits = None
        self.imagecv_8_bits_displayed = None
        self.imagecv_16_bits = None
        self.imagecv_16_bits_displayed = None

        # Crear el widget para representar la imagen
        self.scrolledwindow = Gtk.ScrolledWindow()  # added
        self.viewport = Gtk.Viewport()  # added

        # Agregacion para el canvas
        self.figure, axs = plt.subplots(nrows=1, ncols=2, figsize=(10, 6), sharex=True, sharey=True, frameon=False)
        self.figure.tight_layout()
        self.figure.subplots_adjust(wspace=0, hspace=0, left=0, right=1, bottom=0, top=1)

        self.ax_8_bits = axs[0]
        self.ax_8_bits.axis('off')
        self.ax_16_bits = axs[1]
        self.ax_16_bits.axis('off')

        #Valores de zoom y posicion de la imagen
        self.coordenadas_x_8_bits = None
        self.coordenadas_y_8_bits = None
        self.coordenadas_x_16_bits = None
        self.coordenadas_y_16_bits = None

        self.canvas = FigureCanvas(self.figure)

        self.toolbar = NavigationToolbar(self.canvas, self)
        self.box_botones.pack_start(self.toolbar, False, False, 10)

        # Agregar el lienzo al viewport
        self.viewport.add(self.canvas)

        self.scrolledwindow.add(self.viewport)
        self.box_imagenes.pack_start(self.scrolledwindow, True, True, 0)

        #----- --------------------- Conexiones de los botones con las diferentes funciones ---------------------------#
        self.connect("destroy", Gtk.main_quit)

        # Registramos los eventos de pulsacion del teclado
        self.viewport.set_events(Gdk.EventMask.BUTTON_PRESS_MASK | Gdk.EventMask.POINTER_MOTION_MASK)

        # Variable para identificar si el botón primario del ratón está presionado
        self.mouse_pressed = False

        # Boleanos para saber cuando tenemos activa alguna funcion permanente
        self.zoom_teclado = False
        self.panning_teclado = False

        # Variable utilizada para dormir la funcion de windowing
        self.timeout_id = None

        #Para reconocer el movimiento en vertical y que funque el cambio de window center
        self.viewport.connect("motion-notify-event", self.on_motion_notify_center)
        self.viewport.connect("motion-notify-event", self.on_motion_notify_width)
        self.viewport.connect("button-press-event", self.on_button_press)
        self.viewport.connect("button-release-event", self.on_button_release)

        # Configurar eventos de teclado
        self.connect("key-press-event", self.logica_presionar_z_zoom)
        self.connect("key-press-event", self.logica_presionar_x_panning)

        # Evento zoom con el boton secundario del raton
        self.connect("button-press-event", self.presionado_boton_siguiente_raton_zoom)
        self.connect("button-release-event", self.liberado_boton_siguiente_raton_zoom)

        # Evento panning con el boton anterior raton
        self.connect("button-press-event", self.presionado_boton_atras_raton_panning)
        self.connect("button-release-event", self.liberado_boton_atras_raton_panning)

        # Evento windowing con el siguiente del raton
        self.connect("button-press-event", self.presionado_boton_raton_windowing)
        self.connect("button-release-event", self.liberado_boton_raton_windowing)

        # Mostrar todos los elementos de la ventana
        self.show_all()

        # Ocultamos los botones que no se utilizan hasta cargar multiples imagenes
        self.boton_anterior.hide()
        self.boton_eliminar_foto.hide()
        self.boton_siguiente.hide()
        self.boton_eliminar_todas_fotos.hide()

#-------------------------------------------- METODOS DE CARGA DE IMAGENES --------------------------------------------#

    def mostrar_imagen_8_bits(self, image):
        self.ax_8_bits.clear()
        self.ax_8_bits.imshow(image, cmap='gray')
        self.ax_8_bits.set_title("Version 8 Bits")
        self.ax_8_bits.axis('off')
        self.canvas.draw()

    def actualizar_imagen_8_bits(self, imagen, coordenadas_x_8_bits, coordenadas_y_8_bits):
        self.ax_8_bits.clear()
        self.ax_8_bits.imshow(imagen, cmap='gray')
        self.ax_8_bits.set_title("Version 8 Bits")
        self.ax_8_bits.axis('off')
        self.ax_8_bits.set_xlim(coordenadas_x_8_bits)
        self.ax_8_bits.set_ylim(coordenadas_y_8_bits)
        self.canvas.draw()

    def mostrar_imagen_16_bits(self, image):
        print(image)
        self.ax_16_bits.clear()
        self.ax_16_bits.imshow(image, cmap='gray')
        self.ax_16_bits.set_title("Version 16 Bits")
        self.ax_16_bits.axis('off')
        self.canvas.draw()

    def actualizar_imagen_16_bits(self, image, coordenadas_x_16_bits, coordenadas_y_16_bits):
        print(image)
        self.ax_16_bits.clear()
        self.ax_16_bits.imshow(image, cmap='gray')
        self.ax_16_bits.set_title("Version 16 Bits")
        self.ax_16_bits.axis('off')
        self.ax_16_bits.set_xlim(coordenadas_x_16_bits)
        self.ax_16_bits.set_ylim(coordenadas_y_16_bits)
        self.canvas.draw()

    #Metodo para crear el objeto que maneja la vista con el contenido de las imagenes
    def crear_vista_data(self, path):

        # Despues de cargar el dicom se convierte a .tiff y obtenemos la imagen con una profundidad de 8 bits y
        # otro de 16 bits, lo que nos devuelve el controlador es el path de ambos archivos.

        # Una vez obtenidos los paths el Modelo de la vista crea los objetos con la informacion de las imagenes
        tuple = self.controlador.transformacion_y_guardado_vista(path)

        vista_data = ModeloVista(tuple[0], tuple[1])
        self.lista_imagenes.append(vista_data)

        return vista_data

    # Metodo que a partir del objeto vista_data obtiene el contenido de la imagen y lo muestra en la aplicacion
    def cargar_y_mostrar_images(self, vista_data):
        try:
            self.imagecv_8_bits = vista_data.get_image_numpy_8_bits()
            self.imagecv_8_bits_displayed = vista_data.get_image_numpy_8_bits()

            self.imagecv_16_bits = vista_data.get_image_numpy_16_bits()
            self.imagecv_16_bits_displayed = vista_data.get_image_numpy_16_bits()

            print("Numero elementos de la lista: ", len(self.lista_imagenes))
            print("Posicion de la Lista: ", self.posicion_lista)

            self.mostrar_imagen_8_bits(self.imagecv_8_bits_displayed)
            self.mostrar_imagen_16_bits(self.imagecv_16_bits_displayed)

            print(self.imagecv_16_bits_displayed)

        except Exception as e:
            print("Error al cargar la imagen:", e)

#----------------------------------------------------------------------------------------------------------------------#

#----------------------------------- LOGICA PARA LOS BOTONES DE CARGA DE IMAGENES -------------------------------------#

    #Filtros para el dialogo de elegir archivo
    def filtros_dialago_elegir_fichero(self, dialog):
        filter_dcm = Gtk.FileFilter()
        filter_dcm.set_name("Dicom files")
        filter_dcm.add_pattern("*.dcm")
        dialog.add_filter(filter_dcm)

        filter_any = Gtk.FileFilter()
        filter_any.set_name("Any files")
        filter_any.add_pattern("*")
        dialog.add_filter(filter_any)

    # Metodo para elegir el .dcm que queremos convertir y mostrar en la aplicacion
    def logica_boton_elegir_fichero(self, widget):
        dialog = Gtk.FileChooserDialog(
            title="Please choose a file", parent=self, action=Gtk.FileChooserAction.OPEN
        )
        dialog.add_buttons(
        Gtk.STOCK_CANCEL,
              Gtk.ResponseType.CANCEL,
              Gtk.STOCK_OPEN,
              Gtk.ResponseType.OK,
        )
        self.filtros_dialago_elegir_fichero(dialog)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            print("Open clicked")
            print("File selected: " + dialog.get_filename())
            vista_data = self.crear_vista_data(dialog.get_filename())
            self.cargar_y_mostrar_images(vista_data)
            self.mostrar_imagen_8_bits(self.imagecv_8_bits_displayed)
            self.mostrar_imagen_16_bits(self.imagecv_16_bits_displayed)
        elif response == Gtk.ResponseType.CANCEL:
            print("Cancel clicked")
        dialog.destroy()

    # Metodo para cargar todos los .dcm que existan en un directorio y mostrar el ultimo cargado
    def logica_boton_elegir_directorio(self, widget):
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
            directorio, patron = os.path.split(path)
            directorio = Path(directorio)
            tiff_files = glob.glob(os.path.join(directorio, '*.dcm'))
            if not directorio.exists():
                raise print("No existe directorio")
            elif not tiff_files:
                raise print("No existen dcm en el directorio")

            for f in glob.glob(path):
                print(f)
                print(f.split("/")[-1])
                self.crear_vista_data(f)

            self.posicion_lista = len(self.lista_imagenes) - 1
            self.cargar_y_mostrar_images(self.lista_imagenes[self.posicion_lista])
            self.mostrar_imagen_8_bits(self.imagecv_8_bits_displayed)
            self.mostrar_imagen_16_bits(self.imagecv_16_bits_displayed)

            #Hacer visibles los botones para movernos entre imagenes
            self.boton_anterior.show()
            self.boton_eliminar_foto.show()
            self.boton_siguiente.show()
            self.boton_eliminar_todas_fotos.show()

            dialog.get_filename()
        elif response == Gtk.ResponseType.CANCEL:
            print("Cancel clicked")
            self.boton_anterior.hide()
            self.boton_eliminar_foto.hide()
            self.boton_siguiente.hide()
            self.boton_eliminar_todas_fotos.hide()
        dialog.destroy()

#----------------------------------------------------------------------------------------------------------------------#

#---------------------------------------------- METODOS PARA WINDOWING ------------------------------------------------#

    def aplicar_windowing_imagen_8_bits(self, image, window_center, window_width):
        # Calcular los límites del rango de píxeles
        min_value = window_center - (window_width / 2)
        max_value = window_center + (window_width / 2)

        # Aplicar windowing a la imagen
        windowed_image = np.clip((image - min_value) / window_width * 255, 0, 255).astype(np.uint8)
        return windowed_image

    def aplicar_windowing_imagen_16_bits(self, image, window_center, window_width):
        # Calcular los límites del rango de píxeles
        min_value = window_center - (window_width / 2)
        max_value = window_center + (window_width / 2)

        # Aplicar windowing a la imagen
        windowed_image = np.clip((image - min_value) / window_width * 65535, 0, 65535).astype(np.uint16)
        return windowed_image

#----------------------------------------------------------------------------------------------------------------------#

#--------------------------------------- METODOS DE PARA LOS BOTONES INTERFAZ -----------------------------------------#

    def logica_boton_anterior(self, widget):
        self.ax_8_bits.clear()
        self.ax_16_bits.clear()
        self.ax_8_bits.axis('off')
        self.ax_16_bits.axis('off')
        self.canvas.draw()

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

        self.cargar_y_mostrar_images(self.lista_imagenes[self.posicion_lista])
        self.mostrar_imagen_8_bits(self.imagecv_8_bits_displayed)
        self.mostrar_imagen_16_bits(self.imagecv_16_bits_displayed)

    def logica_boton_siguiente(self, widget):

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

        self.cargar_y_mostrar_images(self.lista_imagenes[self.posicion_lista])
        self.mostrar_imagen_8_bits(self.imagecv_8_bits_displayed)
        self.mostrar_imagen_16_bits(self.imagecv_16_bits_displayed)

    def logica_boton_eliminar_foto_actual(self, widget):

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
                self.cargar_y_mostrar_images(self.lista_imagenes[self.posicion_lista])
                self.mostrar_imagen_8_bits(self.imagecv_8_bits_displayed)
                self.mostrar_imagen_16_bits(self.imagecv_16_bits_displayed)
            else:
                self.ax_8_bits.clear()
                self.ax_16_bits.clear()
                self.ax_8_bits.axis('off')
                self.ax_16_bits.axis('off')
                self.canvas.draw()
                self.boton_anterior.hide()
                self.boton_eliminar_foto.hide()
                self.boton_siguiente.hide()
                self.boton_eliminar_todas_fotos.hide()

        return True

    def logica_boton_eliminar_lista_fotos(self, widget):
        if len(self.lista_imagenes) == 0:
            raise Exception("La lista esta vacia")

        self.windowing_center_8_bits = 127
        self.windowing_width_8_bits = 255
        self.windowing_center_16_bits = 32767
        self.windowing_width_16_bits = 65535

        self.lista_imagenes.clear()
        self.posicion_lista = 0
        self.ax_8_bits.clear()
        self.ax_16_bits.clear()
        self.ax_8_bits.axis('off')
        self.ax_16_bits.axis('off')
        self.canvas.draw()

        self.boton_anterior.hide()
        self.boton_eliminar_foto.hide()
        self.boton_siguiente.hide()
        self.boton_eliminar_todas_fotos.hide()
        return True

#----------------------------------------------------------------------------------------------------------------------#

#----------------------------------- LOGICA ACCIONES (ZOOM, PANNING, WINDOWING) ---------------------------------------#

    def logica_presionar_z_zoom(self, widget, event):
        if event.keyval == Gdk.KEY_z:
            if not self.zoom_teclado:
                self.zoom_teclado = True
                print("Activado Zoom")
            else:
                self.zoom_teclado = False
                print("Desactivado Zoom")
            self.toolbar.zoom()

    def logica_presionar_x_panning(self, widget, event):
        if event.keyval == Gdk.KEY_x:
            if not self.panning_teclado:
                self.panning_teclado = True
                print("Activado Pannning")
            else:
                self.panning_teclado = False
                print("Desactivado Panning")
            self.toolbar.pan()

    #------------------ EVENTOS WINDOWING RATON -----------------
    def presionado_boton_raton_windowing(self, widget, event):
        if event.button == Gdk.BUTTON_SECONDARY:
            self.value_windowing_active = True

    def liberado_boton_raton_windowing(self, widget, event):
        if event.button == Gdk.BUTTON_SECONDARY:
            self.value_windowing_active = False

    #------------------------------------------------------------

    #------------------- EVENTOS PANNING RATON-------------------
    def presionado_boton_atras_raton_panning(self, widget, event):
        if event.button == 8:
            self.toolbar.pan()

    def liberado_boton_atras_raton_panning(self, widget, event):
        if event.button == 8:
            self.toolbar.pan()

    #------------------------------------------------------------

    #-------------------- EVENTOS ZOOM RATON --------------------
    def presionado_boton_siguiente_raton_zoom(self, widget, event):
        if event.button == 9:
            print("ENTRAMOS EN EL ZOOM")
            self.toolbar.zoom()

    def liberado_boton_siguiente_raton_zoom(self, widget, event):
        if event.button == 9:
            print("ENTRAMOS EN EL ZOOM")
            self.toolbar.zoom()

    #------------------------------------------------------------

    def checkbutton_windowing(self, button):
        if button.get_active():
            self.value_windowing_active = True
        else:
            self.value_windowing_active = False
        print("CheckButton state is", self.value_windowing_active)

    def sincronizar_valores_windowing_8_bits(self):
        value_center_16_bits = self.windowing_center_16_bits
        value_width_16_bits = self.windowing_width_16_bits

        percentage = value_center_16_bits / 65535 * 100
        print("Porcentaje de la barra 1:", percentage)
        self.windowing_center_8_bits = round(percentage * 255 / 100)
        self.aplicar_windowing_viewport_8_bits()

        percentage = value_width_16_bits / 65535 * 100
        print("Porcentaje de la barra 2:", percentage)
        self.windowing_width_8_bits = round(percentage * 255 / 100)
        self.aplicar_windowing_viewport_8_bits()

    #cambiar nombre a algo que haga referencia a que es el metodo de cuando clickas con el raton en el viewport
    def aplicar_windowing_viewport_8_bits(self):
        # Obtener los valores de window_center y window_width de las barras de desplazamiento
        print(self.windowing_center_8_bits)
        print(self.windowing_width_8_bits)

        # Aplicar windowing a la imagen cargada
        if hasattr(self, 'imagecv_8_bits'):
            print("entra")
            self.imagecv_8_bits_displayed = self.aplicar_windowing_imagen_8_bits(self.imagecv_8_bits, self.windowing_center_8_bits, self.windowing_width_8_bits)

            self.coordenadas_x_8_bits = self.ax_8_bits.get_xlim()
            self.coordenadas_y_8_bits = self.ax_8_bits.get_ylim()
            self.actualizar_imagen_8_bits(self.imagecv_8_bits_displayed, self.coordenadas_x_8_bits, self.coordenadas_y_8_bits)

        print("LLEGA AQUI ESPROPIESE aplicar_windowing_viewport_8_bits")

        # Detener la propagación del evento
        return False

    def aplicar_windowing_viewport_16_bits(self):
        # Obtener los valores de window_center y window_width de las barras de desplazamiento
        window_center = self.windowing_center_16_bits
        print(window_center)
        window_width = self.windowing_width_16_bits
        print(window_width)

        # Aplicar windowing a la imagen cargada
        if hasattr(self, 'imagecv_16_bits'):
            print("entra")
            self.imagecv_16_bits_displayed = self.aplicar_windowing_imagen_16_bits(self.imagecv_16_bits, window_center, window_width)

            self.coordenadas_x_16_bits = self.ax_16_bits.get_xlim()
            self.coordenadas_y_16_bits = self.ax_16_bits.get_ylim()

            self.actualizar_imagen_16_bits(self.imagecv_16_bits_displayed, self.coordenadas_x_16_bits, self.coordenadas_y_16_bits)

        self.sincronizar_valores_windowing_8_bits()

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
                self.aplicar_windowing_viewport_16_bits()
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

