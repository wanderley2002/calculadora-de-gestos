import cv2
import mediapipe as mp
import time


# ============================================================
# CONFIGURAÇÃO DA CÂMERA
# ============================================================

camera = cv2.VideoCapture(0)


# ============================================================
# CONFIGURAÇÃO DO MEDIAPIPE
# ============================================================

BaseOptions = mp.tasks.BaseOptions
RunningMode = mp.tasks.vision.RunningMode


# Caminho do modelo de detecção das mãos.
CAMINHO_MODELO = "hand_landmarker.task"


# Configuração básica do modelo.
base_options = BaseOptions(
    model_asset_path=CAMINHO_MODELO
)


# Configurações do detector.
options = mp.tasks.vision.HandLandmarkerOptions(
    base_options=base_options,
    running_mode=RunningMode.VIDEO,
    num_hands=2
)


# Criação do detector.
detector = mp.tasks.vision.HandLandmarker.create_from_options(
    options
)


# ============================================================
# VARIÁVEIS DA CALCULADORA
# ============================================================

# Primeiro número da conta.
numero_1 = None

# Operador matemático.
operador = None

# Segundo número da conta.
numero_2 = None

# Resultado da conta.
resultado = None


# ============================================================
# CONTROLE DOS GESTOS
# ============================================================

# Guarda o último gesto detectado.
gesto_anterior = None

# Quantidade de frames que o gesto permaneceu estável.
frames_gesto = 0

# Quantidade de frames necessários para aceitar um gesto.
FRAMES_NECESSARIOS = 15

# Impede que o mesmo gesto seja registrado várias vezes.
gesto_bloqueado = False


# ============================================================
# CONTROLE DO TEMPO DO MEDIAPIPE
# ============================================================

timestamp_ms = 0


# ============================================================
# FUNÇÃO PARA CONTAR OS DEDOS
# ============================================================

def contar_dedos(pontos):

    dedos = 0

    # --------------------------------------------------------
    # INDICADOR
    # --------------------------------------------------------

    # pontos[8][1] = Y da ponta do indicador
    # pontos[6][1] = Y da articulação do indicador
    #
    # Se a ponta estiver acima da articulação,
    # consideramos o dedo levantado.
    #
    if pontos[8][1] < pontos[6][1]:
        dedos += 1


    # --------------------------------------------------------
    # DEDO MÉDIO
    # --------------------------------------------------------

    if pontos[12][1] < pontos[10][1]:
        dedos += 1


    # --------------------------------------------------------
    # ANELAR
    # --------------------------------------------------------

    if pontos[16][1] < pontos[14][1]:
        dedos += 1


    # --------------------------------------------------------
    # MINDINHO
    # --------------------------------------------------------

    if pontos[20][1] < pontos[18][1]:
        dedos += 1


    # --------------------------------------------------------
    # POLEGAR
    # --------------------------------------------------------

    # Aqui usamos X porque o polegar se movimenta
    # principalmente para o lado.
    #
    if pontos[4][0] > pontos[3][0]:
        dedos += 1


    return dedos


# ============================================================
# FUNÇÃO PARA DETECTAR O GESTO JOIA
# ============================================================

def eh_joia(pontos):

    # Nota: esta função recebe os pontos originais do MediaPipe
    # (com atributos .x e .y), igual a função detectar_mais.

    # Polegar levantado.
    polegar_levantado = (
        pontos[4].y < pontos[3].y
    )


    # Indicador fechado.
    indicador_fechado = (
        pontos[8].y > pontos[6].y
    )


    # Médio fechado.
    medio_fechado = (
        pontos[12].y > pontos[10].y
    )


    # Anelar fechado.
    anelar_fechado = (
        pontos[16].y > pontos[14].y
    )


    # Mindinho fechado.
    mindinho_fechado = (
        pontos[20].y > pontos[18].y
    )


    # Só é JOIA se:
    #
    # polegar levantado
    # +
    # todos os outros dedos fechados.
    #
    return (
        polegar_levantado
        and indicador_fechado
        and medio_fechado
        and anelar_fechado
        and mindinho_fechado
    )


# ============================================================
# FUNÇÃO PARA VERIFICAR CRUZAMENTO DE SEGMENTOS
# ============================================================

def segmentos_se_cruzam(a, b, c, d):

    def orientacao(p, q, r):

        valor = (
            (q[1] - p[1]) * (r[0] - q[0])
            -
            (q[0] - p[0]) * (r[1] - q[1])
        )

        if valor == 0:
            return 0

        if valor > 0:
            return 1

        return 2


    o1 = orientacao(a, b, c)
    o2 = orientacao(a, b, d)
    o3 = orientacao(c, d, a)
    o4 = orientacao(c, d, b)


    return (
        o1 != o2
        and o3 != o4
    )


# ============================================================
# DETECTAR O SINAL DE +
# ============================================================

def detectar_mais(maos, largura, altura):

    # Precisamos de duas mãos.
    if len(maos) != 2:
        return False


    mao_1 = maos[0]
    mao_2 = maos[1]


    # Os dois indicadores precisam estar levantados.
    indicador_1_levantado = (
        mao_1[8].y < mao_1[6].y
    )

    indicador_2_levantado = (
        mao_2[8].y < mao_2[6].y
    )


    if not indicador_1_levantado:
        return False

    if not indicador_2_levantado:
        return False


    # --------------------------------------------------------
    # TRANSFORMAR COORDENADAS NORMALIZADAS EM PIXELS
    # --------------------------------------------------------

    # Primeira mão.
    x1_base = int(mao_1[5].x * largura)
    y1_base = int(mao_1[5].y * altura)

    x1_ponta = int(mao_1[8].x * largura)
    y1_ponta = int(mao_1[8].y * altura)


    # Segunda mão.
    x2_base = int(mao_2[5].x * largura)
    y2_base = int(mao_2[5].y * altura)

    x2_ponta = int(mao_2[8].x * largura)
    y2_ponta = int(mao_2[8].y * altura)


    # Primeiro indicador.
    inicio_1 = (
        x1_base,
        y1_base
    )

    fim_1 = (
        x1_ponta,
        y1_ponta
    )


    # Segundo indicador.
    inicio_2 = (
        x2_base,
        y2_base
    )

    fim_2 = (
        x2_ponta,
        y2_ponta
    )


    # Verifica se os dois indicadores se cruzaram.
    return segmentos_se_cruzam(
        inicio_1,
        fim_1,
        inicio_2,
        fim_2
    )


# ============================================================
# FUNÇÃO PARA RESETAR A CALCULADORA
# ============================================================

def resetar():

    global numero_1
    global operador
    global numero_2
    global resultado

    numero_1 = None
    operador = None
    numero_2 = None
    resultado = None


# ============================================================
# FUNÇÃO PARA CALCULAR
# ============================================================

def calcular():

    global resultado

    # Só calculamos quando temos os três elementos:
    #
    # número 1
    # operador
    # número 2
    #
    if (
        numero_1 is None
        or operador is None
        or numero_2 is None
    ):
        return


    if operador == "+":

        resultado = numero_1 + numero_2


# ============================================================
# LOOP PRINCIPAL
# ============================================================

while True:

    # Captura uma imagem da câmera.
    sucesso, frame = camera.read()


    # Se a câmera falhar, encerramos.
    if not sucesso:
        break


    # Espelha a imagem para ficar como um espelho.
    frame = cv2.flip(frame, 1)


    # Pega largura e altura.
    altura, largura, _ = frame.shape


    # ========================================================
    # CONVERTER IMAGEM PARA O MEDIAPIPE
    # ========================================================

    imagem_mp = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=frame
    )


    # ========================================================
    # TIMESTAMP
    # ========================================================

    timestamp_ms += 33


    # ========================================================
    # DETECTAR MÃOS
    # ========================================================

    resultado_maos = detector.detect_for_video(
        imagem_mp,
        timestamp_ms
    )


    # Lista contendo as mãos encontradas.
    maos = resultado_maos.hand_landmarks


    # Lista dos números detectados.
    numeros_detectados = []


    # ========================================================
    # PROCESSAR CADA MÃO
    # ========================================================

    for mao in maos:

        # Lista para guardar X e Y dos landmarks.
        pontos = []


        # ----------------------------------------------------
        # PEGAR OS 21 LANDMARKS
        # ----------------------------------------------------

        for ponto in mao:

            x = int(
                ponto.x * largura
            )

            y = int(
                ponto.y * altura
            )

            # Guardamos como:
            #
            # (X, Y)
            #
            pontos.append(
                (x, y)
            )


        # ----------------------------------------------------
        # CONTAR DEDOS
        # ----------------------------------------------------

        quantidade_dedos = contar_dedos(
            pontos
        )


        numeros_detectados.append(
            quantidade_dedos
        )


        # ----------------------------------------------------
        # DESENHAR LANDMARKS
        # ----------------------------------------------------

        for x, y in pontos:

            cv2.circle(
                frame,
                (x, y),
                5,
                (0, 255, 0),
                -1
            )


        # ----------------------------------------------------
        # CONEXÕES DA MÃO
        # ----------------------------------------------------

        conexoes = [
            (0, 1),
            (1, 2),
            (2, 3),
            (3, 4),

            (0, 5),
            (5, 6),
            (6, 7),
            (7, 8),

            (0, 9),
            (9, 10),
            (10, 11),
            (11, 12),

            (0, 13),
            (13, 14),
            (14, 15),
            (15, 16),

            (0, 17),
            (17, 18),
            (18, 19),
            (19, 20)
        ]


        for inicio, fim in conexoes:

            cv2.line(
                frame,
                pontos[inicio],
                pontos[fim],
                (255, 0, 0),
                2
            )


    # ========================================================
    # DETECTAR +
    # ========================================================

    mais_detectado = detectar_mais(
        maos,
        largura,
        altura
    )


    # ========================================================
    # DETECTAR JOIA
    # ========================================================

    joia_detectada = False


    if len(maos) > 0:

        joia_detectada = eh_joia(
            maos[0]
        )


    # ========================================================
    # IDENTIFICAR O GESTO ATUAL
    # ========================================================

    gesto_atual = None


    # Primeiro verificamos o +.
    if mais_detectado:

        gesto_atual = "+"


    # Depois verificamos JOIA.
    elif joia_detectada:

        gesto_atual = "JOIA"


    # Caso contrário verificamos os dedos.
    elif len(numeros_detectados) > 0:

        gesto_atual = str(
            numeros_detectados[0]
        )


    # ========================================================
    # VERIFICAR ESTABILIDADE DO GESTO
    # ========================================================

    if gesto_atual == gesto_anterior:

        frames_gesto += 1

    else:

        gesto_anterior = gesto_atual

        frames_gesto = 1

        # Como o gesto mudou,
        # podemos aceitar o novo gesto.
        gesto_bloqueado = False


    # ========================================================
    # ACEITAR GESTO
    # ========================================================

    if (
        frames_gesto >= FRAMES_NECESSARIOS
        and not gesto_bloqueado
        and gesto_atual is not None
    ):

        # ----------------------------------------------------
        # NÚMERO
        # ----------------------------------------------------

        if gesto_atual.isdigit():

            numero = int(
                gesto_atual
            )


            # Primeiro número.
            if numero_1 is None:

                numero_1 = numero


            # Segundo número.
            elif (
                operador == "+"
                and numero_2 is None
            ):

                numero_2 = numero


        # ----------------------------------------------------
        # OPERADOR +
        # ----------------------------------------------------

        elif gesto_atual == "+":

            if numero_1 is not None:

                operador = "+"


        # ----------------------------------------------------
        # JOIA = CALCULAR
        # ----------------------------------------------------

        elif gesto_atual == "JOIA":

            calcular()


        # Depois que usamos o gesto,
        # bloqueamos para não repetir.
        gesto_bloqueado = True


    # ========================================================
    # MONTAR EXPRESSÃO
    # ========================================================

    expressao = ""


    if numero_1 is not None:

        expressao += str(
            numero_1
        )


    if operador is not None:

        expressao += (
            " "
            + operador
            + " "
        )


    if numero_2 is not None:

        expressao += str(
            numero_2
        )


    # ========================================================
    # MOSTRAR EXPRESSÃO
    # ========================================================

    cv2.putText(
        frame,
        expressao,
        (50, 100),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.2,
        (0, 255, 0),
        3
    )


    # ========================================================
    # MOSTRAR RESULTADO
    # ========================================================

    if resultado is not None:

        cv2.putText(
            frame,
            f"Resultado: {resultado}",
            (50, 160),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.2,
            (0, 255, 0),
            3
        )


    # ========================================================
    # MOSTRAR GESTO DETECTADO
    # ========================================================

    cv2.putText(
        frame,
        f"Gesto: {gesto_atual}",
        (50, 50),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 255, 255),
        2
    )


    # ========================================================
    # BOTÃO RESET
    # ========================================================

    # Área do botão:
    #
    # X: 50 até 100
    # Y: 400 até 450
    #
    cv2.rectangle(
        frame,
        (50, 400),
        (100, 450),
        (0, 0, 255),
        -1
    )


    # Letra R.
    cv2.putText(
        frame,
        "R",
        (65, 435),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (255, 255, 255),
        2
    )


    # ========================================================
    # MOSTRAR A CÂMERA
    # ========================================================

    cv2.imshow(
        "Calculadora por Gestos",
        frame
    )


    # ========================================================
    # TECLAS
    # ========================================================

    tecla = cv2.waitKey(1) & 0xFF


    # ESC encerra.
    if tecla == 27:

        break


    # R reseta.
    if tecla == ord("r"):

        resetar()


# ============================================================
# FINALIZAÇÃO
# ============================================================

camera.release()

cv2.destroyAllWindows()

detector.close()