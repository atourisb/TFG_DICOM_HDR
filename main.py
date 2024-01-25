from vista.vista import Vista
from modelo.modelo import Modelo
from controlador.controlador import Controlador
import keyboard

def pausar_codigo():
    input('Press <ENTER> to continue')

def main():
    # Uso del MVC

    # Crear instancias de Modelo, Vista y Controlador
    modelo = Modelo()
    vista = Vista()
    controlador = Controlador(modelo, vista)

    # Inicializar la vista con los datos del modelo
    #controlador.actualizar_vista()

    #PRUEBAS CARGA DE UNA SOLA IMAGEN, MODIFICAR LA ULTIMA IMAGEN Y MOSTRAR LA ULTIMA IMAGEN
    ruta1 = "/home/rainor/PycharmProjects/tfg/ImagenesDICOM/2-1.dcm"
    controlador.cargar_imagen(ruta1)
    # Modificar los datos a través del controlador
    controlador.convertir_imagen_ultimo()
    # Verificar que la vista se actualice automáticamente
    controlador.mostrar_imagen_la_ultima()

    pausar_codigo()

    #PRUEBAS CARGA DE MULTIPLES IMAGENES Y BORRADO DE TODAS LAS IMAGENES MOSTRANDO LA LISTA DE IMAGENES CARGADAS
    ruta2 = "/home/rainor/PycharmProjects/tfg/ImagenesDICOM/*.dcm"
    controlador.cargar_multiples_imagen(ruta2)
    # Borrado de toda la lista
    controlador.show_lista()
    controlador.borrar_toda_la_lista()
    controlador.show_lista()

    pausar_codigo()

    #PRUEBAS BORRADO DE LA ULTIMA DESPUES DE BORRAR LA ULTIMA SE MUESTRA UNA DIFERENTE Y MOSTRAMOS LONGITUD DEL ARRAY
    ruta3 = "/home/rainor/PycharmProjects/tfg/ImagenesDICOM/*.dcm"
    controlador.cargar_multiples_imagen(ruta3)
    # Modificar los datos a través del controlador
    controlador.convertir_imagen_todos()
    # Verificar que la vista se actualice automáticamente
    controlador.show_lista()
    controlador.mostrar_imagen_la_ultima()
    #BORRAMOS LA ULTIMA
    controlador.borrar_ultimo()
    controlador.show_lista()
    controlador.mostrar_imagen_la_ultima()

    pausar_codigo()
    #BORRADO PARA LA SIGUIENTE PRUEBA
    controlador.borrar_toda_la_lista()


    #PRUEBA DE MOSTRAR IMAGEN POR POSICION Y BORRADO POR POSICION
    ruta3 = "/home/rainor/PycharmProjects/tfg/ImagenesDICOM/*.dcm"
    controlador.cargar_multiples_imagen(ruta3)
    # Modificar los datos a través del controlador
    controlador.convertir_imagen_todos()
    # Verificar que la vista se actualice automáticamente
    controlador.mostrar_imagen_posicion(2)
    controlador.borrar_posicion(2)
    #se muestra el 1-1002
    controlador.mostrar_imagen_posicion(2)

    pausar_codigo()
    # BORRADO PARA LA SIGUIENTE PRUEBA
    controlador.borrar_toda_la_lista()


    #VERIFICACION PARA MOSTRAR LA IMAGEN QUE SE MUESTRA YA QUE DIGO EN EL COMENTARIO QUE LA 1-1002 ES LA QUE SE MUESTRA
    #DESPUES DEL BORRADO
    ruta4 = "/home/rainor/PycharmProjects/tfg/ImagenesDICOM/1-1002.dcm"
    controlador.cargar_imagen(ruta4)
    # Modificar los datos a través del controlador
    controlador.convertir_imagen_ultimo()
    # Verificar que la vista se actualice automáticamente
    controlador.mostrar_imagen_la_ultima()

    pausar_codigo()
    # BORRADO PARA LA SIGUIENTE PRUEBA
    controlador.borrar_toda_la_lista()


    #PRUEBAS CARGA DE MULTIPLES IMAGENES, MODIFICAR Y MOSTRAR TODAS LAS IMAGENES
    ruta5 = "/home/rainor/PycharmProjects/tfg/ImagenesDICOM/*.dcm"
    controlador.cargar_multiples_imagen(ruta5)
    # Modificar los datos a través del controlador
    controlador.convertir_imagen_todos()
    # Verificar que la vista se actualice automáticamente
    controlador.mostrar_imagen_todos()

    pausar_codigo()
    # BORRADO PARA LA SIGUIENTE PRUEBA
    controlador.borrar_toda_la_lista()


    #PRUEBAS DE CONVERTIR LA IMAGEN EN CIERTA POSICION SIN CONVERTIR EL RESTO
    #no se si esto tiene alguna utilidad
    ruta6 = "/home/rainor/PycharmProjects/tfg/ImagenesDICOM/*.dcm"
    controlador.cargar_multiples_imagen(ruta6)
    controlador.mostrar_imagen_posicion(2)
    #DE ESTA FORMA SE VE QUE LA RESULTANTE CUANDO MUESTRO DE TRANSFORMAR TIENEN LOS MISMOS VALORES EN LAS DOS IMAGENES
    #PERO DESPUES DE CONVERTIRLA TIENEN VALORES DIFERENTES CUANDO VUELVO A MOSTRAR
    # Modificar los datos a través del controlador
    controlador.convertir_imagen_posicion(2)
    # Verificar que la vista se actualice automáticamente
    controlador.mostrar_imagen_posicion(2)


if __name__ == "__main__":
    main()
