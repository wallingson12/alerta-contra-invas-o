import cv2
import numpy as np
import torch

def detect_objects_in_video(video_path):
    # Configuração do YOLOv5
    model_path = 'yolov5s.pt'

    # Carregar modelo YOLOv5 com PyTorch
    model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)

    # Mapeamento das classes
    classes = ['person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck', 'boat', 'traffic light',
               'fire hydrant', 'stop sign', 'parking meter', 'bench', 'bird', 'cat', 'dog', 'horse', 'sheep', 'cow',
               'elephant', 'bear', 'zebra', 'giraffe', 'backpack', 'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee',
               'skis', 'snowboard', 'sports ball', 'kite', 'baseball bat', 'baseball glove', 'skateboard', 'surfboard',
               'tennis racket', 'bottle', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple',
               'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake', 'chair', 'couch',
               'potted plant', 'bed', 'dining table', 'toilet', 'tv', 'laptop', 'mouse', 'remote', 'keyboard',
               'cell phone', 'microwave', 'oven', 'toaster', 'sink', 'refrigerator', 'book', 'clock', 'vase',
               'scissors', 'teddy bear', 'hair drier', 'toothbrush']

    # Inicializar a captura de vídeo
    video = cv2.VideoCapture(video_path)

    # Verificar se a câmera IP está sendo acessada corretamente
    if not video.isOpened():
        print("Erro ao abrir o vídeo")
        exit()

    while True:
        # Capturar o frame atual do vídeo
        ret, img = video.read()
        if not ret:
            break

        # Redimensionar a imagem para processamento
        img = cv2.resize(img, (1000, 700))

        # Detecção de objetos usando YOLOv5
        results = model(img)

        # Processar os resultados da detecção
        for result in results.xyxy[0]:
            class_id = int(result[5])
            confidence = float(result[4])
            label = f"{classes[class_id]}: {confidence:.2f}"
            x, y, w, h = map(int, result[:4])
            # Desenhar retângulo ao redor do objeto detectado
            cv2.rectangle(img, (x, y), (w, h), (255, 0, 0), 2)
            # Rotular o objeto detectado
            cv2.putText(img, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

        # Exibir a imagem com as detecções
        cv2.imshow('IMG', img)

        # Aguardar pressionamento da tecla 'q' para sair
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Liberar recursos
    video.release()
    cv2.destroyAllWindows()

# Testar a função com o vídeo da câmera IP
detect_objects_in_video(Video_Path)
