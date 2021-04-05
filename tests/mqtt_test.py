import logging

from rubix_mqtt.mqtt import MqttClientBase
from rubix_mqtt.setting import MqttSettingBase

log_format = '%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(format=log_format, level=logging.DEBUG)

if __name__ == '__main__':
    client = MqttClientBase()
    client.start(MqttSettingBase(), subscribe_topics=['test1', 'test2'])
