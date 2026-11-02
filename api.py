import cv2 
import mediapipe as mp
import math

camera = cv2.VideoCapture(0)

base_options = mp.tasks.BaseOptions
vision_running_mode = mp.tasks.vision.RunningMode


//variaveis da calculdora

numero_1 = None
operador = None
numero_2 = None
resultado = None

gesto-anterior = None
frame_gesto = 0
frames_necessarios = 15
gesto_bloqueado = False

//funçao para zerar a calculadora

def zerar_calculadora(event,x,y,flags,param):
    global numero_1, operador, numero_2, resultado
    if event == cv2.EVENT_LBUTTONDOWN:
        numero_1 = None
        operador = None
        numero_2 = None
        resultado = None
        gesto_bloqueado = False

        print("Calculadora zerada!")


        def distancia(pontos1, pontos2):
            
            x1 = pontos1.x
            y1 = pontos1.y

            x2 = pontos2.x
            y2 = pontos2.y

            distancia_x = x1 - x2
            distancia_y = y1 - y2
            return math.sqrt(distancia_x ** 2 + distancia_y ** 2)


                //funcao para contar os dedos

                if landmarks[8].y < landmarks[6].y:
                    dedos += 1

                    if landdmarks[12].y < landmarks[10].y:
                        dedos += 1

                        if landmarks[16].y < landmarks[14].y:
                            dedos += 1

                            if landmarks[20].y < landmarks[18].y:
                                dedos += 1

                                if landmarks[4].x < landmarks[3].x:
                                    dedos += 1

                                    return dedos


                                    def detectar_joia(landmarks);
                                    polegar_para_cima = landmarks[4].y <landmarks[3].y 
                                    medio_dobrado = landmarks[12].y > landmarks[10].y
                                    anelar_dobrado = landmarks[16].y > landmarks[14].y
                                    mindinho_dobrado = landmarks[20].y > landmarks[18].y

                                    if(´polegar_para_cima and medio_dobrado and anelar_dobrado and mindinho_dobrado):
                                        return True 

                                        return False

                                        def detectar_cruz(hand_landmarks)
                            


