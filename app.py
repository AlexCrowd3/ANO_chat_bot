import logging
import datetime
import requests
import telebot
from telebot import types

# Настройки API сервиса
API_URL = "https://alexcrowd3-anochat-f80f.twc1.net/add_user"
TIMEOUT = 5
REVIEW_CHAT_ID = "@an0app"  # ID чата, куда будут отправляться отзывы (замените на реальный ID)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Создаем экземпляр бота
bot = telebot.TeleBot("7670677747:AAHpH1LEaYmXFZyctfCvxJAs00eX7rvf9d0")

# Словарь для отслеживания состояния пользователей
user_states = {}

def send_user_data(user_data):
    try:
        logger.info(f"Отправляем данные: {user_data}")
        headers = {'Content-Type': 'application/json'}
        response = requests.post(
            API_URL,
            json=user_data,
            headers=headers,
            timeout=TIMEOUT
        )
        if response.status_code != 200:
            logger.error(f"Ошибка {response.status_code}: {response.text}")
        else:
            logger.info("Данные успешно отправлены")
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка соединения: {e}")

@bot.message_handler(commands=['start'])
def start(message):
    user = message.from_user
    chat_id = message.chat.id
    date = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # Формируем данные для отправки
    user_data = {
        "name": user.first_name,
        "last_name": user.last_name if user.last_name else "Не указано",
        "telegram_id": user.id,
        "chat_id": chat_id,
        "date_of_registration": date
    }
    
    send_user_data(user_data)

    # Создаем основную клавиатуру с эмодзи
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton("/menu"))
    keyboard.add(types.KeyboardButton("/about"))
    keyboard.add(types.KeyboardButton("/review"))
    keyboard.add(types.KeyboardButton("/buy_n_coin"))
    
    bot.send_message(
        chat_id, 
        'Добро пожаловать в ANO! 🎉\nПривет, друг! 👋\nРад видеть тебя здесь. Я — твой помощник от ANO, и моя задача сделать так, чтобы ты узнал своих друзей и коллег совсем с другой стороны. Вместе мы раскроем секреты общения, поднимем настроение и сплотим коллектив. Готов начать?\nДавай сделаем вашу команду ещё ближе и дружнее! 😊', 
        reply_markup=keyboard
    )

@bot.message_handler(commands=['menu'])
def show_menu(message):
    user_id = message.from_user.id
    url = f"https://alexcrowd3-anochat-f80f.twc1.net?main_id={user_id}"
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Открыть приложение", url=url))
    
    bot.send_message(
        message.chat.id, 
        "Главное меню", 
        reply_markup=markup
    )

@bot.message_handler(commands=['about'])
def show_about(message):
    text = "ℹ️ О нас:\nANO — это пространство, где знакомые становятся ближе, а общение — увлекательным. 🌟\nВсё происходит в формате игры: участники задают вопросы или выбирают их из готовых вариантов приложения. А затем отвечают на них анонимно, раскрывая что-то неожиданное, интересное или даже забавное о себе. Это как секретный клуб, где каждый может быть честным, не боясь осуждения. \nС ANO вы узнаете друзей и коллег совсем с другой стороны — искренне, живо и с удовольствием! 💬✨"
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['contacts'])
def show_contacts(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Наш Telegram канал", url="https://t.me/an0app"))
    text = "Если у вас возникли проблемы с приложением или есть предложения по рекламе, доработке приложения\nПишите нам, контакты указаны в нашем канале))\nЕсли котите оставить отзыв, то просто пропишите /rewiev"
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['review'])
def review_start(message):
    chat_id = message.chat.id
    
    # Создаем кнопки "Да" и "Назад"
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("Да ✅"), types.KeyboardButton("Назад 🔙"))
    
    # Отправляем сообщение с вопросом и кнопками
    bot.send_message(chat_id, "Вы хотите оставить отзыв? ✍️", reply_markup=markup)
    
    # Устанавливаем состояние пользователя
    user_states[chat_id] = "awaiting_review_choice"

@bot.message_handler(func=lambda message: message.text in ["Да ✅", "Назад 🔙"])
def handle_review_choice(message):
    chat_id = message.chat.id
    user_state = user_states.get(chat_id)
    
    if user_state == "awaiting_review_choice":
        if message.text == "Да ✅":
            # Переходим к запросу отзыва
            bot.send_message(chat_id, "Пожалуйста, напишите ваш отзыв ниже 👇")
            user_states[chat_id] = "awaiting_review_text"
        elif message.text == "Назад 🔙":
            # Возвращаемся в меню
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.add(types.KeyboardButton("/menu"))
            keyboard.add(types.KeyboardButton("/about"))
            keyboard.add(types.KeyboardButton("/review"))
            bot.send_message(chat_id, "Вы вернулись в главное меню", reply_markup=keyboard)
            del user_states[chat_id]
            show_menu(message)

@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == "awaiting_review_text")
def handle_review_text(message):
    chat_id = message.chat.id
    review_text = message.text
    
    # Отправляем отзыв в определенный чат
    try:
        bot.send_message(REVIEW_CHAT_ID, f"📝 Новый отзыв от пользователя {message.from_user.first_name} {message.from_user.last_name}:\n\n{review_text}")
        bot.send_message(chat_id, "Спасибо за ваш отзыв! ❤️")
    except Exception as e:
        bot.send_message(chat_id, "Произошла ошибка при отправке отзыва. Попробуйте позже.")
        logger.error(f"Ошибка при отправке отзыва: {e}")
    
    # Возвращаем пользователя в меню
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton("/menu"))
    keyboard.add(types.KeyboardButton("/about"))
    keyboard.add(types.KeyboardButton("/review"))
    bot.send_message(chat_id, "Вы вернулись в главное меню", reply_markup=keyboard)
    del user_states[chat_id]
    show_menu(message)

if __name__ == '__main__':
    logger.info("Бот запущен 🚀")
    bot.polling(none_stop=True)