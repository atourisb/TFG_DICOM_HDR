import cv2
from OpenGL.GL import *
from OpenGL.GLUT import *
import numpy as np
from PIL import Image
import glfw

class VistaOpenGl:

    def __init__(self, controlador):
        self.controlador = controlador
        self.angle = 0  # Ángulo de rotación inicial
        self.image_16_bits = None

        # Cargar la imagen de 16 bits sin normalizar
        file_path_16_bits = "/home/rainor/PycharmProjects/tfg/salida//output_image_16_bits_5.tiff"
        self.image_16_bits = cv2.imread(file_path_16_bits, cv2.IMREAD_UNCHANGED)

        self.image_16_bitsfloat = self.image_16_bits.astype(float)

        #No me deja si lo hago esto se cierra
        #self.image_16_bits = np.flip(self.image_16_bits)

        glutInit()
        glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA | GLUT_DEPTH)
        glutInitWindowSize(self.image_16_bits.shape[1], self.image_16_bits.shape[0])
        glutCreateWindow("Vista de Experimento con PyOpenGL")

        glClearColor(0.0, 0.0, 0.0, 1.0)
        glClearDepth(1.0)
        glEnable(GL_DEPTH_TEST)

        glutDisplayFunc(self.draw_image)
        glutIdleFunc(self.update)
        glutMainLoop()

    def update(self):
        self.angle += 0.5  # Incrementar el ángulo de rotación
        glutPostRedisplay()

    def draw_image(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        #Aplicar rotación
        # glTranslatef(self.image_16_bits.shape[1], self.image_16_bits.shape[0], 0)  # Mover al centro de la imagen
        # glRotatef(10, 0, 0, 1)  # Rotar alrededor del eje z
        # glTranslatef(-self.image_16_bits.shape[1], -self.image_16_bits.shape[0], 0)  # Mover de vuelta al origen

        # Representar la imagen
        glRasterPos2i(-1, -1)
        glDrawPixels(self.image_16_bits.shape[1], self.image_16_bits.shape[0], GL_RGB16F, GL_UNSIGNED_SHORT, self.image_16_bits)

        glutSwapBuffers()

# Ejemplo de uso
# controlador = Controlador()  # Reemplaza esto con tu propio controlador
# vista = VistaExperimento(controlador)
