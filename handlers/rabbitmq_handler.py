import pika
import json
import threading
from loguru import logger
from handlers.gpt4free_handler import Gpt4FreeHandler

class RabbitMQHandler:
    def __init__(self):
        self.rabbitmq_url = "amqp://admin:admin123@rabbitmq:5672/"
        self.gpt_handler = Gpt4FreeHandler()
        self.setup_consumers()

    def setup_consumers(self):
        try:
            connection = pika.BlockingConnection(pika.URLParameters(self.rabbitmq_url))
            channel = connection.channel()
            channel.queue_declare(queue='telecom_alerts', durable=True)
            
            def callback(ch, method, properties, body):
                try:
                    alert_data = json.loads(body)
                    logger.info(f"📨 Received alert: {alert_data['type']} for {alert_data.get('phone', 'N/A')}")
                    analysis = self.analyze_alert_with_ai(alert_data)
                    logger.info(f"🤖 AI Analysis: {analysis}")
                except json.JSONDecodeError as e:
                    logger.error(f"❌ Failed to parse alert JSON: {e}")
                except Exception as e:
                    logger.error(f"❌ Error processing alert: {e}")

            channel.basic_consume(
                queue='telecom_alerts', 
                on_message_callback=callback, 
                auto_ack=True
            )
            
            logger.info("✅ RabbitMQ consumer started for 'telecom_alerts' queue")
            consumer_thread = threading.Thread(target=channel.start_consuming, daemon=True)
            consumer_thread.start()
            
        except Exception as e:
            logger.error(f"❌ Failed to setup RabbitMQ consumer: {e}")

    def analyze_alert_with_ai(self, alert_data: dict) -> str:
        return self.gpt_handler.analyze_alert_with_ai(alert_data)

    def send_alert(self, alert_data: dict):
        try:
            connection = pika.BlockingConnection(pika.URLParameters(self.rabbitmq_url))
            channel = connection.channel()
            
            channel.queue_declare(queue='telecom_alerts', durable=True)
            
            channel.basic_publish(
                exchange='',
                routing_key='telecom_alerts',
                body=json.dumps(alert_data),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # persistent message
                )
            )
            
            connection.close()
            logger.info(f"✅ Alert sent to RabbitMQ: {alert_data['type']}")
            
        except Exception as e:
            logger.error(f"❌ Failed to send alert to RabbitMQ: {e}")