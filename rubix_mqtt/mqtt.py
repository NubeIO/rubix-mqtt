import logging
import time
import uuid
from typing import Callable, List

import paho.mqtt.client as mqtt
from rubix_mqtt.setting import MqttSettingBase

logger = logging.getLogger(__name__)


class MqttClientBase:

    def __init__(self):
        self.__client = None
        self.__config = None
        self.__subscribe_topics = None
        self.__callback = None

    @property
    def client(self) -> mqtt.Client:
        return self.__client

    @property
    def config(self) -> MqttSettingBase:
        return self.__config

    @property
    def subscribe_topics(self) -> List[str]:
        return self.__subscribe_topics

    def start(self, config: MqttSettingBase, subscribe_topics: List[str] = None, callback: Callable = lambda: None):
        self.__config = config
        self.__subscribe_topics = subscribe_topics or []
        self.__callback = callback
        config_name: str = f'{self.config.name}-{str(uuid.uuid4())}'
        logger.info(f'Starting MQTT client[{config_name}]...')
        self.__client = mqtt.Client(config_name)
        if self.config.authentication:
            self.__client.username_pw_set(self.config.username, self.config.password)
        if self.config.ssl:
            self.__client.tls_set()
        self.__client.on_connect = self._on_connect
        self.__client.on_message = self._on_message
        if self.config.attempt_reconnect_on_unavailable:
            while True:
                try:
                    self.__client.connect_async(self.config.host, self.config.port, self.config.keepalive)
                    self.__client.loop_start()
                    break
                except (ConnectionRefusedError, OSError) as e:
                    logger.error(
                        f'MQTT client[{self.config.name}] connection failure {self.to_string()} -> '
                        f'{type(e).__name__}. Attempting reconnect in '
                        f'{self.config.attempt_reconnect_secs} seconds')
                    time.sleep(self.config.attempt_reconnect_secs)
        else:
            try:
                self.__client.connect_async(self.config.host, self.config.port, self.config.keepalive)
            except Exception as e:
                # catching so can set _client to None so publish_cov doesn't stack messages forever
                self.__client = None
                logger.error(str(e))
                return
        logger.info(f'MQTT client {config_name} connected {self.to_string()}')

    def status(self) -> bool:
        return bool(self.config and self.config.enabled and self.__client and self.__client.is_connected())

    def to_string(self) -> str:
        return f'{self.config.host}:{self.config.port}'

    def _on_connect(self, client, userdata, flags, reason_code, properties=None):
        if reason_code > 0:
            reasons = {
                1: 'Connection refused - incorrect protocol version',
                2: 'Connection refused - invalid client identifier',
                3: 'Connection refused - server unavailable',
                4: 'Connection refused - bad username or password',
                5: 'Connection refused - not authorised'
            }
            reason = reasons.get(reason_code, 'unknown')
            self.__client = None
            raise Exception(f'MQTT Connection Failure: {reason}')
        self._on_connection_successful()

    def _on_connection_successful(self):
        logger.info(f'MQTT sub to {self.subscribe_topics}')
        if self.__callback:
            self.__callback()
        for subscribe_topic in self.subscribe_topics:
            self.__client.subscribe(subscribe_topic)

    def _on_message(self, client, userdata, message):
        pass
