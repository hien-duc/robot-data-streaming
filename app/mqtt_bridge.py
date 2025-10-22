import json
import threading
import paho.mqtt.client as mqtt
import asyncio

class MQTTBridge:
    def __init__(self, broker_host: str = "localhost", broker_port: int = 1883, loop: asyncio.AbstractEventLoop = None):
        self.host = broker_host
        self.port = broker_port
        self.client = mqtt.Client()
        self.loop = loop or asyncio.get_event_loop()
        # set callbacks
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def start(self):
        # run MQTT loop in background thread
        self.client.connect(self.host, self.port, keepalive=60)
        t = threading.Thread(target=self.client.loop_forever, daemon=True)
        t.start()

    def on_connect(self, client, userdata, flags, rc):
        print(f"MQTT connected: rc={rc}")
        # subscribe to VDA5050 topics
        client.subscribe("/vda5050/#")

    def on_message(self, client, userdata, msg):
        # parse topic: /vda5050/{manufacturer}/{serial}/{message_type}
        topic = msg.topic
        try:
            payload = msg.payload.decode('utf-8')
        except Exception:
            payload = None
        # fire-and-forget coroutine to update RobotState
        asyncio.run_coroutine_threadsafe(self._handle_message(topic, payload), self.loop)

    async def _handle_message(self, topic: str, payload: str):
        from app.core.robot_state import RobotState
        # topic parts
        parts = [p for p in topic.split('/') if p]
        # expect ['vda5050', manufacturer, serial, message_type]
        if len(parts) < 4:
            return
        _, manufacturer, serial, message_type = parts[:4]
        try:
            data = json.loads(payload) if payload else {}
        except Exception:
            data = {"raw": payload}
        rs = RobotState.get_instance()
        await rs.update_from_mqtt(manufacturer, serial, message_type, data)
