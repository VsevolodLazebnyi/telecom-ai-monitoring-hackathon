import time
import random
import json
import redis
from loguru import logger

class TelecomDataSimulator:
    def __init__(self):
        self.redis_url = "redis://:admin123@redis:6379/0"
        self.redis_client = redis.Redis.from_url(self.redis_url, decode_responses=True)
        
        self.tariffs = [450, 690, 800, 1200]
        self.regions = ["Moscow", "SPb", "Kazan", "Novosibirsk", "Vladivostok"]
        self.error_codes = ["TIMEOUT", "HANDSHAKE_FAIL", "RADIO_LINK_FAILURE", "AUTH_FAILURE"]
        
        self.init_redis_data()

    def generate_phone_number(self):
        return f"+7911{random.randint(1000000, 9999999)}"

    def init_redis_data(self):
        """Инициализация тестовых данных в Redis"""
        try:
            for i in range(100):
                user_key = f"user:{i}"
                user_data = {
                    "user_id": str(i),
                    "phone": self.generate_phone_number(),
                    "tariff": str(random.choice(self.tariffs)),
                    "balance": str(random.randint(-500, 2000)),
                    "region": random.choice(self.regions),
                    "status": "active"
                }
                self.redis_client.hset(user_key, mapping=user_data)
            
            logger.info("✅ Initialized 100 users in Redis")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Redis data: {e}")

    def simulate_connection_issue(self):
        """Симуляция разрыва соединения"""
        try:
            user_id = random.randint(0, 99)
            user_key = f"user:{user_id}"
            user_data = self.redis_client.hgetall(user_key)
            
            if not user_data:
                return

            alert = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "type": "CONNECTION_FAILURE",
                "severity": random.choice(["WARNING", "CRITICAL"]),
                "user_id": user_data["user_id"],
                "phone": user_data["phone"],
                "region": user_data["region"],
                "details": {
                    "duration_sec": random.randint(10, 300),
                    "base_station": f"BS_{random.randint(1,50)}",
                    "error_code": random.choice(self.error_codes)
                }
            }
            
            alert_key = f"alert:{int(time.time())}:{user_id}"
            self.redis_client.setex(alert_key, 3600, json.dumps(alert))
            self.redis_client.incr("alerts:connection_failure:total")
            
            logger.warning(f"📡 Connection issue: {user_data['phone']} - {alert['details']['error_code']}")
            
        except Exception as e:
            logger.error(f"❌ Error simulating connection issue: {e}")

    def simulate_billing_error(self):
        """Симуляция ошибки биллинга"""
        try:
            user_id = random.randint(0, 99)
            user_key = f"user:{user_id}"
            user_data = self.redis_client.hgetall(user_key)
            
            if not user_data:
                return

            expected_charge = int(user_data["tariff"])
            actual_charge = int(expected_charge * random.uniform(0.5, 2.0))

            alert = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "type": "BILLING_ERROR",
                "severity": "HIGH",
                "user_id": user_data["user_id"],
                "phone": user_data["phone"],
                "region": user_data["region"],
                "details": {
                    "expected_charge": expected_charge,
                    "actual_charge": actual_charge,
                    "balance_before": user_data["balance"],
                    "transaction_id": f"TXN{random.randint(10000, 99999)}"
                }
            }
            new_balance = int(user_data["balance"]) - actual_charge
            self.redis_client.hset(user_key, "balance", str(new_balance))
            alert_key = f"alert:{int(time.time())}:{user_id}"
            self.redis_client.setex(alert_key, 3600, json.dumps(alert))
            self.redis_client.incr("alerts:billing_error:total")
            
            logger.error(f"💳 Billing error: {user_data['phone']} - Charged {actual_charge} instead of {expected_charge}")
            
        except Exception as e:
            logger.error(f"❌ Error simulating billing error: {e}")

    def simulate_traffic_spike(self):
        """Симуляция всплеска трафика"""
        try:
            alert = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "type": "TRAFFIC_SPIKE",
                "severity": "MEDIUM",
                "region": random.choice(self.regions),
                "details": {
                    "current_connections": random.randint(1000, 5000),
                    "normal_connections": 800,
                    "increase_percent": random.randint(50, 300)
                }
            }
            
            alert_key = f"alert:{int(time.time())}:traffic"
            self.redis_client.setex(alert_key, 1800, json.dumps(alert))
            self.redis_client.incr("alerts:traffic_spike:total")
            
            logger.info(f"📊 Traffic spike in {alert['region']}: {alert['details']['increase_percent']}% increase")
            
        except Exception as e:
            logger.error(f"❌ Error simulating traffic spike: {e}")

    def run_simulation(self):
        """Главный цикл симуляции"""
        logger.info("🎮 Starting telecom data simulation...")
        
        event_weights = {
            'connection': 0.4,
            'billing': 0.3, 
            'traffic': 0.2,
            'none': 0.1
        }
        
        event_types = list(event_weights.keys())
        weights = list(event_weights.values())
        
        while True:
            try:
                # Случайным образом выбираем тип события
                event_type = random.choices(event_types, weights=weights, k=1)[0]
                
                if event_type == 'connection':
                    self.simulate_connection_issue()
                elif event_type == 'billing':
                    self.simulate_billing_error()
                elif event_type == 'traffic':
                    self.simulate_traffic_spike()
                # else: 'none' - ничего не генерируем
                time.sleep(random.uniform(1, 5))
            except Exception as e:
                logger.error(f"❌ Error in simulation loop: {e}")
                time.sleep(5)

if __name__ == "__main__":
    simulator = TelecomDataSimulator()
    simulator.run_simulation()