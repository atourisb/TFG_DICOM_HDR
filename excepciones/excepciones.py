class ArchivoNoEncontradoError(Exception):
    def __init__(self, ruta):
        self.ruta = ruta
        super().__init__(f"'{ruta}' El archivo no se encontró en la ruta especificada.")

class NoEsArchivoError(Exception):
    def __init__(self, ruta):
        self.ruta = ruta
        super().__init__(f"'{ruta}' no es un archivo")

class ExtensionIncorrectaError(Exception):
    def __init__(self, extension):
        self.extension = extension
        super().__init__('El archivo de entrada no tiene la extension .dcm, debería ser un DICOM')

class DirectorioNoExisteError(Exception):
    def __init__(self, directorio):
        self.directorio = directorio
        super().__init__(f"El directorio '{directorio}' no existe.")

class ArchivosDCMNoEncontradosError(Exception):
    def __init__(self, directorio):
        self.directorio = directorio
        super().__init__(f"No se encontraron archivos .dcm en el directorio {directorio}.")

class ListaVaciaError(Exception):
    def __init__(self, mensaje="La lista está vacía."):
        self.mensaje = mensaje
        super().__init__(self.mensaje)

class PosicionInvalidaError(Exception):
    def __init__(self, posicion):
        self.posicion = posicion
        super().__init__(f"La posicion dada no es una posicion valida {posicion}.")