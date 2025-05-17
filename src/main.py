from src.parser_manager import ParserManager
import json


if __name__ == '__main__':
    with open('./src/config.json', 'r') as f:
        config_data = json.load(f)
    ParserManager(config_data['settings']['base_radius'], config_data['settings']['base_angle'], config_data['settings']['platform_radius'], config_data['settings']['platform_angle']).parse().run()
