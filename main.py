import cv2
import threading
import pygame
from datetime import datetime

# Caminho dos arquivos de configuração
Config_Path = 'ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt'
Model_Path = 'frozen_inference_graph.pb'
Classes_Path = 'coco.names'
Video_Path = 'ex01.mp4'  # Caminho do vídeo de entrada (substitua pelo caminho do seu arquivo de vídeo)
person_count = 0

# Variáveis globais para controle da ROI
roi_x = 250
roi_y = 100
roi_width = 500
roi_height = 200

# Variáveis globais para controle do redimensionamento
resizing = False
mouse_start = (0, 0)

# Variáveis globais para controle do alerta e gravação de vídeo
alerta_ativo = False
alert_count = 0
gravando_video = False
video_writer = None

# Inicializar o modelo de detecção
net = cv2.dnn_DetectionModel(Config_Path, Model_Path)
net.setInputSize(320, 320)
net.setInputScale(1.0 / 127.5)
net.setInputMean((127.5, 127.5, 127.5))
net.setInputSwapRB(True)

# Carregar a lista de classes
with open(Classes_Path, 'r') as f:
    ClassesList = f.read().splitlines()

# Definir o índice da classe desejada (pessoa)
desired_class_index = ClassesList.index('person') + 1  # Encontrar o índice da classe 'person' (1-based index)

# Inicializar o mixer de áudio do pygame
pygame.mixer.init()

# Carregar o arquivo de áudio
alert_sound = pygame.mixer.Sound('alert_sound.wav.mp3')

# Função de callback para eventos do mouse
def mouse_callback(event, x, y, flags, param):
    global resizing, roi_x, roi_y, mouse_start

    if event == cv2.EVENT_LBUTTONDOWN:
        # Verificar se o clique está dentro da ROI e iniciar redimensionamento
        if roi_x < x < roi_x + roi_width and roi_y < y < roi_y + roi_height:
            resizing = True
            mouse_start = (x, y)
    elif event == cv2.EVENT_MOUSEMOVE:
        # Atualizar a ROI durante o redimensionamento
        if resizing:
            delta_x = x - mouse_start[0]
            delta_y = y - mouse_start[1]
            roi_x += delta_x
            roi_y += delta_y
            mouse_start = (x, y)
    elif event == cv2.EVENT_LBUTTONUP:
        # Finalizar o redimensionamento ao soltar o botão do mouse
        resizing = False

# Função para desenhar retângulo na área de interesse (ROI) com transparência
def draw_roi_rectangle(image):
    global roi_x, roi_y, roi_width, roi_height

    red_color = (0, 0, 255)  # Cor vermelha (BGR)
    transparency = 0.4  # Nível de transparência (0 a 1)

    overlay = image.copy()
    cv2.rectangle(overlay, (roi_x, roi_y), (roi_x + roi_width, roi_y + roi_height), red_color, -1)  # Desenhar retângulo vermelho
    cv2.addWeighted(overlay, transparency, image, 1 - transparency, 0, image)

    return (roi_x, roi_y, roi_width, roi_height)  # Retornar as coordenadas da ROI

# Função para verificar se um ponto (cx, cy) está dentro de uma área (x, y, w, h)
def is_point_inside_area(cx, cy, area):
    x, y, w, h = area
    return x <= cx <= x + w and y <= cy <= y + h

# Função para incrementar a contagem de pessoas detectadas
def increment_person_count():
    global person_count
    person_count += 1

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

# Função para processar os resultados da detecção
def processar_deteccoes(classes, confidences, boxes, img):
    global alerta_ativo, alert_count

    # Desenhar retângulo na área de interesse (ROI) com transparência
    area_of_interest = draw_roi_rectangle(img)

    # Iterar sobre as detecções
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
                    if alert_count < 3:
                        # Iniciar thread para reproduzir o alerta
                        threading.Thread(target=emitir_alerta).start()
                        alert_count += 1  # Incrementar o contador de alerta

                # Desenhar retângulo ao redor da pessoa
                cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
                cv2.putText(img, 'person', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

# Função para inicializar a captura de vídeo
def capturar_video():
    return cv2.VideoCapture(Video_Path)

# Função para liberar os recursos de vídeo
def liberar_video(video):
    if gravando_video:
        encerrar_gravacao_video()
    video.release()
    cv2.destroyAllWindows()

# Configurar a função de callback do mouse
cv2.namedWindow('IMG')
cv2.setMouseCallback('IMG', mouse_callback)

# Inicializar a captura de vídeo
video = capturar_video()

# Loop principal
while True:
    # Capturar o próximo frame do vídeo
    ret, img = video.read()
    if not ret:
        break

    # Redimensionar a imagem para processamento
    img = cv2.resize(img, (1000, 700))

    # Processar os resultados da detecção
    classes, confidences, boxes = net.detect(img, confThreshold=0.6)
    processar_deteccoes(classes, confidences, boxes, img)

    # Gravar frame no vídeo se estiver gravando
    if gravando_video:
        video_writer.write(img)

    # Exibir a mensagem "INVASOR DETECTADO" de forma fixa na tela se o alerta estiver ativo
    if alerta_ativo:
        cv2.putText(img, 'INVASOR DETECTADO', (105, 65), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

    # Exibir a imagem com as detecções
    cv2.imshow('IMG', img)

    # Aguardar pressionamento da tecla 'q' para sair
    key = cv2.waitKey(1)
    if key & 0xFF == ord('q'):
        break

# Liberar recursos
liberar_video(video)
