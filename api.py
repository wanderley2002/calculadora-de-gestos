import cv2 
import mediapipe as mp
import math

camera = cv2.VideoCapture(0)

base_options = mp.tasks.BaseOptions
vision_running_mode = mp.tasks.vision.RunningMode

# Variáveis da calculadora
numero_1 = None
operador = None
numero_2 = None
resultado = None

gesto_anterior = None
frame_gesto = 0
frames_necessarios = 15
gesto_bloqueado = False

# Função para zerar a calculadora no clique do mouse
def zerar_calculadora(event, x, y, flags, param):
    global numero_1, operador, numero_2, resultado, gesto_bloqueado
    if event == cv2.EVENT_LBUTTONDOWN:
        numero_1 = None
        operador = None
        numero_2 = None
        resultado = None
        gesto_bloqueado = False
        print("Calculadora zerada!")

# Função para calcular distância euclidiana entre dois pontos
def distancia(pontos1, pontos2):
    x1, y1 = pontos1.x, pontos1.y
    x2, y2 = pontos2.x, pontos2.y
    distancia_x = x1 - x2
    distancia_y = y1 - y2
    return math.sqrt(distancia_x ** 2 + distancia_y ** 2)

# Função para contar os dedos levantados
def contar_dedos(landmarks):
    dedos = 0
    if landmarks[8].y < landmarks[6].y:
        dedos += 1
    if landmarks[12].y < landmarks[10].y:
        dedos += 1
    if landmarks[16].y < landmarks[14].y:
        dedos += 1
    if landmarks[20].y < landmarks[18].y:
        dedos += 1
    if landmarks[4].x < landmarks[3].x:
        dedos += 1
    return dedos

# Função para detectar o gesto de "joia" (legal / thumbs up)
def detectar_joia(landmarks):
    polegar_para_cima = landmarks[4].y < landmarks[3].y 
    medio_dobrado = landmarks[12].y > landmarks[10].y
    anelar_dobrado = landmarks[16].y > landmarks[14].y
    mindinho_dobrado = landmarks[20].y > landmarks[18].y

    if polegar_para_cima and medio_dobrado and anelar_dobrado and mindinho_dobrado:
        return True 
    return False

# Função para detectar o gesto de cruz
def detectar_cruz(hand_landmarks):
    pass