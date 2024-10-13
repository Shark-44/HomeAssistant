import appdaemon.plugins.hass.hassapi as hass

class TVLightAutomation(hass.Hass):

    def initialize(self):
        self.handles = []
        
        # Écoute les changements d'état du switch Ambilight
        self.listen_state(self.start_automations, "switch.65pus7304_12_ambilight_hue", new="on", immediate=True)
        self.listen_state(self.stop_automations, "switch.65pus7304_12_ambilight_hue", new="off", immediate=True)

    def start_automations(self, entity, attribute, old, new, kwargs):
        if not self.handles:  # Ne démarre que si aucune automation n'est déjà active
            self.log("Mode Cinéma activé")
            # Écoute les changements d'état du media_player lorsque Ambilight est activé
            handle = self.listen_state(self.media_change, "media_player.65pus7304_12_6", immediate=True)
            self.handles.append(handle)
            self.log(f"Automatisation démarrée avec handle ID : {handle}")
        else:
            self.log("Automations déjà actives")

    def stop_automations(self, entity, attribute, old, new, kwargs):
        if self.handles:  # Arrête seulement si des handles existent
            self.log("Arrêt du Mode Cinéma, suppression des écoutes")
            for handle in self.handles:
                self.cancel_listen_state(handle)
                self.log(f"Écoute annulée pour handle ID : {handle}")
            self.handles = []
        else:
            self.log("Aucune automation à arrêter")

    def media_change(self, entity, attribute, old, new, kwargs):
        # Gestion des états du média
        if old in ["off", "standby", "unavailable", "paused", "unknown", "idle", "buffering", None] and new == "playing":  
            self.log("Le média est en LECTURE. Éteindre les lumières.")
            self.call_service("script/turn_on", entity_id="script.Lights_tv_play")
        
        elif old in ["off", "standby", "unavailable", "paused", "unknown", "idle", "playing", None] and new == "buffering":  
            self.log("Le média est en LECTURE. Éteindre les lumières.")
            self.call_service("script/turn_on", entity_id="script.Lights_tv_play")

        elif old in ["playing", "buffering", None] and new == "paused": 
            self.log("Le média est en PAUSE. Activation du script de pause.")
            self.call_service("script/turn_on", entity_id="script.Lights_tv_pause")
        
        elif old in ["playing", "paused"] and new in ["standby", "unavailable", "unknown", "idle"]:
            self.log("Le média est en ATTENTE. Activation du script d'arrêt.")
            self.call_service("script/turn_on", entity_id="script.Lights_tv_stop")
        
        elif new == "off":  
            self.log("Le média est ÉTEINT. Activation du script d'arrêt.")
            self.call_service("script/turn_on", entity_id="script.Lights_tv_stop")