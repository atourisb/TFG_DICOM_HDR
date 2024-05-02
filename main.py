from vista.vista import Vista
from modelo.modelo import Modelo
from controlador.controlador import Controlador
import os
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

def pausar_codigo():
    input('Press <ENTER> to continue')

def main():
    # Uso del MVC

    # Crear instancias de Modelo, Vista y Controlador
    modelo = Modelo()

    controlador = Controlador(modelo)

    vista = Vista(controlador)
    vista.connect("destroy", Gtk.main_quit)
    Gtk.main()

    #VERIFICACION PARA MOSTRAR LA IMAGEN QUE SE MUESTRA YA QUE DIGO EN EL COMENTARIO QUE LA 1-1002 ES LA QUE SE MUESTRA
    #DESPUES DEL BORRADO
    ruta4 = "/home/rainor/PycharmProjects/tfg/ImagenesDICOM/2-3.dcm"
    #ruta4 = "/home/rainor/PycharmProjects/tfg/ImagenesDICOM/casa"
    #ruta4 = "/home/rainor/PycharmProjects/tfg/ImagenesDICOM/TextFile.txt"

    #controlador.mostrar_ventana()

    #controlador.cargar_unico_dicom(ruta4)
    # Modificar los datos a través del controlador
    #controlador.transformar_ultimo_dicom_tiff_16_bits()

    #controlador.transformar_ultimo_dicom_tiff_8_bits()
    # Guardar los datos a traves del controlador
    #controlador.guardar_ultimo_dicom_tiff_16_bits()

    #controlador.guardar_ultimo_dicom_tiff_8_bits()
    # Verificar que la vista se actualice automáticamente
    #controlador.visualizar_ultimo_dicom()
    #vista.show_all()
    #vista = Vista()

    #---------------- PRUEBA DE GUARDO TODOS-----------------
    #PRUEBA ERROR DAR UNA POSICION NO VALIDA
    # ruta3 = "/home/rainor/PycharmProjects/tfg/ImagenesDICOM/*.dcm"
    # controlador.cargar_multiples_dicom(ruta3)
    # # Modificar los datos a través del controlador
    # controlador.transformar_todos_los_dicom()
    # # Verificar que la vista se actualice automáticamente
    # controlador.guardar_todos_los_dicom()
    # #se muestra el 1-1002

'''
    #---------------- PRUEBA DE EXCEPCIONES-----------------
    # PRUEBA ERROR DAR UNA POSICION NO VALIDA
    ruta3 = "/home/rainor/PycharmProjects/tfg/ImagenesDICOM/*.dcm"
    controlador.cargar_multiples_dicom(ruta3)
    # Modificar los datos a través del controlador
    controlador.transformar_todos_los_dicom()
    # Verificar que la vista se actualice automáticamente
    controlador.visualizar_dicom_en_posicion(12)
    controlador.borrar_dicom_cargado_en_posicion(12)
    #se muestra el 1-1002
    controlador.visualizar_dicom_en_posicion(12)


    # PRUEBAS CARGA DE UNA SOLA IMAGEN, MODIFICAR LA ULTIMA IMAGEN Y MOSTRAR LA ULTIMA IMAGEN
    ruta1 = "/home/rainor/PycharmProjects/tfg/ImagenesDICOM/2-1.dcm"
    controlador.cargar_unico_dicom(ruta1)
    # Modificar los datos a través del controlador
    controlador.transformar_ultimo_dicom()
    # Verificar que la vista se actualice automáticamente
    controlador.visualizar_ultimo_dicom()

    pausar_codigo()

    # PRUEBAS CARGA DE MULTIPLES IMAGENES Y BORRADO DE TODAS LAS IMAGENES MOSTRANDO LA LISTA DE IMAGENES CARGADAS
    ruta2 = "/home/rainor/PycharmProjects/tfg/ImagenesDICOM/*.dcm"
    controlador.cargar_multiples_dicom(ruta2)
    # Borrado de toda la lista
    controlador.mostrar_cantidad_de_dicom_cargados()
    controlador.borrar_todos_los_dicom_cargados_de_la_lista()
    controlador.mostrar_cantidad_de_dicom_cargados()

    pausar_codigo()

    # PRUEBAS BORRADO DE LA ULTIMA DESPUES DE BORRAR LA ULTIMA SE MUESTRA UNA DIFERENTE Y MOSTRAMOS LONGITUD DEL ARRAY
    ruta3 = "/home/rainor/PycharmProjects/tfg/ImagenesDICOM/*.dcm"
    controlador.cargar_multiples_dicom(ruta3)
    # Modificar los datos a través del controlador
    controlador.transformar_todos_los_dicom()
    # Verificar que la vista se actualice automáticamente
    controlador.mostrar_cantidad_de_dicom_cargados()
    controlador.visualizar_ultimo_dicom()
    # BORRAMOS LA ULTIMA
    controlador.borrar_ultimo_dicom_cargado()
    controlador.mostrar_cantidad_de_dicom_cargados()
    controlador.visualizar_ultimo_dicom()

    pausar_codigo()
    # BORRADO PARA LA SIGUIENTE PRUEBA
    controlador.borrar_todos_los_dicom_cargados_de_la_lista()


    # PRUEBA DE MOSTRAR IMAGEN POR POSICION Y BORRADO POR POSICION
    ruta3 = "/home/rainor/PycharmProjects/tfg/ImagenesDICOM/*.dcm"
    controlador.cargar_multiples_dicom(ruta3)
    # Modificar los datos a través del controlador
    controlador.transformar_todos_los_dicom()
    # Verificar que la vista se actualice automáticamente
    controlador.visualizar_dicom_en_posicion(2)
    controlador.borrar_dicom_cargado_en_posicion(2)
    #se muestra el 1-1002
    controlador.visualizar_dicom_en_posicion(2)

    pausar_codigo()
    # BORRADO PARA LA SIGUIENTE PRUEBA
    controlador.borrar_todos_los_dicom_cargados_de_la_lista()


    # VERIFICACION PARA MOSTRAR LA IMAGEN QUE SE MUESTRA YA QUE DIGO EN EL COMENTARIO QUE LA 1-1002 ES LA QUE SE MUESTRA
    #DESPUES DEL BORRADO
    ruta4 = "/home/rainor/PycharmProjects/tfg/ImagenesDICOM/1-1002.dcm"
    controlador.cargar_unico_dicom(ruta4)
    # Modificar los datos a través del controlador
    controlador.transformar_ultimo_dicom()
    # Verificar que la vista se actualice automáticamente
    controlador.visualizar_ultimo_dicom()

    pausar_codigo()
    # BORRADO PARA LA SIGUIENTE PRUEBA
    controlador.borrar_todos_los_dicom_cargados_de_la_lista()


    # PRUEBAS CARGA DE MULTIPLES IMAGENES, MODIFICAR Y MOSTRAR TODAS LAS IMAGENES
    ruta5 = "/home/rainor/PycharmProjects/tfg/ImagenesDICOM/*.dcm"
    controlador.cargar_multiples_dicom(ruta5)
    # Modificar los datos a través del controlador
    controlador.transformar_todos_los_dicom()
    # Verificar que la vista se actualice automáticamente
    controlador.visualizar_todos_los_dicom()

    pausar_codigo()
    # BORRADO PARA LA SIGUIENTE PRUEBA
    controlador.borrar_todos_los_dicom_cargados_de_la_lista()


    # PRUEBAS DE CONVERTIR LA IMAGEN EN CIERTA POSICION SIN CONVERTIR EL RESTO
    #no se si esto tiene alguna utilidad
    ruta6 = "/home/rainor/PycharmProjects/tfg/ImagenesDICOM/*.dcm"
    controlador.cargar_multiples_dicom(ruta6)
    controlador.visualizar_dicom_en_posicion(2)
    # DE ESTA FORMA SE VE QUE LA RESULTANTE CUANDO MUESTRO DE TRANSFORMAR TIENEN LOS MISMOS VALORES EN LAS DOS IMAGENES
    # PERO DESPUES DE CONVERTIRLA TIENEN VALORES DIFERENTES CUANDO VUELVO A MOSTRAR
    # Modificar los datos a través del controlador
    controlador.transformar_dicom_en_posicion(2)
    # Verificar que la vista se actualice automáticamente
    controlador.visualizar_dicom_en_posicion(2)
'''


if __name__ == "__main__":
    main()
