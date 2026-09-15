from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
import threading

# Import sécurisé pour Android
try:
    from jnius import autoclass
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    activity = PythonActivity.mActivity
    Context = autoclass('android.content.Context')
    ANDROID = True
except Exception:
    ANDROID = False

class AuraVisionApp(App):
    def build(self):
        self.title = "Aura Vision Directe"
        root = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        self.cam_image = Image(source='', size_hint=(1, 0.5))
        root.add_widget(self.cam_image)
        
        self.status_label = Label(
            text="Aura est prête et connectée au système.",
            size_hint=(1, 0.2),
            halign='center',
            valign='middle'
        )
        self.status_label.bind(size=self.status_label.setter('text_size'))
        root.add_widget(self.status_label)
        
        input_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.15), spacing=10)
        
        self.text_input = TextInput(
            hint_text="Ex: Désactive le Wi-Fi, Ouvre TikTok...",
            multiline=False
        )
        input_layout.add_widget(self.text_input)
        
        send_btn = Button(text="Exécuter", size_hint=(0.3, 1))
        send_btn.bind(on_press=self.process_command)
        input_layout.add_widget(send_btn)
        
        root.add_widget(input_layout)
        return root

    
    def process_command(self, instance):
        user_text = self.text_input.text.strip()
        if not user_text:
            return
        self.status_label.text = f"Analyse : '{user_text}'..."
        self.text_input.text = ""
        threading.Thread(target=self.execute_action, args=(user_text,)).start()

    def execute_action(self, command):
        cmd = command.lower()
        if "wifi" in cmd:
            if "désactive" in cmd or "coupe" in cmd:
                self.toggle_wifi(False)
            elif "active" in cmd or "allume" in cmd:
                self.toggle_wifi(True)
        elif "youtube" in cmd:
            self.open_app("com.google.android.youtube")
        elif "tiktok" in cmd:
            self.open_app("com.zhiliaoapp.musically")
        else:
            self.status_label.text = f"Commande reçue : {command}"

    def toggle_wifi(self, enable):
        if not ANDROID:
            self.status_label.text = "Simulation : Wi-Fi " + ("activé" if enable else "désactivé")
            return
        try:
            Context = autoclass('android.content.Context')
            wifi_manager = activity.getSystemService(Context.WIFI_SERVICE)
            success = wifi_manager.setWifiEnabled(enable)
            if success:
                state = "activé" if enable else "désactivé"
                self.status_label.text = f"Succès : Wi-Fi {state}."
            else:
                self.status_label.text = "Android restreint la modification directe du Wi-Fi."
        except Exception as e:
            self.status_label.text = f"Erreur Wi-Fi : {str(e)}"

    def open_app(self, package_name):
        if not ANDROID:
            self.status_label.text = f"Simulation : Ouverture de {package_name}"
            return
        try:
            pm = activity.getPackageManager()
            intent = pm.getLaunchIntentForPackage(package_name)
            if intent:
                activity.startActivity(intent)
                self.status_label.text = "Application ouverte !"
            else:
                self.status_label.text = "Application non trouvée."
        except Exception as e:
            self.status_label.text = f"Erreur d'ouverture : {str(e)}"

if __name__ == '__main__':
    AuraVisionApp().run()


