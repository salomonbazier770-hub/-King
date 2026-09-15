import os
import subprocess
import json
import requests

class DeviceConsciousness:
    @staticmethod
    def get_info():
        try:
            batt = json.loads(subprocess.run("termux-battery-status", shell=True, capture_output=True, text=True).stdout)
            niveau = batt.get("percentage", 100)
            statut = batt.get("status", "INCONNU")
        except:
            niveau, statut = 100, "INCONNU"
        
        modele = subprocess.run("getprop ro.product.model", shell=True, capture_output=True, text=True).stdout.strip()
        android_ver = subprocess.run("getprop ro.build.version.release", shell=True, capture_output=True, text=True).stdout.strip()
        
        try:
            df = subprocess.run("df /data | tail -1", shell=True, capture_output=True, text=True).stdout.split()
            espace_libre_go = round(int(df[3]) / (1024 * 1024), 2)
        except:
            espace_libre_go = "Inconnu"

        return {
            "model": modele or "TECNO KM7",
            "android": android_ver or "15",
            "battery_level": niveau,
            "battery_status": statut,
            "free_storage_gb": espace_libre_go
        }

    @staticmethod
    def generer_suggestions(info):
        suggestions = []
        if isinstance(info["battery_level"], int) and info["battery_level"] < 30 and info["battery_status"] != "CHARGING":
            suggestions.append("Suggestion : Batterie sous les 30%, active l'économie d'énergie.")
        if isinstance(info["free_storage_gb"], (int, float)) and info["free_storage_gb"] < 2:
            suggestions.append("Suggestion : Stockage faible (< 2 Go). Nettoyage conseillé.")
        if not suggestions:
            suggestions.append("Système parfaitement optimisé.")
        return suggestions

class LocalEngine:
    @staticmethod
    def executer_tache_locale(prompt):
        p = prompt.lower()
        
        # 1. WIFI - Utilisation de l'intent et de termux-wifi-enable
        if "wifi" in p or "wi-fi" in p:
            if any(mot in p for mot in ["coupe", "éteins", "désactive", "arrête"]):
                # Tentative Termux API
                subprocess.run("termux-wifi-enable false", shell=True)
                # Tentative alternative via intent Android 15
                os.system("am broadcast -a io.github.termux.app.RUN_COMMAND_P --es com.termux.app.execute.cmd 'svc wifi disable' > /dev/null 2>&1")
                return "J'ai envoyé l'ordre de couper le Wi-Fi. (Note : Android 15 bloque parfois l'extinction directe sans permission root/adb)."
            elif any(mot in p for mot in ["allume", "active", "mets"]):
                subprocess.run("termux-wifi-enable true", shell=True)
                return "Wi-Fi activé avec succès."

        # 2. FLASH
        if "flash" in p:
            if any(mot in p for mot in ["allume", "active"]):
                os.system("termux-torch on")
                return "Flash allumé."
            elif any(mot in p for mot in ["éteins", "coupe"]):
                os.system("termux-torch off")
                return "Flash éteint."
            
        # 3. VIBRATION
        elif "vibre" in p or "vibration" in p:
            os.system("termux-vibrate -d 500")
            return "Vibration effectuée."
            
        # 4. VOLUME
        elif "volume" in p or "son" in p:
            if "fond" in p or "max" in p:
                os.system("termux-volume music 15")
                return "Volume au maximum."
            elif "silence" in p or "muet" in p or "coupe" in p:
                os.system("termux-volume music 0")
                return "Volume coupé."

        # 5. LUMINESCENCE
        elif "luminosité" in p:
            if "faible" in p or "baisse" in p:
                os.system("termux-brightness 50")
                return "Luminosité réduite."
            elif "fond" in p or "maximum" in p:
                os.system("termux-brightness 255")
                return "Luminosité au maximum."

        # 6. INFOS ET ETAT
        elif "paramètres" in p or "état" in p or "info" in p or "batterie" in p:
            info = DeviceConsciousness.get_info()
            suggs = DeviceConsciousness.generer_suggestions(info)
            return f"Appareil : {info['model']} (Android {info['android']}). Batterie : {info['battery_level']}%. Espace libre : {info['free_storage_gb']} Go.\n" + "\n".join(suggs)
            
        return None

class MultiAI:
    def __init__(self):

    def interroger_gemini(self, prompt, device_context):
        headers = {"Content-Type": "application/json"}
        
        contexte_systeme = (
            f"Tu es l'assistant personnel intelligent de Salomon sur {device_context['model']} (Android {device_context['android']}). "
            f"Sois ultra-bref, direct et factuel. Réponds en français."
        )
        
        payload = {
            "contents": [{
                "parts": [{"text": f"{contexte_systeme}\n\nSalomon: {prompt}"}]
            }]
        }
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=15)
            if response.status_code == 200:
                res_data = response.json()
                return res_data["candidates"][0]["content"]["parts"][0]["text"]
            else:
                return "Erreur Cloud. Commandes locales disponibles."
        except:
            return "Mode hors-ligne actif."

def parler(texte):
    print(f"\nIA: {texte}\n")
    txt_propre = texte.replace('"', '').replace("'", "").replace("\n", " ")
    os.system(f'termux-tts-speak "{txt_propre}"')

ai_brain = MultiAI()
info = DeviceConsciousness.get_info()
parler(f"Contrôleur système prêt sur {info['model']}.")

while True:
    user_input = input("\nSalomon > ")
    if user_input.lower() in ["quitter", "exit", "stop"]:
        parler("Fermeture du système.")
        break
    if not user_input.strip():
        continue

    reponse_locale = LocalEngine.executer_tache_locale(user_input)
    
    if reponse_locale:
        rep_texte = reponse_locale
    else:
        rep_texte = ai_brain.interroger_gemini(user_input, info)

    parler(rep_texte)
