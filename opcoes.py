import subprocess
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.slider import Slider
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle
from kivy.uix.button import Button
from app import SettingsScreen  # Importa a classe SettingsScreen

class RectangleWidget(Widget):
    def __init__(self, **kwargs):
        super(RectangleWidget, self).__init__(**kwargs)
        self.rect = Rectangle(pos=self.pos, size=(200, 150))
        self.canvas.add(self.rect)

    def update_rectangle(self, x, y, width, height):
        self.rect.pos = (x, y)
        self.rect.size = (width, height)

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self.rect_widget = RectangleWidget()

        layout = BoxLayout(orientation='vertical')

        x_slider = Slider(min=0, max=1000, value=100, step=1)
        y_slider = Slider(min=0, max=1000, value=100, step=1)
        width_slider = Slider(min=50, max=1000, value=200, step=1)
        height_slider = Slider(min=50, max=1000, value=150, step=1)

        x_slider.bind(value=self.on_x_change)
        y_slider.bind(value=self.on_y_change)
        width_slider.bind(value=self.on_width_change)
        height_slider.bind(value=self.on_height_change)

        control_panel = BoxLayout(orientation='horizontal', spacing=20)
        control_panel.add_widget(x_slider)
        control_panel.add_widget(y_slider)
        control_panel.add_widget(width_slider)
        control_panel.add_widget(height_slider)

        self.back_button = Button(text='Voltar', size_hint=(None, None), size=(100, 50))
        self.back_button.bind(on_press=self.go_to_settings)

        layout.add_widget(control_panel)
        layout.add_widget(self.back_button)
        layout.add_widget(self.rect_widget)

        self.add_widget(layout)

    def go_to_settings(self, instance):
        self.manager.current = 'settings'

    def on_x_change(self, instance, value):
        self.rect_widget.update_rectangle(value, self.rect_widget.rect.pos[1],
                                          self.rect_widget.rect.size[0], self.rect_widget.rect.size[1])

    def on_y_change(self, instance, value):
        self.rect_widget.update_rectangle(self.rect_widget.rect.pos[0], value,
                                          self.rect_widget.rect.size[0], self.rect_widget.rect.size[1])

    def on_width_change(self, instance, value):
        self.rect_widget.update_rectangle(self.rect_widget.rect.pos[0], self.rect_widget.rect.pos[1],
                                          value, self.rect_widget.rect.size[1])

    def on_height_change(self, instance, value):
        self.rect_widget.update_rectangle(self.rect_widget.rect.pos[0], self.rect_widget.rect.pos[1],
                                          self.rect_widget.rect.size[0], value)

class TesteKivyApp(App):
    def build(self):
        sm = ScreenManager()
        main_screen = MainScreen(name='main')
        settings_screen = SettingsScreen(name='settings')

        sm.add_widget(main_screen)
        sm.add_widget(settings_screen)

        return sm

if __name__ == '__main__':
    TesteKivyApp().run()
