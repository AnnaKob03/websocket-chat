import os
from dotenv import load_dotenv  # Для загрузки .env файла
import tornado.ioloop
import tornado.web
import tornado.websocket
import redis
import json
import threading
import asyncio
import uuid

# Загрузка переменных окружения из .env
load_dotenv()

# Настройки Redis из переменных окружения
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

# Подключение к Redis
redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

# Настройки Tornado из переменных окружения
TORNADO_PORT = int(os.getenv("TORNADO_PORT", 8888))

class WebSocketHandler(tornado.websocket.WebSocketHandler):
    """
    Обработчик WebSocket соединений для чата.
    """
    clients = set()  # Хранение активных WebSocket соединений

    def open(self):
        """
        Срабатывает при открытии нового WebSocket соединения.
        """
        # Получение имени пользователя или генерация уникального имени
        self.username = self.get_argument("username", None)
        if not self.username:
            self.username = f"User-{str(uuid.uuid4())[:8]}"

        self.clients.add(self)  # Добавление клиента в активный список
        redis_client.sadd("online_clients", self.username)  # Сохранение имени пользователя в Redis

        self.update_clients_list()  # Обновление списка клиентов

        # Отправка приветственного сообщения
        self.write_message(json.dumps({
            "type": "welcome",
            "message": f"Добро пожаловать в чат, {self.username}!"
        }))

    def on_message(self, message):
        """
        Обработка входящих сообщений от клиента.
        """
        # Форматирование данных сообщения
        data = {
            "type": "message",
            "data": {
                "sender": self.username,
                "message": message
            }
        }
        # Публикация сообщения в Redis Pub/Sub
        redis_client.publish('chat_channel', json.dumps(data))

    def on_close(self):
        """
        Срабатывает при закрытии WebSocket соединения.
        """
        self.clients.remove(self)  # Удаление клиента из активного списка
        redis_client.srem("online_clients", self.username)  # Удаление клиента из Redis

        self.update_clients_list()  # Обновление списка клиентов

    def check_origin(self, origin):
        """
        Разрешение запросов с других доменов.
        """
        return True

    def update_clients_list(self):
        """
        Обновление списка активных клиентов.
        """
        online_clients = list(redis_client.smembers("online_clients"))  # Получение клиентов из Redis

        # Форматирование данных для отправки
        data = {
            "type": "clients",
            "clients": online_clients
        }

        # Отправка обновлённого списка всем подключённым клиентам
        for client in self.clients:
            client.write_message(json.dumps(data))


async def redis_listener():
    """
    Асинхронный слушатель Pub/Sub канала Redis.
    """
    pubsub = redis_client.pubsub()
    pubsub.subscribe("chat_channel")  # Подписка на канал "chat_channel"
    for message in pubsub.listen():
        if message["type"] == "message":
            # Десериализация данных из сообщения
            data = json.loads(message["data"])
            # Отправка сообщения всем подключённым клиентам
            for client in WebSocketHandler.clients:
                client.write_message(json.dumps(data))


def start_redis_listener():
    """
    Запуск слушателя Redis в отдельном потоке.
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(redis_listener())


if __name__ == "__main__":
    # Настройка приложения Tornado
    app = tornado.web.Application([
        (r"/websocket", WebSocketHandler),  # Эндпоинт для WebSocket соединений
        (r"/(.*)", tornado.web.StaticFileHandler, {"path": "./static", "default_filename": "index.html"})  # Статические файлы
    ])
    app.listen(TORNADO_PORT)  # Слушаем порт из переменной окружения

    print(f"Сервер запущен: http://localhost:{TORNADO_PORT}")

    # Запуск Redis слушателя в отдельном потоке
    threading.Thread(target=start_redis_listener, daemon=True).start()

    # Запуск основного цикла Tornado
    tornado.ioloop.IOLoop.current().start()
