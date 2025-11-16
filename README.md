# Alerta Contra Invasões

Este projeto é uma aplicação de visão computacional capaz de detectar pessoas em tempo real utilizando *deep learning*.  
Quando uma pessoa é identificada dentro de uma área configurável (ROI), o sistema dispara um alerta sonoro e visual, além de iniciar automaticamente a gravação de um vídeo para apoiar na identificação.

---

## 📌 Funcionalidades

- **Detecção em tempo real** usando o modelo *SSD MobileNet v3*.
- **Área de detecção ajustável (ROI)** — mover/redimensionar livremente.
- **Alerta sonoro automático** ao detectar uma pessoa.
- **Gravação de vídeo** durante o alerta.
- Interface gráfica com **Kivy** para controle da aplicação.

---

## 🚀 Tecnologias Utilizadas

- **OpenCV** — visão computacional.
- **Kivy** — interface gráfica.
- **Pygame** — alerta sonoro.
- **Threading (Python)** — execução paralela para evitar travamentos.

---

## 📦 Requisitos

- Python 3.x  
- OpenCV  
- Kivy  
- Pygame  

Instale tudo com:

```bash
pip install -r requirements.txt
