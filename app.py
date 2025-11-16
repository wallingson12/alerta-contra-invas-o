import threading
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import AsyncImage
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle

from main import run_system  # sua função de detecção
from db_utils import validate_user  # validação de login com hash

class LoginScreen(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Fundo azul
        with self.canvas.before:
            Color(0, 0, 1, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

        # GIF animado
        self.gif_image = AsyncImage(
            source='mario-yoshi.gif', anim_delay=0.1,
            size_hint=(None, None), size=(300, 300),
            pos_hint={'center_x': 0.5, 'center_y': 0.7}
        )

        # Campos de login
        self.username_input = TextInput(
            hint_text='Nome de Usuário', size_hint=(None, None),
            size=(200, 40), pos_hint={'center_x': 0.5, 'center_y': 0.5}, multiline=False
        )
        self.password_input = TextInput(
            hint_text='Senha', size_hint=(None, None),
            size=(200, 40), pos_hint={'center_x': 0.5, 'center_y': 0.4},
            multiline=False, password=True
        )

        # Botão de login
        self.login_button = Button(
            text='Login', size_hint=(None, None),
            size=(100, 50), pos_hint={'center_x': 0.5, 'center_y': 0.3}
        )
        self.login_button.bind(on_press=self.check_login)

        # Adiciona widgets
        self.add_widget(self.gif_image)
        self.add_widget(self.username_input)
        self.add_widget(self.password_input)
        self.add_widget(self.login_button)

    def _update_rect(self, instance, value):
        self.rect.size = instance.size
        self.rect.pos = instance.pos

    def check_login(self, instance):
        username = self.username_input.text
        password = self.password_input.text

        if validate_user(username, password):
            # Remove widgets de login
            self.clear_widgets()

            # Mensagem de boas-vindas
            welcome_label = Label(
                text=f'Bem-vindo, {username}!', font_size=24,
                pos_hint={'center_x': 0.5, 'center_y': 0.5},
                color=(1, 1, 1, 1)
            )
            self.add_widget(welcome_label)

            # Inicia o sistema em thread separada
            threading.Thread(target=run_system, daemon=True).start()
        else:
            # Erro de login
            error_label = Label(
                text='Usuário ou senha inválidos!', font_size=18,
                pos_hint={'center_x': 0.5, 'center_y': 0.2},
                color=(1, 0, 0, 1)
            )
            self.add_widget(error_label)


class LoginApp(App):
    def build(self):
        return LoginScreen()


if __name__ == '__main__':
    LoginApp().run()
