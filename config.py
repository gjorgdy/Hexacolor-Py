import json

class Config():

    def __init__(self):
        try:
            with open('config.json') as config_file:
                self.config = json.load(config_file)
                #print(json.dumps(self.config, indent=4))
                config_file.close()
        except:
            config_file = open('config.json', 'x')
            standard_config = {
                'version': '1.0',
                'devices': {},
                'canvas': {
                    'monitor': 1,
                    'ratio': None
                }
            }
            self.config = standard_config
            config_file.write(json.dumps(standard_config, indent=4))
            config_file.close()

    def update_config(self, updated_config):
        config_file = open('config.json', 'w')
        config_file.write(json.dumps(updated_config, indent=4))
        config_file.close()

    def get_device(self, device_id):
        try:
            return self.config['devices'][device_id]
        except:
            return None

    def get_canvas(self):
        return self.config['canvas']

    def register_device(self, sdk, device_index):
        device = sdk.get_device_info(device_index)

        if str(device.id) in list(self.config['devices'].keys()):
            return {}

        device_id = device.id
        device_dict = {
            'model': device.model,
            'led_count': device.led_count,
            'height': 100,
            'width': 100,
            'left': 0,
            'top': 0
        }

        self.config['devices'][str(device_id)] = device_dict
        self.update_config(self.config)
        return device_dict