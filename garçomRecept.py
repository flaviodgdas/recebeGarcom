import socket
import threading
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.animation import Animation
from kivy.core.audio import SoundLoader

# Recebe o pedido da mesa.
class ReceptorApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical')

        self.label = Label(text='Esperando chamadas...', color=[1, 1, 1, 1])
        self.layout.add_widget(self.label)

        self.receber_button = Button(text='Receber Chamada')
        self.receber_button.bind(on_press=self.confirmar_atendimento)
        self.receber_button.disabled = True  # Desativado até receber chamada
        self.layout.add_widget(self.receber_button)

        # Inicia thread para escutar chamadas
        threading.Thread(target=self.escutar_chamadas, daemon=True).start()

        return self.layout

    def escutar_chamadas(self):
        host = '127.0.0.1'  # IP do receptor
        port = 12345        # Porta para receber chamadas
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((host, port))
            s.listen()
            while True:
                conn, addr = s.accept()
                with conn:
                    self.mensagem_recebida = conn.recv(1024).decode('utf-8')
                    self.label.text = self.mensagem_recebida
                    self.receber_button.disabled = False
                    self.reproduzir_som('bip.mp3')  # Reproduz o som
                    self.iniciar_piscando()
                    print(f'Chamada recebida: {self.mensagem_recebida}')

    def confirmar_atendimento(self, instance):
        if hasattr(self, 'mensagem_recebida'):
            mesa_num = self.mensagem_recebida.split(' ')[1]  # Extrai o número da mesa
            mensagem = f'Atendimento confirmado para a Mesa {mesa_num}.'
            print(mensagem)

            # Envia confirmação para a mesa
            host = '127.0.0.1'  # IP da mesa
            port = 12346        # Porta da mesa
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.connect((host, port))
                    s.sendall(mensagem.encode('utf-8'))
                    self.label.text = 'Esperando chamadas...'
                    self.receber_button.disabled = True  # Desativa botão após atendimento
                    self.parar_som()
                    print('Estado reiniciado.')
                except ConnectionRefusedError:
                    print('Erro: Não foi possível enviar a mensagem para a mesa.')

    def reproduzir_som(self, caminho):
        """Reproduz o som especificado."""
        self.som = SoundLoader.load(caminho)
        if self.som:
            self.som.loop = True  # Reproduzir em loop
            self.som.play()
            print('Reproduzindo som...')

    def parar_som(self):
        """Para o som em reprodução."""
        if hasattr(self, 'som') and self.som:
            self.som.stop()
            print('Som parado.')

    def iniciar_piscando(self):
        """Anima o label para piscar."""
        self.anim = Animation(color=[1, 0, 0, 1], duration=0.5) + Animation(color=[1, 1, 1, 1], duration=0.5)
        self.anim.repeat = True
        self.anim.start(self.label)

if __name__ == '__main__':
    ReceptorApp().run()