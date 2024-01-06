import json

class Config:
    def __init__(self, config_file):
        with open(config_file, 'r') as f:
            self.config = json.load(f)

    @property
    def auto_swing(self):
        return self.config.get('auto_swing', {})

    @property
    def regain_stamina(self):
        return self.config.get('regain_stamina', {})

    @property
    def auto_eat(self):
        return self.config.get('auto_eat', {})

    @property
    def auto_eat_slots(self):
        return self.auto_eat.get('slots', {})

    @property
    def auto_drop_settings(self):
        return self.config.get('auto_drop_settings', {})
    
    