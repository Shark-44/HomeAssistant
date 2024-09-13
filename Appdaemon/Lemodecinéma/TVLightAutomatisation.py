import appdaemon.plugins.hass.hassapi as hass

class TVLightAutomation(hass.Hass):

    def initialize(self):
        # Vérifier l'état actuel du switch Ambilight et démarrer en conséquence
        self.listen_state(self.switch_state_changed, "switch.65pus7304_12_ambilight_hue", new = "on", immediate = True)


    def switch_state_changed(self, entity, attribute, old, new, kwargs):
        # Démarrer l'écoute des états du média si le switch passe à "on"
        if new == "on":
            self.log("Ambilight switch turned ON. Starting media state listener.")
            self.listen_state(self.media_state_changed, "media_player.65pus7304_12_6")
        elif new == "off":
            self.log("Ambilight switch turned OFF. Stopping media state listener.")
    def media_state_changed(self, entity, attribute, old, new, kwargs):
        # Gestion des états du média
        if old in ("off", "standby", "unavailable", "paused", "unknown", "idle") and new == "playing":  
            self.log("Media is PLAYING. Turning off room lights.")
            self.call_service("script/turn_on", entity_id="script.lights_tv_play")
        
        elif old == "playing" and new == "paused": 
            self.log("Media is PAUSED. Activating pause scene.")
            self.call_service("script/turn_on", entity_id="script.lights_tv_pause")
        
        elif old in ["playing", "paused"] and new in ["standby", "unavailable", "paused", "unknown", "idle"]:
            self.log("Media is IDLE. Activating stop scene.")
            self.call_service("script/turn_on", entity_id="script.lights_tv_stop")
        
        elif new == "off":  
            self.log("Media is OFF. Activating stop scene.")
            self.call_service("script/turn_on", entity_id="script.lights_tv_stop")