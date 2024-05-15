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

        self.start_window_center = int
        self.start_window_width = int
        self.start_y = float
        self.start_x = float

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

        self.windowing_center_8_bits = 127
        self.windowing_width_8_bits = 255
        self.windowing_center_16_bits = 32767
        self.windowing_width_16_bits = 65535

        # Boton para cargar una imagen o una carpeta con multiples imagenes
        self.boton_cargar_fichero = Gtk.Button(label="Abrir archivo/carpeta")
        #self.boton_cargar_fichero.connect("clicked", self.evento_boton_elegir_fichero)
        self.boton_cargar_fichero.connect("clicked", self.evento_boton_elegir_archivo_o_directorio)
        self.box_botones.pack_start(self.boton_cargar_fichero, False, False, 10)

        # Boton para movernos a la imagen anterior de las imagenes cargadas
        self.boton_anterior = Gtk.Button(label="Anterior Foto")
        self.boton_anterior.connect("clicked", self.evento_boton_anterior)
        self.boton_anterior.hide()
        self.box_botones.pack_start(self.boton_anterior, False, False, 10)

        # Boton para movernos a la imagen siguiente de las imagenes cargadas
        self.boton_siguiente = Gtk.Button(label="Siguiente Foto")
        self.boton_siguiente.connect("clicked", self.evento_boton_siguiente)
        self.boton_siguiente.hide()
        self.box_botones.pack_start(self.boton_siguiente, False, False, 10)

        # Boton para eliminar la imagen que se esta representando en la aplicacion
        self.boton_eliminar_foto = Gtk.Button(label="Eliminar Foto Actual")
        self.boton_eliminar_foto.connect("clicked", self.evento_boton_eliminar_foto_actual)
        self.boton_eliminar_foto.hide()
        self.box_botones.pack_start(self.boton_eliminar_foto, False, False, 10)

        # CheckBox para activar y desactivar el windowing
        self.check_button = Gtk.CheckButton(label="Activar Windowing")
        self.check_button.connect("toggled", self.evento_checkbutton_windowing)
        self.box_botones.pack_start(self.check_button, False, False, 10)
        self.value_windowing_active = False

        # Añadir una entrada para introducir números
        self.entry_numero_window_center = Gtk.Entry()
        self.entry_numero_window_center.set_input_purpose(Gtk.InputPurpose.DIGITS)
        self.entry_numero_window_center.set_placeholder_text("Window Center")
        # Conexión al evento changed
        self.entry_numero_window_center.connect("activate", self.evento_entry_cambiado_valor_window_center)
        self.box_botones.pack_start(self.entry_numero_window_center, False, False, 10)

        # Añadir una entrada para introducir números
        self.entry_numero_window_width = Gtk.Entry()
        self.entry_numero_window_width.set_input_purpose(Gtk.InputPurpose.DIGITS)
        self.entry_numero_window_width.set_placeholder_text("Window Width")
        # Conexión al evento changed
        self.entry_numero_window_width.connect("activate", self.evento_entry_cambiado_valor_window_width)
        self.box_botones.pack_start(self.entry_numero_window_width, False, False, 10)

        # Boton que elimina todas las imagenes que han sido cargadas
        self.boton_eliminar_todas_fotos = Gtk.Button()
        self.boton_eliminar_todas_fotos.connect("clicked", self.evento_boton_eliminar_lista_fotos)
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

        self.imagecv_8_bits = np.ndarray
        self.imagecv_8_bits_displayed = np.ndarray
        self.imagecv_16_bits = np.ndarray
        self.imagecv_16_bits_displayed = np.ndarray

        # Crear el widget para representar la imagen
        self.scrolledwindow = Gtk.ScrolledWindow()  # added
        self.viewport = Gtk.Viewport()  # added

        # Agregacion para el canvas
        #TENIA 10 6 figsize
        self.figure, axs = plt.subplots(nrows=1, ncols=2, figsize=(10, 6), sharex=True, sharey=True, frameon=False)
        self.figure.tight_layout()
        self.figure.subplots_adjust(wspace=0.01, hspace=0.01, left=0.01, right=0.99, bottom=0.01, top=0.97)

        self.ax_8_bits = axs[0]
        self.ax_8_bits.axis('off')
        self.ax_16_bits = axs[1]
        self.ax_16_bits.axis('off')

        #Valores de zoom y posicion de la imagen
        self.coordenadas_x_8_bits = tuple
        self.coordenadas_y_8_bits = tuple
        self.coordenadas_x_16_bits = tuple
        self.coordenadas_y_16_bits = tuple

        self.canvas = FigureCanvas(self.figure)

        self.toolbar = NavigationToolbar(self.canvas)
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
        self.viewport.connect("motion-notify-event", self.evento_movimiento_vertical_window_center)
        self.viewport.connect("motion-notify-event", self.evento_movimiento_horizontal_window_width)
        self.viewport.connect("button-press-event", self.evento_boton_primario_presionado_windowing)
        self.viewport.connect("button-release-event", self.evento_boton_primario_liberado_windowing)

        # Configurar eventos de teclado
        self.connect("key-press-event", self.evento_presionar_tecla_z_zoom)
        self.connect("key-press-event", self.evento_presionar_tecla_x_panning)

        # Evento zoom con el boton secundario del raton
        self.connect("button-press-event", self.evento_presionado_boton_siguiente_raton_zoom)
        self.connect("button-release-event", self.evento_liberado_boton_siguiente_raton_zoom)

        # Evento panning con el boton anterior raton
        self.connect("button-press-event", self.evento_presionado_boton_atras_raton_panning)
        self.connect("button-release-event", self.evento_liberado_boton_atras_raton_panning)

        # Evento windowing con el siguiente del raton
        self.connect("button-press-event", self.evento_presionado_boton_secundario_raton_windowing)
        self.connect("button-release-event", self.evento_liberado_boton_secundario_raton_windowing)

        # Mostrar todos los elementos de la ventana
        self.show_all()

        # Ocultamos los botones que no se utilizan hasta cargar multiples imagenes
        self.boton_anterior.hide()
        self.boton_eliminar_foto.hide()
        self.boton_siguiente.hide()
        self.boton_eliminar_todas_fotos.hide()
        self.entry_numero_window_center.hide()
        self.entry_numero_window_width.hide()

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
        self.ax_16_bits.clear()
        self.ax_16_bits.imshow(image, cmap='gray')
        self.ax_16_bits.set_title("Version 16 Bits")
        self.ax_16_bits.axis('off')
        self.canvas.draw()

    def actualizar_imagen_16_bits(self, image, coordenadas_x_16_bits, coordenadas_y_16_bits):
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

        except Exception as e:
            print("Error al cargar la imagen:", e)

#----------------------------------------------------------------------------------------------------------------------#

#----------------------------------- LOGICA PARA LOS BOTONES DE CARGA DE IMAGENES -------------------------------------#

    def evento_boton_elegir_archivo_o_directorio(self, widget):
        dialog = Gtk.FileChooserDialog(
            title="Elige un fichero o carpeta",
            parent=self,
            action=Gtk.FileChooserAction.OPEN,
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, "Select", Gtk.ResponseType.OK
        )
        dialog.set_default_size(800, 400)

        # Agregar filtros para archivos .dcm
        filter_dcm = Gtk.FileFilter()
        filter_dcm.set_name("Dicom files")
        filter_dcm.add_pattern("*.dcm")
        dialog.add_filter(filter_dcm)

        # Mostrar archivos de cualquier tipo
        filter_any = Gtk.FileFilter()
        filter_any.set_name("Any files")
        filter_any.add_pattern("*")
        dialog.add_filter(filter_any)

        # Cambiar a selección a OPEN que permite seleccionar uno o varios archivos
        dialog.set_action(Gtk.FileChooserAction.OPEN)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            print("Select clicked")
            selected_path = dialog.get_filename()
            print("Selected path:", selected_path)
            if os.path.isfile(selected_path):

                # Si se seleccionó un archivo
                vista_data = self.crear_vista_data(selected_path)
                self.cargar_y_mostrar_images(vista_data)
                self.mostrar_imagen_8_bits(self.imagecv_8_bits_displayed)
                self.mostrar_imagen_16_bits(self.imagecv_16_bits_displayed)

                # Mostrar botones para eliminar imágenes
                self.boton_eliminar_foto.show()
                self.boton_eliminar_todas_fotos.show()

                if len(self.lista_imagenes) > 1:
                    # Mostrar botones para navegar entre imágenes
                    self.boton_anterior.show()
                    self.boton_siguiente.show()
            elif os.path.isdir(selected_path):
                # Si se seleccionó una carpeta
                print("Folder selected: " + selected_path)
                path = os.path.join(selected_path, "*.dcm")
                directorio, patron = os.path.split(path)
                directorio = Path(directorio)
                tiff_files = glob.glob(os.path.join(directorio, '*.dcm'))
                if not tiff_files:
                    raise print("No existen archivos .dcm en el directorio")

                for f in glob.glob(path):
                    print(f)
                    print(f.split("/")[-1])
                    self.crear_vista_data(f)

                self.posicion_lista = len(self.lista_imagenes) - 1
                self.cargar_y_mostrar_images(self.lista_imagenes[self.posicion_lista])
                self.mostrar_imagen_8_bits(self.imagecv_8_bits_displayed)
                self.mostrar_imagen_16_bits(self.imagecv_16_bits_displayed)

                # Mostrar botones para navegar entre imágenes
                self.boton_anterior.show()
                self.boton_eliminar_foto.show()
                self.boton_siguiente.show()
                self.boton_eliminar_todas_fotos.show()

        elif response == Gtk.ResponseType.CANCEL:
            print("Cancel clicked")
            self.boton_anterior.hide()
            self.boton_eliminar_foto.hide()
            self.boton_siguiente.hide()
            self.boton_eliminar_todas_fotos.hide()

        dialog.destroy()

#----------------------------------------------------------------------------------------------------------------------#

#---------------------------------------------- METODOS PARA WINDOWING ------------------------------------------------#

    # Metodos que calculan y obtienen los valores de los pixeles despues de modificar el window_center o el window_width
    def calcular_windowing_imagen_8_bits(self, image, window_center, window_width):
        # Calcular los límites del rango de píxeles
        min_value = window_center - (window_width / 2)
        max_value = window_center + (window_width / 2)

        # Aplicar windowing a la imagen
        windowed_image = np.clip((image - min_value) / window_width * 255, 0, 255).astype(np.uint8)
        return windowed_image

    def calcular_windowing_imagen_16_bits(self, image, window_center, window_width):
        # Calcular los límites del rango de píxeles
        min_value = window_center - (window_width / 2)
        max_value = window_center + (window_width / 2)

        # Aplicar windowing a la imagen
        windowed_image = np.clip((image - min_value) / window_width * 65535, 0, 65535).astype(np.uint16)
        return windowed_image

#----------------------------------------------------------------------------------------------------------------------#

#--------------------------------------- METODOS DE PARA LOS BOTONES INTERFAZ -----------------------------------------#

    def evento_boton_anterior(self, widget):
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

    def evento_boton_siguiente(self, widget):

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

    def evento_boton_eliminar_foto_actual(self, widget):

        self.windowing_center_8_bits = 127
        self.windowing_width_8_bits = 255
        self.windowing_center_16_bits = 32767
        self.windowing_width_16_bits = 65535

        if len(self.lista_imagenes) == 0:
            raise Exception("La lista esta vacia")

        if self.posicion_lista < len(self.lista_imagenes):

            del self.lista_imagenes[self.posicion_lista]
            self.controlador.borrar_dicom_cargado_en_posicion(self.posicion_lista)

            # Verificar si la lista tiene elementos después de borrar
            if self.lista_imagenes:
                # Ajustar la posición si es necesario
                if self.posicion_lista >= len(self.lista_imagenes):
                    self.posicion_lista -= 1

                # En caso de que haya solo una imagen escondemos los botones para cambiar las fotos
                if len(self.lista_imagenes) == 1:
                    self.boton_anterior.hide()
                    self.boton_siguiente.hide()

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

    def evento_boton_eliminar_lista_fotos(self, widget):
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

        self.controlador.borrar_todos_los_dicom_cargados_de_la_lista()

        self.boton_anterior.hide()
        self.boton_eliminar_foto.hide()
        self.boton_siguiente.hide()
        self.boton_eliminar_todas_fotos.hide()
        return True

#----------------------------------------------------------------------------------------------------------------------#

#----------------------------------- LOGICA ACCIONES (ZOOM, PANNING, WINDOWING) ---------------------------------------#

    def evento_presionar_tecla_z_zoom(self, widget, event):
        if event.keyval == Gdk.KEY_z:
            if not self.zoom_teclado:
                self.zoom_teclado = True
                print("Activado Zoom")
            else:
                self.zoom_teclado = False
                print("Desactivado Zoom")
            self.toolbar.zoom()

    def evento_presionar_tecla_x_panning(self, widget, event):
        if event.keyval == Gdk.KEY_x:
            if not self.panning_teclado:
                self.panning_teclado = True
                print("Activado Pannning")
            else:
                self.panning_teclado = False
                print("Desactivado Panning")
            self.toolbar.pan()

    #------------------ EVENTOS WINDOWING RATON -----------------
    def evento_presionado_boton_secundario_raton_windowing(self, widget, event):
        if event.button == Gdk.BUTTON_SECONDARY:
            self.value_windowing_active = True

    def evento_liberado_boton_secundario_raton_windowing(self, widget, event):
        if event.button == Gdk.BUTTON_SECONDARY:
            self.value_windowing_active = False

    #------------------------------------------------------------

    #------------------- EVENTOS PANNING RATON-------------------
    def evento_presionado_boton_atras_raton_panning(self, widget, event):
        if event.button == 4:
            self.toolbar.pan()

    def evento_liberado_boton_atras_raton_panning(self, widget, event):
        if event.button == 4:
            self.toolbar.pan()

    #------------------------------------------------------------

    #-------------------- EVENTOS ZOOM RATON --------------------
    def evento_presionado_boton_siguiente_raton_zoom(self, widget, event):
        if event.button == 5:
            self.toolbar.zoom()

    def evento_liberado_boton_siguiente_raton_zoom(self, widget, event):
        if event.button == 5:
            self.toolbar.zoom()

    #------------------------------------------------------------

    def evento_checkbutton_windowing(self, button):
        if button.get_active():
            self.value_windowing_active = True
            self.entry_numero_window_center.show()
            self.entry_numero_window_width.show()
        else:
            self.value_windowing_active = False
            self.entry_numero_window_center.hide()
            self.entry_numero_window_width.hide()
        print("Windowing permanente ", self.value_windowing_active)

    def evento_entry_cambiado_valor_window_center(self, entry):
        # Esta función se ejecutará cada vez que el contenido de la entrada cambie
        try:
            # Convertir el texto de la entrada a int
            nuevo_valor = int(entry.get_text())
            if (nuevo_valor > 65535):
                nuevo_valor = 65535
            elif (nuevo_valor < 0):
                nuevo_valor = 0
            self.windowing_center_16_bits = nuevo_valor
            self.aplicar_windowing_viewport_16_bits()
        except ValueError:
            # Manejar el caso en el que el texto introducido no sea un número válido
            pass

    def evento_entry_cambiado_valor_window_width(self, entry):
        # Esta función se ejecutará cada vez que el contenido de la entrada cambie
        try:
            # Convertir el texto de la entrada a int
            nuevo_valor = int(entry.get_text())
            if (nuevo_valor > 65535):
                nuevo_valor = 65535
            elif (nuevo_valor < 0):
                nuevo_valor = 0
            self.windowing_width_16_bits = nuevo_valor
            self.aplicar_windowing_viewport_16_bits()
        except ValueError:
            # Manejar el caso en el que el texto introducido no sea un número válido
            pass

    def sincronizar_valores_windowing_8_bits(self):
        value_center_16_bits = self.windowing_center_16_bits
        value_width_16_bits = self.windowing_width_16_bits

        percentage = value_center_16_bits / 65535 * 100
        self.windowing_center_8_bits = round(percentage * 255 / 100)
        print("Valor window center de la imagen de 8 bits: ", self.windowing_center_8_bits)
        self.aplicar_windowing_viewport_8_bits()

        percentage = value_width_16_bits / 65535 * 100
        self.windowing_width_8_bits = round(percentage * 255 / 100)
        print("Valor window width de la imagen de 8 bits: ", self.windowing_width_8_bits)
        self.aplicar_windowing_viewport_8_bits()

    def evento_boton_primario_presionado_windowing(self, viewport, event):
        if self.value_windowing_active:
            if event.button == Gdk.BUTTON_PRIMARY:  # Botón izquierdo del ratón
                self.start_y = event.y
                self.start_x = event.x
                self.start_window_center = self.windowing_center_16_bits
                self.start_window_width = self.windowing_width_16_bits
                self.mouse_pressed = True

    def evento_boton_primario_liberado_windowing(self, viewport, event):
        if self.value_windowing_active:
            if event.button == Gdk.BUTTON_PRIMARY:  # Botón izquierdo del ratón
                self.aplicar_windowing_viewport_16_bits()
                self.mouse_pressed = False

    def aplicar_windowing_viewport_8_bits(self):
        # Aplicar windowing a la imagen cargada
        if hasattr(self, 'imagecv_8_bits'):
            self.imagecv_8_bits_displayed = self.calcular_windowing_imagen_8_bits(self.imagecv_8_bits, self.windowing_center_8_bits, self.windowing_width_8_bits)
            self.coordenadas_x_8_bits = self.ax_8_bits.get_xlim()
            self.coordenadas_y_8_bits = self.ax_8_bits.get_ylim()
            self.actualizar_imagen_8_bits(self.imagecv_8_bits_displayed, self.coordenadas_x_8_bits, self.coordenadas_y_8_bits)
        return False

    #Funcion encargada de calcular y aplicar los cambios en la imagen y propagarlos a la imagen de 8 bits de profundidad
    def aplicar_windowing_viewport_16_bits(self):
        # Obtener los valores de window_center y window_width de las barras de desplazamiento
        print("Valor window center de la imagen de 16 bits: ", self.windowing_center_16_bits)
        print("Valor window width de la imagen de 16 bits: ", self.windowing_width_16_bits)

        # Aplicar windowing a la imagen cargada
        if hasattr(self, 'imagecv_16_bits'):
            self.imagecv_16_bits_displayed = self.calcular_windowing_imagen_16_bits(self.imagecv_16_bits, self.windowing_center_16_bits, self.windowing_width_16_bits)
            self.coordenadas_x_16_bits = self.ax_16_bits.get_xlim()
            self.coordenadas_y_16_bits = self.ax_16_bits.get_ylim()
            self.actualizar_imagen_16_bits(self.imagecv_16_bits_displayed, self.coordenadas_x_16_bits, self.coordenadas_y_16_bits)

        self.sincronizar_valores_windowing_8_bits()
        return False

    def evento_movimiento_vertical_window_center(self, widget, event):
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

    def evento_movimiento_horizontal_window_width(self, widget, event):
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

