import re

with open("main.py", "r", encoding="utf-8") as f:
    content = f.read()

new_methods = """
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
"""

if "def process_command" in content:
    content = re.sub(r'def process_command.*?(?=if __name__)', new_methods + '\n', content, flags=re.DOTALL)
else:
    content = content.replace("if __name__ == '__main__':", new_methods + "\nif __name__ == '__main__':")

with open("main.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Mise à jour de main.py effectuée avec succès !")
