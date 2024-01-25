import matplotlib.pyplot as plt

# Vista

class Vista:
    def mostrar_dicom_original_y_dicom_transformado(self, dicom):

        plt.figure()
        plt.imshow(dicom.pixel_data_original, cmap='gray')
        plt.figure()
        plt.imshow(dicom.pixel_data_modified, cmap='gray')
        plt.show()

    def mostrar_cantidad_de_la_lista(self, lista):
        print(len(lista))
