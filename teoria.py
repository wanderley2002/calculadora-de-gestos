import cv2
import mediapipe as mp
import math


# ============================================================
# CONFIGURAÇÃO DA CÂMERA
# ============================================================

camera = cv2.VideoCapture(0)


# ============================================================
# CONFIGURAÇÃO DO MEDIAPIPE
# ============================================================

base_options = mp.tasks.BaseOptions
vision_running_mode = mp.tasks.vision.RunningMode


# ============================================================
# VARIÁVEIS DA CALCULADORA
# ============================================================

numero_1 = None
# Aqui vai guardar o primeiro número que eu colocar com a mão


operador = None
# Aqui vai guardar o operador da conta
# Exemplo: "+"


numero_2 = None
# Aqui vai guardar o segundo número


resultado = None
# Aqui vai guardar o resultado da conta


# ============================================================
# CONTROLE DOS GESTOS
# ============================================================

gesto_anterior = None
# Guarda o último gesto reconhecido


frame_gesto = 0
# Conta quantos frames o mesmo gesto está aparecendo


frames_necessarios = 15
# O gesto precisa permanecer por 15 frames
# para ser aceito pela calculadora


gesto_bloqueado = False
# False = pode aceitar um gesto
# True = já aceitou o gesto atual


# ============================================================
# FUNÇÃO PARA ZERAR A CALCULADORA
# ============================================================

def zerar_calculadora(event, x, y, flags, param):

    global numero_1
    global operador
    global numero_2
    global resultado
    global gesto_bloqueado

    # Verifica se o usuário clicou com o botão esquerdo
    if event == cv2.EVENT_LBUTTONDOWN:

        # Área do botão RESET
        if 20 <= x <= 150 and 400 <= y <= 450:

            numero_1 = None
            operador = None
            numero_2 = None
            resultado = None
            gesto_bloqueado = False

            print("Calculadora zerada!")


# ============================================================
# FUNÇÃO PARA CALCULAR DISTÂNCIA ENTRE DOIS PONTOS
# ============================================================

def distancia(ponto1, ponto2):

    x1 = ponto1.x
    y1 = ponto1.y

    x2 = ponto2.x
    y2 = ponto2.y

    distancia_x = x1 - x2
    distancia_y = y1 - y2

    return math.sqrt(
        distancia_x ** 2 + distancia_y ** 2
    )


# ============================================================
# FUNÇÃO PARA CONTAR OS DEDOS
# ============================================================

def contar_dedos(landmarks):

    dedos = 0


    # --------------------------------------------------------
    # INDICADOR
    # --------------------------------------------------------

    if landmarks[8].y < landmarks[6].y:
        dedos += 1


    # --------------------------------------------------------
    # MÉDIO
    # --------------------------------------------------------

    if landmarks[12].y < landmarks[10].y:
        dedos += 1


    # --------------------------------------------------------
    # ANELAR
    # --------------------------------------------------------

    if landmarks[16].y < landmarks[14].y:
        dedos += 1


    # --------------------------------------------------------
    # MINDINHO
    # --------------------------------------------------------

    if landmarks[20].y < landmarks[18].y:
        dedos += 1


    # --------------------------------------------------------
    # POLEGAR
    # --------------------------------------------------------

    # Compara a posição horizontal do polegar.
    # Essa regra funciona melhor quando a palma está
    # aproximadamente virada para a câmera.

    if landmarks[4].x < landmarks[3].x:
        dedos += 1


    return dedos


# ============================================================
# DETECTAR JOIA
# ============================================================

def detectar_joia(landmarks):

    # Polegar para cima
    polegar_para_cima = landmarks[4].y < landmarks[3].y

    # Os outros dedos estão dobrados
    indicador_dobrado = landmarks[8].y > landmarks[6].y
    medio_dobrado = landmarks[12].y > landmarks[10].y
    anelar_dobrado = landmarks[16].y > landmarks[14].y
    mindinho_dobrado = landmarks[20].y > landmarks[18].y

    if (
        polegar_para_cima
        and indicador_dobrado
        and medio_dobrado
        and anelar_dobrado
        and mindinho_dobrado
    ):
        return True

    return False


# ============================================================
# DETECTAR CRUZ
# ============================================================

def detectar_cruz(hand_landmarks):

    # Precisamos de duas mãos
    if len(hand_landmarks) < 2:
        return False


    mao_1 = hand_landmarks[0]
    mao_2 = hand_landmarks[1]


    # Pega a ponta do indicador das duas mãos
    indicador_1 = mao_1[8]
    indicador_2 = mao_2[8]


    # Calcula a distância entre os indicadores
    distancia_indicadores = distancia(
        indicador_1,
        indicador_2
    )


    # Se os indicadores estiverem muito próximos,
    # consideramos que os dedos estão formando a cruz.
    #
    # Como as coordenadas do MediaPipe são normalizadas,
    # usamos um valor pequeno.

    if distancia_indicadores < 0.10:

        return True


    return False


# ============================================================
# TRANSFORMAR O GESTO EM UMA INFORMAÇÃO
# ============================================================

def identificar_gesto(hand_landmarks):

    # --------------------------------------------------------
    # PRIMEIRO VERIFICAMOS A CRUZ
    # --------------------------------------------------------

    if detectar_cruz(hand_landmarks):

        return "CRUZ"


    # --------------------------------------------------------
    # SE TEMOS UMA MÃO, ANALISAMOS ESSA MÃO
    # --------------------------------------------------------

    if len(hand_landmarks) == 1:

        landmarks = hand_landmarks[0]


        # ----------------------------------------------------
        # VERIFICA SE É JOIA
        # ----------------------------------------------------

        if detectar_joia(landmarks):

            return "JOIA"


        # ----------------------------------------------------
        # CONTA OS DEDOS
        # ----------------------------------------------------

        quantidade_dedos = contar_dedos(landmarks)


        # ----------------------------------------------------
        # RETORNA O NÚMERO
        # ----------------------------------------------------

        if 0 <= quantidade_dedos <= 5:

            return quantidade_dedos


    # Nenhum gesto reconhecido
    return None


# ============================================================
# RECEBER O GESTO E SALVAR NA CALCULADORA
# ============================================================

def processar_gesto(gesto):

    global numero_1
    global operador
    global numero_2
    global resultado
    global gesto_bloqueado


    # ========================================================
    # SE O GESTO JÁ FOI ACEITO, NÃO ACEITA NOVAMENTE
    # ========================================================

    if gesto_bloqueado:

        return


    # ========================================================
    # PRIMEIRO NÚMERO
    # ========================================================

    if numero_1 is None:

        # Só aceitamos números aqui
        if isinstance(gesto, int):

            numero_1 = gesto

            gesto_bloqueado = True

            print("Número 1 salvo:", numero_1)

        return


    # ========================================================
    # OPERADOR
    # ========================================================

    if operador is None:

        if gesto == "CRUZ":

            operador = "+"

            gesto_bloqueado = True

            print("Operador salvo:", operador)

        return


    # ========================================================
    # SEGUNDO NÚMERO
    # ========================================================

    if numero_2 is None:

        if isinstance(gesto, int):

            numero_2 = gesto

            gesto_bloqueado = True

            print("Número 2 salvo:", numero_2)

        return


    # ========================================================
    # RESULTADO
    # ========================================================

    if resultado is None:

        if gesto == "JOIA":

            if operador == "+":

                resultado = numero_1 + numero_2

                gesto_bloqueado = True

                print("-----------------------------")
                print("Número 1:", numero_1)
                print("Operador:", operador)
                print("Número 2:", numero_2)
                print("Resultado:", resultado)
                print("-----------------------------")


# ============================================================
# CONFIGURAÇÃO DO MODELO DE MÃO
# ============================================================

options = mp.tasks.vision.HandLandmarkerOptions(

    base_options=base_options(
        model_asset_path="hand_landmarker.task"
    ),

    running_mode=vision_running_mode.VIDEO,

    num_hands=2
)


# ============================================================
# CRIA O DETECTOR
# ============================================================

with mp.tasks.vision.HandLandmarker.create_from_options(options) as detector:

    # Cria a janela
    cv2.namedWindow("Calculadora de Gestos")

    # Liga nossa função de reset ao mouse
    cv2.setMouseCallback(
        "Calculadora de Gestos",
        zerar_calculadora
    )


    # Contador de tempo do vídeo
    timestamp = 0


    # ========================================================
    # LOOP PRINCIPAL
    # ========================================================

    while True:

        # ----------------------------------------------------
        # PEGA UM FRAME DA CÂMERA
        # ----------------------------------------------------

        sucesso, frame = camera.read()


        if not sucesso:

            print("Não foi possível capturar a câmera.")

            break


        # ----------------------------------------------------
        # ESPELHAR A CÂMERA
        # ----------------------------------------------------

        frame = cv2.flip(frame, 1)


        # ----------------------------------------------------
        # CONVERTER BGR PARA RGB
        # ----------------------------------------------------

        imagem_rgb = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )


        # ----------------------------------------------------
        # TRANSFORMAR EM MP IMAGE
        # ----------------------------------------------------

        imagem_mp = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=imagem_rgb
        )


        # ----------------------------------------------------
        # AUMENTA O TIMESTAMP
        # ----------------------------------------------------

        timestamp += 1


        # ----------------------------------------------------
        # DETECTA AS MÃOS
        # ----------------------------------------------------

        resultado_maos = detector.detect_for_video(
            imagem_mp,
            timestamp
        )


        # ----------------------------------------------------
        # PEGA OS LANDMARKS
        # ----------------------------------------------------

        hand_landmarks = resultado_maos.hand_landmarks


        # ----------------------------------------------------
        # IDENTIFICA O GESTO
        # ----------------------------------------------------

        gesto_atual = identificar_gesto(
            hand_landmarks
        )


        # ====================================================
        # CONTROLE DOS 15 FRAMES
        # ====================================================

        if gesto_atual is not None:

            # Se é o mesmo gesto do frame anterior
            if gesto_atual == gesto_anterior:

                frame_gesto += 1

            else:

                # Mudou de gesto
                gesto_anterior = gesto_atual

                frame_gesto = 1

                # Desbloqueia para permitir
                # que o novo gesto seja aceito
                gesto_bloqueado = False


            # ------------------------------------------------
            # GESTO FICOU 15 FRAMES NA TELA
            # ------------------------------------------------

            if frame_gesto >= frames_necessarios:

                processar_gesto(
                    gesto_atual
                )


        else:

            # Não detectou gesto
            gesto_anterior = None

            frame_gesto = 0


        # ====================================================
        # MOSTRAR A EXPRESSÃO NA TELA
        # ====================================================

        texto_conta = ""


        if numero_1 is not None:

            texto_conta += str(numero_1)


        if operador is not None:

            texto_conta += " " + operador


        if numero_2 is not None:

            texto_conta += " " + str(numero_2)


        if resultado is not None:

            texto_conta += " = " + str(resultado)


        # ----------------------------------------------------
        # MOSTRA A CONTA
        # ----------------------------------------------------

        cv2.putText(
            frame,
            texto_conta,
            (50, 100),
            cv2.FONT_HERSHEY_SIMPLEX,
            2,
            (0, 255, 0),
            4
        )


        # ====================================================
        # MOSTRAR O GESTO DETECTADO
        # ====================================================

        if gesto_atual is not None:

            texto_gesto = "Gesto: " + str(gesto_atual)

            cv2.putText(
                frame,
                texto_gesto,
                (50, 160),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255, 255, 255),
                2
            )


        # ====================================================
        # MOSTRAR OS FRAMES
        # ====================================================

        cv2.putText(
            frame,
            f"Frames: {frame_gesto}/{frames_necessarios}",
            (50, 200),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )


        # ====================================================
        # BOTÃO RESET
        # ====================================================

        cv2.rectangle(
            frame,
            (20, 400),
            (150, 450),
            (0, 0, 255),
            -1
        )


        cv2.putText(
            frame,
            "RESET",
            (35, 435),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )


        # ====================================================
        # MOSTRA A CÂMERA
        # ====================================================

        cv2.imshow(
            "Calculadora de Gestos",
            frame
        )


        # ====================================================
        # ESC PARA SAIR
        # ====================================================

        tecla = cv2.waitKey(1) & 0xFF

        if tecla == 27:

            break


# ============================================================
# ENCERRAR
# ============================================================

camera.release()

cv2.destroyAllWindows()