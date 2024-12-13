// Установка WebSocket соединения с сервером
const ws = new WebSocket("ws://localhost:8888/websocket");

// Обработчик входящих сообщений от сервера
ws.onmessage = (event) => {
    try {
        const data = JSON.parse(event.data);

        // Обработка приветственного сообщения
        if (data.type === "welcome") {
            displayChatMessage("System", data.message, "system");
        }

        // Обработка обычных сообщений
        if (data.type === "message") {
            const { sender, message } = data.data;
            displayChatMessage(sender, message, "user");
        }

        // Обновление списка клиентов онлайн
        if (data.type === "clients") {
            updateClientsList(data.clients);
        }
    } catch (error) {
        console.error("Ошибка при обработке входящего сообщения:", error);
        console.error("Содержимое сообщения:", event.data);
    }
};

// Функция для отображения сообщения в чате
const displayChatMessage = (sender, message, messageType) => {
    const chat = document.getElementById("chat");
    const messageElement = document.createElement("div");

    // Стилизация сообщений в зависимости от типа
    messageElement.textContent = `${sender}: ${message}`;
    messageElement.classList.add("message");
    if (messageType === "system") {
        messageElement.classList.add("system");
    } else {
        messageElement.classList.add("user");
    }

    chat.appendChild(messageElement);

    // Автопрокрутка вниз для новых сообщений
    chat.scrollTop = chat.scrollHeight;
};

// Функция для обновления списка клиентов онлайн
const updateClientsList = (clients) => {
    const clientsList = document.getElementById("clients");
    clientsList.innerHTML = ""; // Очистка текущего списка

    clients.forEach((client) => {
        const clientItem = document.createElement("div");
        clientItem.textContent = client;
        clientItem.classList.add("client");
        clientsList.appendChild(clientItem);
    });
};

// Функция для отправки сообщения
const sendMessage = () => {
    const input = document.getElementById("message");
    const message = input.value.trim();

    if (message) {
        ws.send(message); // Отправка сообщения через WebSocket
        input.value = ""; // Очистка поля ввода
    }
};

// Стилизация через CSS (включено прямо в JS для простоты)
const style = document.createElement("style");
style.textContent = `
    body {
        font-family: Arial, sans-serif;
        background-color: #f0f0f5;
        margin: 0;
        padding: 0;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 100vh;
    }
    h1 {
        color: #444;
    }
    .container {
        background-color: #fff;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        width: 80%;
        max-width: 600px;
        padding: 20px;
    }
    #clients, #chat {
        border: 1px solid #ddd;
        border-radius: 5px;
        padding: 10px;
        margin-bottom: 15px;
        overflow-y: auto;
    }
    #clients {
        background-color: #e8f5e9;
        height: 100px;
    }
    #chat {
        background-color: #fce4ec;
        height: 300px;
    }
    #message-container {
        display: flex;
        gap: 10px;
    }
    #message {
        flex: 1;
        padding: 10px;
        border: 1px solid #ccc;
        border-radius: 5px;
        outline: none;
        font-size: 16px;
    }
    #message:focus {
        border-color: #66afe9;
        box-shadow: 0 0 5px rgba(102, 175, 233, 0.6);
    }
    button {
        padding: 10px 20px;
        background-color: #4caf50;
        color: white;
        border: none;
        border-radius: 5px;
        font-size: 16px;
        cursor: pointer;
    }
    button:hover {
        background-color: #45a049;
    }
    .message {
        margin-bottom: 5px;
    }
    .message.system {
        color: #777;
        font-style: italic;
    }
    .message.user {
        color: #000;
    }
    .client {
        font-weight: bold;
        color: #2e7d32;
    }
`;
document.head.appendChild(style);
