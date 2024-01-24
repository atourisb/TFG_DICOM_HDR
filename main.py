from vista.vista import Vista
from modelo.modelo import Modelo
from modelo.dicom_data import DicomData
from controlador.controlador import Controlador
from utils.dicom_utils import DicomUtils

def main():
    # Uso del MVC

    #Esto esta mal ya que no tiene que tener acceso a utils solo deberia tener acceso al modelo y la vista y despues
    #Borrar esto esto solo es para probar que lo que hice del controlador funciona, pensar mejor todo lo que tiene que
    #Ver con el modelo y la organizacion del proyecto
    ruta = "/home/rainor/PycharmProjects/tfg/ImagenesDICOM/2-2.dcm"


    # Crear instancias de Modelo, Vista y Controlador
    modelo = Modelo()
    vista = Vista()
    controlador = Controlador(modelo, vista)

    # Inicializar la vista con los datos del modelo
    #controlador.actualizar_vista()

    #PRUEBAS CARGA DE UNA SOLA IMAGEN, MODIFICAR LA ULTIMA IMAGEN Y MOSTRAR LA ULTIMA IMAGEN
    #ruta3 = "/home/rainor/PycharmProjects/tfg/ImagenesDICOM/2-1.dcm"
    #controlador.cargar_imagen(ruta3)
    # Modificar los datos a través del controlador
    #controlador.convertir_imagen_ultimo()
    # Verificar que la vista se actualice automáticamente
    #controlador.mostrar_imagen_la_ultima()



    #PRUEBAS CARGA DE MULTIPLES IMAGENES Y BORRADO DE TODAS LAS IMAGENES
    # ruta1 = "/home/rainor/PycharmProjects/tfg/ImagenesDICOM/*.dcm"
    #controlador.cargar_multiples_imagen(ruta1)
    # Borrado de toda la lista
    # controlador.show_lista()
    #controlador.borrar_toda_la_lista()
    #controlador.show_lista()



    #PRUEBAS BORRADO DE LA ULTIMA DESPUES DE BORRAR LA ULTIMA SE MUESTRA DE DIFERENTE FORMA MOSTRAMOS LONGITUD DEL ARRAY
    #ruta2 = "/home/rainor/PycharmProjects/tfg/ImagenesDICOM/*.dcm"
    #controlador.cargar_multiples_imagen(ruta2)
    # Modificar los datos a través del controlador
    #controlador.convertir_imagen_todos()
    # Verificar que la vista se actualice automáticamente
    # controlador.show_lista()
    #controlador.mostrar_imagen_la_ultima()
    #BORRAMOS LA ULTIMA
    # controlador.borrar_ultimo()
    # controlador.show_lista()
    # controlador.mostrar_imagen_la_ultima()



    # controlador.borrar_toda_la_lista()


    #pruebas posiciones
    #ruta3 = "/home/rainor/PycharmProjects/tfg/ImagenesDICOM/*.dcm"
    #controlador.cargar_multiples_imagen(ruta3)
    # Modificar los datos a través del controlador
    #controlador.convertir_imagen_todos()
    # Verificar que la vista se actualice automáticamente
    #controlador.mostrar_imagen_posicion(2)
    #controlador.borrar_posicion(2)
    #se muestra el 1-1002
    #controlador.mostrar_imagen_posicion(2)

    #controlador.borrar_toda_la_lista()

    #prueba de ello es que si hago esto
    #TODO ESTO FUNCA DE PUTA MADRE NICE
    #ruta4 = "/home/rainor/PycharmProjects/tfg/ImagenesDICOM/1-1002.dcm"
    #controlador.cargar_imagen(ruta4)
    # Modificar los datos a través del controlador
    #controlador.convertir_imagen_ultimo()
    # Verificar que la vista se actualice automáticamente
    #controlador.mostrar_imagen_la_ultima()



    #controlador.borrar_toda_la_lista()



    #PRUEBAS CARGA DE MULTIPLES IMAGENES, MODIFICAR Y MOSTRAR TODAS LAS IMAGENES
    #ruta2 = "/home/rainor/PycharmProjects/tfg/ImagenesDICOM/*.dcm"
    #controlador.cargar_multiples_imagen(ruta2)
    # Modificar los datos a través del controlador
    #controlador.convertir_imagen_todos()
    # Verificar que la vista se actualice automáticamente
    #controlador.mostrar_imagen_todos()

    #BORRADO DE TODA LA LISTA PARA LA SIGUIENTE PRUEBA
    # controlador.borrar_toda_la_lista()



    #convertir_imagen_posicion
    #ruta2 = "/home/rainor/PycharmProjects/tfg/ImagenesDICOM/*.dcm"
    #controlador.cargar_multiples_imagen(ruta2)
    # controlador.mostrar_imagen_posicion(2)
    #DE ESTA FORMA SE VE QUE LA RESULTANTE CUANDO MUESTRO DE TRANSFORMAR TIENEN LOS MISMOS VALORES EN LAS DOS IMAGENES
    #PERO DESPUES DE CONVERTIRLA TIENEN VALORES DIFERENTES CUANDO VUELVO A MOSTRAR
    # Modificar los datos a través del controlador
    #controlador.convertir_imagen_posicion(2)
    # Verificar que la vista se actualice automáticamente
    #controlador.mostrar_imagen_posicion(2)


if __name__ == "__main__":
    main()
