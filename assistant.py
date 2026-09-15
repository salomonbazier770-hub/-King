import os
import subprocess
import json
import requests
import datetime

class DeviceConsciousness:
    @staticmethod
    def get_info():
        try:
            batt = json.loads(subprocess.run("termux-battery-status", capture_output=True, text=True).stdout or "{}")
            niveau = batt.get("percentage", 100)
            statut = batt.get("status", "INCONNU")
        except:
            niveau, statut = 100, "INCONNU"
        
        try:
            modele = subprocess.run("getprop ro.product.model", shell=True, capture_output=True, text=True).stdout.strip()
            android_ver = subprocess.run("getprop ro.build.version.release", shell=True, capture_output=True, text=True).stdout.strip()
        except:
            modele, android_ver = "TECNO", "15"

        try:
            df = subprocess.run("df /data | tail -1", shell=True, capture_output=True, text=True).stdout.split()
            espace_libre_go = round(int(df[3]) / (1024*1024), 1) if len(df) > 3 else "Inconnu"
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
        if isinstance(info["battery_level"], int) and info["battery_level"] < 20 and info["battery_status"] != "CHARGING":
            suggestions.append("⚠️ Batterie faible, pense à brancher ton téléphone.")
        if isinstance(info["free_storage_gb"], (int, float)) and info["free_storage_gb"] < 2:
            suggestions.append("⚠️ Espace de stockage faible.")
        if not suggestions:
            suggestions.append("✨ Système parfaitement stable et opérationnel.")
        return suggestions

class LocalEngine:
    @staticmethod
    def executer_tache_locale(prompt):
        p = prompt.lower()
        
        # 1. WIFI
        if "wifi" in p or "wi-fi" in p:
            if any(mot in p for mot in ["coupe", "éteins", "désactive"]):
                os.system("am broadcast -a io.github.termux.wifi.WIFI_DISABLE")
                return "Wi-Fi désactivé."
            elif any(mot in p for mot in ["allume", "active", "mets"]):
                os.system("am broadcast -a io.github.termux.wifi.WIFI_ENABLE")
                return "Wi-Fi activé avec succès."

        # 2. FLASH
        elif "flash" in p:
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
            if any(mot in p for mot in ["fond", "max", "maximum"]):
                os.system("termux-volume music 15")
                return "Volume au maximum."
            elif any(mot in p for mot in ["silence", "muet", "coupe"]):
                os.system("termux-volume music 0")
                return "Volume coupé."

        # 5. LUMINESCENCE
        elif "luminosité" in p:
            if any(mot in p for mot in ["faible", "baisse"]):
                os.system("termux-brightness 50")
                return "Luminosité réduite."
            elif any(mot in p for mot in ["fond", "maximum"]):
                os.system("termux-brightness 255")
                return "Luminosité au maximum."

        # 6. MÉO / NOTES (NOUVEAU)
        elif "note" in p or "rappelle-moi" in p or "memo" in p:
            contenu_note = prompt.replace("note", "").replace("rappelle-moi", "").replace("memo", "").strip()
            if contenu_note:
                withفتح("notes_assistant.txt", "a", encoding="utf-8") as f:
                    f.write(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}] {contenu_note}\n")
                return f"C'est c'est noté dans tes mémos : '{contenu_note}'"
            else:
                try:
                    if os.path.exists("notes_assistant.txt"):
                        with open("notes_assistant.txt", "r", encoding="utf-8") as f:
                            notes = f.read()
                        return f"Voici tes notes enregistrées :\n{notes}"
                    else:
                        return "Tu n'as aucune note pour l'instant."
                except:
                    return "Erreur lors de la lecture des notes."

        # 7. LANCER UNE APPLICATION (NOUVEAU)
        elif "ouvre" in p or "lance" in p:
            app_nom = p.replace("ouvre", "").replace("lance", "").strip()
            if "whatsapp" in app_nom:
                os.system("am start -n com.whatsapp/.Main")
                return "Ouverture de WhatsApp..."
            elif "youtube" in app_nom:
                os.system("am start -n com.google.android.youtube/com.google.android.apps.youtube.app.WatchWhileActivity")
                return "Ouverture de YouTube..."
            elif "paramètre" in app_nom or "réglage" in app_nom:
                os.system("am start -a android.settings.SETTINGS")
                return "Ouverture des paramètres."
            else:
                return f"Je ne sais pas encore lancer l'application {app_nom} directement, mais je progresse !"

        # 8. MÉTÉO (NOUVEAU)
        elif "météo" in p or "temps" in p:
            try:
                # Utilisation d'une API météo publique géolocalisée simple
                res = requests.get("https://wttr.in/?format=3", timeout=5)
                if res.status_code == 200:
                    return f"Météo actuelle : {res.text.strip()}"
            except:
                pass
            return "Impossible de récupérer la météo pour le moment (vérifie ta connexion)."

        # 9. INFOS ET ETAT
        elif any(mot in p for mot in ["paramètres", "état", "infos", "batterie", "stockage"]):
            info = DeviceConsciousness.get_info()
            suggs = DeviceConsciousness.generer_suggestions(info)
            return f"Appareil : {info['model']} (Android {info['android']})\nBatterie : {info['battery_level']}% ({info['battery_status']})\nStockage libre : {info['free_storage_gb']} Go\nConseil : {suggs[0]}"

        return None

class MultiAI:
    def __init__(self):
        self.api_key = "" # Sécurisé pour GitHub

    def interroger_gemini(self, prompt, device_contexte):
        if not self.api_key:
            return "Mode hors-ligne : Je peux exécuter tes commandes matérielles, la météo et tes mémos, mais pour discuter avec l'IA, ajoute ta clé API Gemini dans le code."
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.api_key}"
        headers = {"Content-Type": "application/json"}
        contexte_systeme = (
            f"Tu es l'assistant personnel intelligent et ultra-efficace de Salomon. "
            f"Contexte appareil actuel : {device_contexte}. "
            f"Sois ultra-bref, direct et factuel. Réponds avec précision."
        )
        payload = {
            "contents": [{
                "parts": [{"text": f"{contexte_systeme}\n\nUtilisateur : {prompt}"}]
            }]
        }
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            if response.status_code == 200:
                res_data = response.json()
                return res_data["candidates"][0]["content"]["parts"][0]["text"]
            else:
                return "Erreur Cloud. Commandes locales uniquement."
        except:
            return "Mode hors-ligne actif."

def parler(texte):
    print(f"\nAI: {texte}\n")
    txt_propre = texte.replace('"', '').replace("'", "").replace("\n", ". ")
    os.system(f"termux-tts-speak '{txt_propre}'")

ai_brain = MultiAI()
info = DeviceConsciousness.get_info()
parler(f"Contrôleur système prêt sur {info['model']}")

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
