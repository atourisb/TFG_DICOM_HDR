import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf, Gdk
import glob
import os
from pathlib import Path

# Colocar segunda imagen y replicar movimientos conectando el segundo viewport con los mismos metodos que el otro viewport(?) creo que asi
# y mirar lo de las specs del pc y mostrarlo de alguna forma

class ModeloVista:

    """Atributos de tipo de dato usado para guardar la info extraida del DICOM"""
    original_pixbuf: GdkPixbuf.Pixbuf
    displayed_pixbuf: GdkPixbuf.Pixbuf
    image: Gtk.Image

    def __init__(self, file_path):
        self.original_pixbuf = GdkPixbuf.Pixbuf.new_from_file(file_path)
        self.displayed_pixbuf = GdkPixbuf.Pixbuf.new_from_file(file_path)
        self.image = Gtk.Image.new_from_pixbuf(self.displayed_pixbuf)

    def get_original_pixbuf(self):
        return self.original_pixbuf

    def get_displayed_pixbuf(self):
        return self.displayed_pixbuf

    def get_image(self):
        return self.image
class ImageWindow(Gtk.Window):

    def __init__(self):
        self.lista_imagenes = []
        Gtk.Window.__init__(self, title="Aplicacion")
        self.set_default_size(1600, 1000)
        self.set_border_width(20)

        # Crear una caja principal
        self.box_principal = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.add(self.box_principal)  # Agregar la caja a la ventana
        self.box_principal.set_homogeneous(False)
        self.box_principal.set_spacing(20)

        # Crear una caja secundaria para botones
        self.box_botones = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.box_principal.pack_start(self.box_botones, False, False, 0)
        self.box_botones.set_homogeneous(True)
        self.box_botones.set_spacing(0)

        self.button1 = Gtk.Button(label="Elegir Fichero")
        self.button1.connect("clicked", self.on_file_clicked)
        self.box_botones.pack_start(self.button1, False, False, 10)

        self.button2 = Gtk.Button(label="Elegir Carpeta")
        self.button2.connect("clicked", self.on_folder_clicked)
        self.box_botones.pack_start(self.button2, False, False, 10)

        self.button3 = Gtk.Button(label="Anterior Foto")
        self.button3.connect("clicked", self.on_button_anterior_clicked)
        self.button3.hide()
        self.box_botones.pack_start(self.button3, False, False, 10)

        self.button4 = Gtk.Button(label="Eliminar Foto Actual")
        self.button4.connect("clicked", self.on_button_delete_foto_actual_clicked)
        self.button4.hide()
        self.box_botones.pack_start(self.button4, False, False, 10)

        self.button5 = Gtk.Button(label="Siguiente Foto")
        self.button5.connect("clicked", self.on_button_siguiente_clicked)
        self.button5.hide()
        self.box_botones.pack_start(self.button5, False, False, 10)

        self.button_delete = Gtk.Button()
        self.button_delete.connect("clicked", self.on_button_delete_lista_clicked)
        self.button_delete.hide()
        self.button_delete.set_image(Gtk.Image.new_from_icon_name("user-trash-symbolic", Gtk.IconSize.BUTTON))
        self.box_botones.pack_start(self.button_delete, False, False, 10)

        self.original_pixbuf = None
        self.displayed_pixbuf = None

        # Crear una caja secundaria para visualizar la imagen
        self.box2 = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.box_principal.pack_start(self.box2, True, True, 0)
        self.box2.set_homogeneous(True)
        self.box2.set_spacing(0)

        # Create an image widget to display the image
        self.scrolledwindow = Gtk.ScrolledWindow() #added
        self.viewport = Gtk.Viewport() #added
        self.scrolledwindow.add(self.viewport)
        self.vadjustment1 = self.viewport.get_vadjustment()
        self.hadjustment1 = self.viewport.get_hadjustment()
        self.box2.pack_start(self.scrolledwindow, True, True, 0)

        # Segunda Imagen ---------------------------------------------
        self.original_pixbuf2 = None
        self.displayed_pixbuf2 = None

        self.scrolledwindow2 = Gtk.ScrolledWindow() #added
        self.viewport2 = Gtk.Viewport() #added
        self.scrolledwindow2.add(self.viewport2)
        self.vadjustment2 = self.viewport2.get_vadjustment()
        self.hadjustment2 = self.viewport2.get_hadjustment()
        self.box2.pack_start(self.scrolledwindow2, True, True, 0)

        #Acaba la segunda imagen ---------------------------------------------

        # Connect
        self.connect("destroy", Gtk.main_quit)
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

        self.viewport.set_events(Gdk.EventMask.BUTTON_PRESS_MASK | Gdk.EventMask.POINTER_MOTION_MASK)
        self.viewport2.set_events(Gdk.EventMask.BUTTON_PRESS_MASK | Gdk.EventMask.POINTER_MOTION_MASK)

        # Factor de zoom inicial
        self.zoom_factor = 1.0
        self.ratio = 3.
        self.posicion_lista = 0
        self.panning = False

        # Mostrar todos los elementos de la ventana
        self.show_all()
        self.button3.hide()
        self.button4.hide()
        self.button5.hide()
        self.button_delete.hide()

    def scale_image(self):
        self.displayed_pixbuf = self.original_pixbuf.scale_simple(self.original_pixbuf.get_width() * self.ratio,
                                                                  self.original_pixbuf.get_height() * self.ratio, 2)

    def load_image(self, file_path):
        try:
            self.original_pixbuf = GdkPixbuf.Pixbuf.new_from_file(file_path)
            self.displayed_pixbuf = GdkPixbuf.Pixbuf.new_from_file(file_path)
            self.image = Gtk.Image.new_from_pixbuf(self.displayed_pixbuf)  # added
            self.image2 = Gtk.Image.new_from_pixbuf(self.displayed_pixbuf)  # added
            # scaled_pixbuf = pixbufdelaimagen.scale_simple(600, 400, GdkPixbuf.InterpType.BILINEAR)
            # image.set_from_pixbuf(scaled_pixbuf)
        except Exception as e:
            print("Error al cargar la imagen:", e)

    #movida para probar a ver si se puede desactivar temporalmente la sync de barras cuando hacemos paning
    def on_button_press_event(self, widget, event):
        if event.button == Gdk.BUTTON_PRIMARY:
            self.panning = True

    def on_button_release_event(self, widget, event):
        if event.button == Gdk.BUTTON_PRIMARY:
            self.panning = False

    def load_image_conobjeto(self, objeto):
        try:
            self.original_pixbuf = objeto.get_original_pixbuf()
            self.displayed_pixbuf = objeto.get_displayed_pixbuf()
            self.image = objeto.get_image()
            self.image2 = Gtk.Image.new_from_pixbuf(self.displayed_pixbuf)  # added
            #self.image2 = objeto.get_image()

            print(self.image)
            print(objeto.get_image())
            print("Numero elementos de la lista: ", len(self.lista_imagenes))
            print("Posicion de la Lista: ", self.posicion_lista)
            #self.image.set_from_pixbuf(pixbuf)

            self.scale_image()
            self.viewport.set_size_request(self.displayed_pixbuf.get_width(), self.displayed_pixbuf.get_height())
            self.viewport.add(self.image)
            self.viewport.show_all()

            self.viewport2.set_size_request(self.displayed_pixbuf.get_width(), self.displayed_pixbuf.get_height())
            self.viewport2.add(self.image2)
            self.viewport2.show_all()

        except Exception as e:
            print("Error al cargar la imagen:", e)

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
        self.load_image_conobjeto(self.lista_imagenes[self.posicion_lista])



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
        self.load_image_conobjeto(self.lista_imagenes[self.posicion_lista])

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
            self.load_image(dialog.get_filename())
            self.scale_image()
            self.viewport.set_size_request(self.displayed_pixbuf.get_width(), self.displayed_pixbuf.get_height())
            self.viewport.add(self.image)
            self.viewport.show_all()

            self.viewport2.set_size_request(self.displayed_pixbuf.get_width(), self.displayed_pixbuf.get_height())
            self.viewport2.add(self.image2)
            self.viewport2.show_all()

        elif response == Gtk.ResponseType.CANCEL:
            print("Cancel clicked")

        dialog.destroy()

    def add_filters(self, dialog):
        filter_text = Gtk.FileFilter()
        filter_text.set_name("Text files")
        filter_text.add_mime_type("text/plain")
        dialog.add_filter(filter_text)

        filter_py = Gtk.FileFilter()
        filter_py.set_name("Python files")
        filter_py.add_mime_type("text/x-python")
        dialog.add_filter(filter_py)

        filter_any = Gtk.FileFilter()
        filter_any.set_name("Any files")
        filter_any.add_pattern("*")
        dialog.add_filter(filter_any)

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
            self.load_image_conobjeto(self.lista_imagenes[self.posicion_lista])

        return True

    def cargar_image_multiple_lista(self, file_path):
        try:
            objetoFoto = ModeloVista(file_path)
            self.lista_imagenes.append(objetoFoto)

        except Exception as e:
            print("Error al cargar la imagen:", e)

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


            path = dialog.get_filename()+("/*.tiff")
            print(path)

            directorio, patron = os.path.split(path)
            print(directorio)
            directorio = Path(directorio)
            tiff_files = glob.glob(os.path.join(directorio, '*.tiff'))

            if not directorio.exists():
                raise print("funca pochillon no existe directorio")
            elif not tiff_files:
                raise print("Funca pocho no hay tiff")

            # self.print_directory()
            plots = []
            for f in glob.glob(path):
                print(f)
                print(f.split("/")[-1])
                filename = f.split("/")[-1]
                self.cargar_image_multiple_lista(f)

            self.posicion_lista = len(self.lista_imagenes) - 1
            self.load_image_conobjeto(self.lista_imagenes[self.posicion_lista])

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

    def on_scroll_event(self, widget, event):
        # Verificar si se está realizando un scroll hacia arriba o hacia abajo
        if (event.keyval == Gdk.KEY_Control_L or event.keyval == Gdk.KEY_Control_R) & event.direction == Gdk.ScrollDirection.UP:
            self.zoom_in()
        elif (event.keyval == Gdk.KEY_Control_L or event.keyval == Gdk.KEY_Control_R) & event.direction == Gdk.ScrollDirection.DOWN:
            self.zoom_out()

    def on_scroll_event_zoom(self, widget, event):
        # Verificar si se ha movido la rueda del ratón y si la tecla Ctrl está presionada
        if event.state & Gdk.ModifierType.CONTROL_MASK and event.direction in [Gdk.ScrollDirection.UP,
                                                                               Gdk.ScrollDirection.DOWN]:
            #self.viewport.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.NEVER)
            if event.direction == Gdk.ScrollDirection.UP:
                self.zoom_in()
            elif event.direction == Gdk.ScrollDirection.DOWN:
                self.zoom_out()

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

    def on_scroll_eventctrl(self, widget, event):
        # Handles zoom in / zoom out on Ctrl+mouse wheel
        accel_mask = Gtk.accelerator_get_default_mod_mask()
        if event.state & accel_mask == Gdk.ModifierType.CONTROL_MASK:
            direction = event.get_scroll_deltas()[2]
            if direction > 0:  # scrolling down -> zoom out
                self.zoom_out()
            else:
                self.zoom_in()

    def zoom_in(self):
        self.zoom_factor *= 1.1  # Factor de aumento del zoom
        self.update_image()

    def zoom_out(self):
        self.zoom_factor /= 1.1  # Factor de reducción del zoom
        self.update_image()

    def update_image(self):
        # Cargar la imagen original

        # Escalar la imagen según el factor de zoom
        scaled_width = int(self.original_pixbuf.get_width() * self.zoom_factor)
        scaled_height = int(self.original_pixbuf.get_height() * self.zoom_factor)
        displayed_pixbuf = self.original_pixbuf.scale_simple(scaled_width, scaled_height, GdkPixbuf.InterpType.BILINEAR)

        # Mostrar la imagen actualizada
        self.image.set_from_pixbuf(displayed_pixbuf)
        self.image2.set_from_pixbuf(displayed_pixbuf)

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

win = ImageWindow()
win.connect("destroy", Gtk.main_quit)
Gtk.main()
