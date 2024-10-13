import appdaemon.plugins.hass.hassapi as hass
import datetime
from datetime import timedelta

class PumpAutomation(hass.Hass):

    def initialize(self):
        # Vérifier l'état initial de l'automatisation
        self.check_initial_state()
        
        # Écouter les changements d'état de l'interrupteur de la pompe
        self.listen_state(self.check_pump_state, "sensor.etat_pompe")
        
        # Écouter les changements de l'heure de démarrage de la pompe
        self.listen_state(self.update_pump_start_time, "input_datetime.pompe_start_time")

    def check_initial_state(self):
        """Vérifier l'état initial de la pompe au démarrage."""
        etat_pompe = self.get_state("sensor.etat_pompe")
        self.log(f"État initial de la pompe : {etat_pompe}")
        
        if etat_pompe == "Arrêt":
            self.stop_pump(None)
        elif etat_pompe == "Marche Forcée":
            self.start_pump(None)
        elif etat_pompe == "Marche Auto":
            self.check_temperature_and_run_pump(immediate=True)

    def check_pump_state(self, entity, attribute, old, new, kwargs):
        """Gérer les actions en fonction de l'état de la pompe."""
        etat_pompe = self.get_state("sensor.etat_pompe")
        self.log(f"Changement d'état de la pompe : {etat_pompe}")
        
        if etat_pompe == "Arrêt":
            self.stop_pump(None)
        elif etat_pompe == "Marche Forcée":
            self.start_pump(None)
        elif etat_pompe == "Marche Auto":
            self.check_temperature_and_run_pump(immediate=True)

    def update_pump_start_time(self, entity, attribute, old, new, kwargs):
        """Mise à jour de l'heure de démarrage de la pompe."""
        self.log("Heure de démarrage de la pompe mise à jour.")
        self.check_temperature_and_run_pump(immediate=True)

    def check_temperature_and_run_pump(self, immediate=False):
        """Vérifier la température et gérer le relais en mode automatique."""
        pompe_start_time = self.get_state("input_datetime.pompe_start_time")
        pompe_start_time = self.parse_time(pompe_start_time)
        
        today = datetime.datetime.now()
        pompe_start_time = today.replace(hour=pompe_start_time.hour, minute=pompe_start_time.minute, second=0, microsecond=0)
        
        temperature = float(self.get_state("sensor.esphome_web_219874_sonde_de_temperature"))
        self.log(f"Température actuelle : {temperature}°C.")
        
        if 16 <= temperature < 20:
            hours = 8
            minute = 2  # Deux minutes pour test et 0h
        elif 20 <= temperature < 24:
            hours = 10
        elif 24 <= temperature < 28:
            hours = 12
        elif temperature >= 28:
            hours = 14
        else:
            self.log(f"Température en dehors de la plage : {temperature}°C. Pompe non activée.")
            return
        
        end_time = pompe_start_time + timedelta(hours=hours)
        end_time_str = end_time.strftime("%H:%M:%S")
        
        self.log(f"Démarrage prévu de la pompe à {pompe_start_time.strftime('%H:%M:%S')} pour {hours} heures, jusqu'à {end_time_str}.")
        
        current_time = datetime.datetime.now()
        
        if immediate and pompe_start_time <= current_time < end_time:
            self.log("Mode auto activé pendant le créneau horaire. Démarrage immédiat de la pompe.")
            self.start_pump(None)
            # Planifier l'arrêt de la pompe à l'heure de fin prévue
            self.run_at(self.stop_pump, end_time)
        else:
            # Lancer la pompe à l'heure de démarrage
            self.run_at(self.start_pump, pompe_start_time)
            # Arrêter la pompe à l'heure de fin
            self.run_at(self.stop_pump, end_time)

    def start_pump(self, kwargs):
        """Démarrer la pompe."""
        self.turn_on("switch.esphome_web_219874_relais_1")
        self.log("Pompe démarrée.")

    def stop_pump(self, kwargs):
        """Arrêter la pompe."""
        self.turn_off("switch.esphome_web_219874_relais_1")
        self.log("Pompe arrêtée.")