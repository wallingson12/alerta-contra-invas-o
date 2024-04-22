import cv2
import threading
import pygame
from datetime import datetime

# Caminho do vídeo de entrada (substitua pelo caminho do seu arquivo de vídeo)
Video_Path = 'ex01.mp4'

Config_Path = 'ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt'
Model_Path = 'frozen_inference_graph.pb'
Classes_Path = 'coco.names'

# Carregar a lista de classes
with open(Classes_Path, 'r') as f:
    ClassesList = f.read().splitlines()

# Definir o índice da classe desejada (pessoa)
desired_class_index = ClassesList.index('person') + 1  # Encontrar o índice da classe 'person' (1-based index)

# Inicializar o modelo de detecção
net = cv2.dnn_DetectionModel(Config_Path, Model_Path)
net.setInputSize(320, 320)
net.setInputScale(1.0 / 127.5)
net.setInputMean((127.5, 127.5, 127.5))
net.setInputSwapRB(True)

# Variável global para contar pessoas detectadas
person_count = 0

# Função para incrementar a contagem de pessoas detectadas
def increment_person_count():
    global person_count
    person_count += 1

# Inicializar o mixer de áudio do pygame
pygame.mixer.init()

# Carregar o arquivo de áudio
alert_sound = pygame.mixer.Sound('alert_sound.wav.mp3')

# Variáveis para controle de alerta e gravação de vídeo
alerta_ativo = False
alert_count = 0
gravando_video = False
video_writer = None

# Função para desenhar retângulo em uma área de interesse (ROI) com transparência
def draw_roi_rectangle(image):
    # Quanto maior x mais a direita
    # Quanto maior y mais abaixo
    # Quanto maior w mais largo
    # Quanto maior h mais alto

    x, y, w, h = 0, 200, 1000, 300  # Coordenadas da área de interesse (ROI)
    red_color = (0, 0, 255)  # Cor vermelha (BGR)
    transparency = 0.4  # Nível de transparência (0 a 1)

    overlay = image.copy()
    cv2.rectangle(overlay, (x, y), (x + w, y + h), red_color, -1)  # Desenhar retângulo vermelho
    cv2.addWeighted(overlay, transparency, image, 1 - transparency, 0, image)

    return (x, y, w, h)  # Retornar as coordenadas da ROI

# Função para verificar se um ponto (cx, cy) está dentro de uma área (x, y, w, h)
def is_point_inside_area(cx, cy, area):
    x, y, w, h = area
    return x <= cx <= x + w and y <= cy <= y + h

# Função para iniciar a gravação de vídeo
def iniciar_gravacao_video():
    global gravando_video, video_writer
    video_filename = f"alerta_{datetime.now().strftime('%Y%m%d_%H%M%S')}.avi"
    video_writer = cv2.VideoWriter(video_filename, cv2.VideoWriter_fourcc(*'XVID'), 20, (1000, 700))
    gravando_video = True

# Função para encerrar a gravação de vídeo
def encerrar_gravacao_video():
    global gravando_video, video_writer
    if video_writer is not None:
        video_writer.release()
    gravando_video = False

# Função para emitir um alerta em uma thread separada
def emitir_alerta():
    global alerta_ativo, alert_count, gravando_video
    print("ALERTA: Pessoa detectada na área!")
    alerta_ativo = True  # Ativar o alerta

    # Iniciar gravação de vídeo ao detectar invasão
    iniciar_gravacao_video()

    # Reproduzir o áudio várias vezes (limite de 3 vezes)
    for _ in range(1):
        alert_sound.play()
        pygame.time.wait(int(alert_sound.get_length() * 200))  # Aguardar o término da reprodução do áudio

    # Encerrar gravação de vídeo ao finalizar alerta
    encerrar_gravacao_video()
    alerta_ativo = False  # Desativar o alerta após o término
    alert_count = 0  # Zerar o contador de alerta após reprodução limitada

# Inicializar a captura de vídeo do arquivo de vídeo
video = cv2.VideoCapture(Video_Path)

while True:
    # Capturar o próximo frame do vídeo
    ret, img = video.read()
    if not ret:
        break

    # Redimensionar a imagem para processamento
    img = cv2.resize(img, (1000, 700))

    # Desenhar retângulo na área de interesse (ROI) com transparência
    area_of_interest = draw_roi_rectangle(img)

    # Detectar objetos na imagem
    classes, confidences, boxes = net.detect(img, confThreshold=0.6)

    # Processar os resultados da detecção
    if len(classes):
        for classId, confidence, box in zip(classes.flatten(), confidences.flatten(), boxes):
            if classId == desired_class_index and ClassesList[classId - 1] == 'person':
                # Verificar se é uma pessoa
                x, y, w, h = box
                cx = x + w // 2  # Calcular o centro x da pessoa
                cy = y + h // 2  # Calcular o centro y da pessoa

                # Verificar se o centro da pessoa está dentro da área de interesse
                if is_point_inside_area(cx, cy, area_of_interest) and not alerta_ativo:
                    # Verificar se o alerta pode ser emitido novamente (máximo 3 vezes)
                    increment_person_count()
                    print(person_count)
                    if alert_count < 3:
                        # Iniciar thread para reproduzir o alerta
                        threading.Thread(target=emitir_alerta).start()
                        alert_count += 1  # Incrementar o contador de alerta

                # Desenhar retângulo ao redor da pessoa
                cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
                cv2.putText(img, 'person', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

    # Gravar frame no vídeo se estiver gravando
    if gravando_video:
        video_writer.write(img)

    # Exibir a mensagem "INVASOR DETECTADO" de forma fixa na tela se o alerta estiver ativo
    if alerta_ativo:
        cv2.putText(img, 'INVASOR DETECTADO', (105, 65), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

    # Exibir a imagem com as detecções
    cv2.imshow('IMG', img)

    # Aguardar pressionamento da tecla 'q' para sair
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Liberar recursos
if gravando_video:
    encerrar_gravacao_video()
video.release()
cv2.destroyAllWindows()
