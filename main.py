
import math
from pathlib import Path
from threading import Lock

import cv2
import mediapipe as mp


class CalculadoraGestos:

    def __init__(self):
        caminho_modelo = (
            Path(__file__).resolve().parent
            / "hand_landmarker.task"
        )

        if not caminho_modelo.exists():
            raise FileNotFoundError(
                f"Modelo não encontrado: {caminho_modelo}"
            )

        options = mp.tasks.vision.HandLandmarkerOptions(
            base_options=mp.tasks.BaseOptions(
                model_asset_path=str(caminho_modelo)
            ),
            running_mode=mp.tasks.vision.RunningMode.IMAGE,
            num_hands=2,
        )

        self.detector = (
            mp.tasks.vision.HandLandmarker
            .create_from_options(options)
        )

        self.lock = Lock()
        self.zerar()

    def zerar(self):
        self.numero_1 = None
        self.operador = None
        self.numero_2 = None
        self.resultado = None

        self.gesto_anterior = None
        self.frame_gesto = 0
        self.frames_necessarios = 15
        self.gesto_bloqueado = False

        self.mensagem = "Mostre um número com a mão"

    @staticmethod
    def distancia(ponto1, ponto2):
        distancia_x = ponto1.x - ponto2.x
        distancia_y = ponto1.y - ponto2.y

        return math.sqrt(
            distancia_x ** 2 + distancia_y ** 2
        )

    @staticmethod
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

    @staticmethod
    def detectar_joia(landmarks):
        polegar_para_cima = (
            landmarks[4].y < landmarks[3].y
        )

        indicador_dobrado = (
            landmarks[8].y > landmarks[6].y
        )

        medio_dobrado = (
            landmarks[12].y > landmarks[10].y
        )

        anelar_dobrado = (
            landmarks[16].y > landmarks[14].y
        )

        mindinho_dobrado = (
            landmarks[20].y > landmarks[18].y
        )

        return (
            polegar_para_cima
            and indicador_dobrado
            and medio_dobrado
            and anelar_dobrado
            and mindinho_dobrado
        )

    def detectar_cruz(self, hand_landmarks):
        if len(hand_landmarks) < 2:
            return False

        mao_1 = hand_landmarks[0]
        mao_2 = hand_landmarks[1]

        indicador_1 = mao_1[8]
        indicador_2 = mao_2[8]

        distancia_indicadores = self.distancia(
            indicador_1,
            indicador_2
        )

        return distancia_indicadores < 0.10

    def identificar_gesto(self, hand_landmarks):
        if self.detectar_cruz(hand_landmarks):
            return "CRUZ"

        if len(hand_landmarks) == 1:
            landmarks = hand_landmarks[0]

            if self.detectar_joia(landmarks):
                return "JOIA"

            return self.contar_dedos(landmarks)

        return None

    def processar_gesto(self, gesto):
        if self.gesto_bloqueado or gesto is None:
            return

        if isinstance(gesto, int):
            if self.numero_1 is None:
                self.numero_1 = gesto
                self.mensagem = (
                    f"Primeiro número: {gesto}"
                )

            elif (
                self.operador == "+"
                and self.numero_2 is None
            ):
                self.numero_2 = gesto
                self.mensagem = (
                    f"Segundo número: {gesto}"
                )

            else:
                self.mensagem = (
                    "Use a cruz para somar "
                    "ou zere para começar novamente"
                )
                return

        elif gesto == "CRUZ":
            if (
                self.numero_1 is not None
                and self.operador is None
            ):
                self.operador = "+"
                self.mensagem = "Operação: soma (+)"

            else:
                self.mensagem = (
                    "Mostre o primeiro número "
                    "antes de escolher a operação"
                )
                return

        elif gesto == "JOIA":
            if (
                self.numero_1 is not None
                and self.operador == "+"
                and self.numero_2 is not None
            ):
                self.resultado = (
                    self.numero_1 + self.numero_2
                )

                self.mensagem = (
                    f"Resultado: {self.resultado}"
                )

            else:
                self.mensagem = (
                    "Mostre os dois números "
                    "e faça a cruz antes da joia"
                )
                return

        else:
            return

        self.gesto_bloqueado = True

    def reconhecer_imagem(self, imagem_bgr):
        if imagem_bgr is None or imagem_bgr.size == 0:
            raise ValueError("A imagem está vazia.")

        imagem_rgb = cv2.cvtColor(
            imagem_bgr,
            cv2.COLOR_BGR2RGB
        )

        imagem_mp = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=imagem_rgb
        )

        with self.lock:
            resultado = self.detector.detect(imagem_mp)

            gesto = self.identificar_gesto(
                resultado.hand_landmarks
            )

            if gesto is None:
                self.gesto_anterior = None
                self.frame_gesto = 0
                self.gesto_bloqueado = False

            elif gesto == self.gesto_anterior:
                self.frame_gesto += 1

            else:
                self.gesto_anterior = gesto
                self.frame_gesto = 1

            if (
                gesto is not None
                and self.frame_gesto >= self.frames_necessarios
            ):
                self.processar_gesto(gesto)

            return self.estado()

    def estado(self):
        return {
            "gesto": (
                self.gesto_anterior
                if self.gesto_anterior is not None
                else None
            ),
            "numero_1": self.numero_1,
            "operador": self.operador,
            "numero_2": self.numero_2,
            "resultado": self.resultado,
            "mensagem": self.mensagem,
            "frames": self.frame_gesto,
            "frames_necessarios": self.frames_necessarios,
            "gesto_bloqueado": self.gesto_bloqueado,
        }

    def fechar(self):
        self.detector.close()
