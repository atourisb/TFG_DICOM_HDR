import glob
import os

import matplotlib.pyplot as plt
import numpy as np
import pydicom
import subprocess
import imageio

def print_directory():
    # Especifica el directorio que deseas listar
    directorio = "/home/rainor/PycharmProjects/tfg/Imagenes DICOM/"
    # Construye el comando
    comando = f"ls -l {directorio}"
    # Ejecuta el comando y captura la salida
    resultado = subprocess.run(comando, shell=True, check=True, stdout=subprocess.PIPE, text=True)
    # Imprime la salida del comando
    print(resultado.stdout)

def get_dicom_field(ds, tag):
    # Accede al campo utilizando la etiqueta numérica
    field_value = ds[tag]

    return field_value

def plot_multiple_images():
    class IndexTracker(object):
        def __init__(self, ax, X):
            self.ax = ax
            ax.set_title('Scroll to Navigate through the DICOM Image Slices')

            self.X = X
            rows, cols, self.slices = X.shape
            self.ind = self.slices//2

            self.im = ax.imshow(self.X[:, :, self.ind], cmap='gray') #, cmap='gray'
            self.update()

        def onscroll(self, event):
            print("%s %s" % (event.button, event.step))
            if event.button == 'up':
                self.ind = (self.ind + 1) % self.slices
            else:
                self.ind = (self.ind - 1) % self.slices
            self.update()

        def update(self):
            self.im.set_data(self.X[:, :, self.ind])
            ax.set_ylabel('Slice Number: %s' % self.ind)
            self.im.axes.figure.canvas.draw()

    fig, ax = plt.subplots(1,1)

    print_directory()

    plots = []

    for f in glob.glob("/home/rainor/PycharmProjects/tfg/Imagenes DICOM/*.dcm"):
        print(f.split("/")[-1])
        filename = f.split("/")[-1]
        ds = pydicom.dcmread(filename)
        pixel_data = ds.pixel_array

        print(type(ds.pixel_array))

        #resolucion
        resolution = (ds.Rows, ds.Columns)
        print(resolution)

        #(0x0028, 0x0106) (0x0028, 0x0107)

        #Con Esto puedes saber si un campo esta en el ds
        #print ([0x0028, 0x0106] in ds)
        #tagSmallestImagePixelValue = [0x0028, 0x0106]
        #tagLargestImagePixelValue = [0x0028, 0x0107]
        #min_pixel_value = get_dicom_field(ds, tagSmallestImagePixelValue)
        #max_pixel_value = get_dicom_field(ds, tagLargestImagePixelValue)
        min_pixel_value = ds.pixel_array.min()
        max_pixel_value = ds.pixel_array.max()
        print("Minimo valor ", min_pixel_value ," Maximo valor ", max_pixel_value)

        #primero intento de que no salga en negro
        pixel_data_prueba = (ds.pixel_array*100)/65535
        output_path16 = "output_imagemain16.tiff"
        #imageio.imsave(output_path16, pixel_data_prueba, format='TIFF')


        #Esta linea lo que hace es transformar los valores de positivos a negativos pero no se porque prefiere tener el pixel data en valores por debajo de 0
        pixel_data = pixel_data*1+(-1024)
        plots.append(pixel_data)

        width, height = ds.Rows, ds.Columns
        data = np.random.randint(min_pixel_value, max_pixel_value, size=(width, height), dtype=np.uint32)

        # Especificar el nombre del archivo TIFF
        output_name = "output_image.tiff"
        output_path = os.path.join("/home/rainor/PycharmProjects/tfg/", output_name)

        # Guardar la imagen como TIFF
        imageio.imsave(output_path, pixel_data, format='tiff')
        print(f"Imagen TIFF guardada en: {output_path}")

        #print(f"Imagen TIFF guardada en: {output_path}")

    y = np.dstack(plots)

    tracker = IndexTracker(ax, y)

    fig.canvas.mpl_connect('scroll_event', tracker.onscroll)
    plt.figure()
    plt.imshow(pixel_data)
    plt.show()

def main():
    plot_multiple_images()

if __name__ == "__main__":
    main()
