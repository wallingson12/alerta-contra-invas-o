# Alerta contra invasões
Este projeto consiste em uma aplicação que utiliza técnicas de visão computacional para detectar a presença de pessoas em vídeos. 
A detecção é realizada em tempo real e, ao identificar uma pessoa em uma área pré-definida, o sistema emite alertas visuais e sonoros e inicia a gravação de um video para ajudar na identificação.

# Funcionalidades
- Utilização do modelo SSD MobileNet para detecção de objetos, com foco na classe 'person'.
- Interface gráfica desenvolvida com Kivy para configuração e controle da aplicação.
- Reprodução de alerta sonoro e visual ao detectar uma pessoa na área de interesse.
- Gravação de vídeo automática durante o alerta de detecção.

# Tecnologias
- OpenCV: Biblioteca de visão computacional para processamento de imagens e vídeos.
- Kivy: Framework Python para criação de interfaces gráficas multi-touch.
- Pygame: Biblioteca para reprodução de áudio durante os alertas.
- Python threading: Utilizado para executar funções em threads separadas para alertas simultâneos.

 # Requisitos
- Python 3.x
- OpenCV
- Kivy
- Pygame

## Clone este repositório:
git clone https://github.com/seu-usuario/nome-do-repositorio.git

## Instale as dependências:
pip install -r requirements.txt

# Utilização 
- Execute o arquivo python app.py

# Estrutura de arquivos
- alerta-contra-invas-o/
- app.py
- main.py
- opcoes.py
- alert_sound.wav.mp3
- ex01.mp4
- ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt
- frozen_inference_graph.pb
- coco.names
- mario-yoshi.gif
- README.md
- requirements.txt

# Contribuição
Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou pull requests para melhorias no projeto.
