import kivy
import subprocess
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import AsyncImage
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle

class LoginScreen(FloatLayout):
    def __init__(self, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)

        # Definir cor de fundo
        with self.canvas.before:
            Color(0, 0, 1, 1)  # Cor azul (R=0, G=0, B=1, A=1)
            self.rect = Rectangle(size=self.size, pos=self.pos)

        self.bind(size=self._update_rect, pos=self._update_rect)

        # Widget da tela de login: imagem GIF
        self.gif_image = AsyncImage(source='mario-yoshi.gif', anim_delay=0.1,
                                    size_hint=(None, None), size=(300, 300),
                                    pos_hint={'center_x': 0.5, 'center_y': 0.7})

        # Outros widgets da tela de login
        self.username_input = TextInput(hint_text='Nome de Usuário',
                                        size_hint=(None, None), size=(200, 40),
                                        pos_hint={'center_x': 0.5, 'center_y': 0.5},
                                        multiline=False)

        self.password_input = TextInput(hint_text='Senha',
                                        size_hint=(None, None), size=(200, 40),
                                        pos_hint={'center_x': 0.5, 'center_y': 0.4},
                                        multiline=False, password=True)

        self.login_button = Button(text='Login',
                                   size_hint=(None, None), size=(100, 50),
                                   pos_hint={'center_x': 0.5, 'center_y': 0.3},
                                   padding=(1, 5))

        self.login_button.bind(on_press=self.check_login)

        # Adicionando widgets ao layout inicial
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
        if username == 'wallingson' and password == 'senha':
            print('Login bem-sucedido!')

            # Remover widgets da tela de login
            self.remove_widget(self.gif_image)
            self.remove_widget(self.username_input)
            self.remove_widget(self.password_input)
            self.remove_widget(self.login_button)

            # Adicionar novo widget para a próxima tela ou funcionalidade
            welcome_label = Label(text=f'Bem-vindo, {username}!',
                                  font_size=24,
                                  pos_hint={'center_x': 0.5, 'center_y': 0.5},
                                  color=(1, 1, 1, 1))  # Cor do texto: branco (R=1, G=1, B=1, A=1)

            # self.config_button = Button(text='Configurações',
            #                             size_hint=(None, None), size=(200, 100),
            #                             pos_hint={'center_x': 0.5, 'center_y': 0.3},
            #                             padding=(1, 5))

            self.add_widget(welcome_label)
            # self.add_widget(self.config_button)

            # self.login_button.bind(on_press=self.check_login)

            # Exemplo: Iniciar subprocesso após login bem-sucedido
            subprocess.Popen(['python', 'main.py'])
        else:
            print('Login inválido. Tente novamente.')

class TesteKivyApp(App):
    def build(self):
        return LoginScreen()

if __name__ == '__main__':
    TesteKivyApp().run()