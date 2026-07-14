import telebot
import sqlite3
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# 1. Твои настройки
TOKEN = 'ТОКЕН'
bot = telebot.TeleBot(TOKEN)

# Если захочешь ограничить доступ к /admin, впиши сюда свой Telegram ID
# Узнать его можно через бота @getmyid_bot
ADMIN_ID = 5966765250


#  БАЗА ДАННЫХ (Создание и подключение) 
def init_db():
    conn = sqlite3.connect('shop.db')
    cursor = conn.cursor()
    # Создаем таблицу заказов, если ее еще нет
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            item_name TEXT
        )
    ''')
    conn.commit()
    conn.close()


# Запускаем создание базы при старте скрипта
init_db()


#  КАТЕГОРИИ И СВЯЗЬ С МЕНЕДЖЕРОМ 
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = InlineKeyboardMarkup(row_width=1)

    # Кнопки категорий
    btn1 = InlineKeyboardButton("📱 Электроника", callback_data="category_tech")
    btn2 = InlineKeyboardButton("👕 Одежда", callback_data="category_clothes")

    # Кнопка-ссылка на менеджера (вставь свой юзернейм без @)
    btn_manager = InlineKeyboardButton("👨‍💻 Связаться с менеджером", url="https://t.me/твой_юзернейм")

    markup.add(btn1, btn2, btn_manager)
    bot.send_message(message.chat.id, "Добро пожаловать в магазин! Выберите категорию:", reply_markup=markup)


# ФОТО ТОВАРОВ ПО КАТЕГОРИЯМ 
@bot.callback_query_handler(func=lambda call: call.data.startswith("category_"))
def show_category(call):
    bot.answer_callback_query(call.id)  # Убираем часики загрузки

    if call.data == "category_tech":
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("Купить за 5000 руб.", callback_data="buy_Смартфон"))

        # Отправляем фото по прямой ссылке
        photo_url = "https://via.placeholder.com/400x300.png?text=SmartPhone"
        bot.send_photo(call.message.chat.id, photo_url, caption="Смартфон X-Pro\nОтличный телефон!",
                       reply_markup=markup)

    elif call.data == "category_clothes":
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("Купить за 1500 руб.", callback_data="buy_Футболка"))

        photo_url = "https://via.placeholder.com/400x300.png?text=T-Shirt"
        bot.send_photo(call.message.chat.id, photo_url, caption="Футболка с логотипом\n100% хлопок.",
                       reply_markup=markup)


# СОХРАНЕНИЕ ЗАКАЗА В SQLITE 
@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_"))
def process_buy(call):
    # Достаем название товара из callback_data (например, из "buy_Смартфон" получаем "Смартфон")
    item_name = call.data.split("_")[1]
    user_id = call.from_user.id
    username = call.from_user.username or "Без_юзернейма"

    # Записываем в базу
    conn = sqlite3.connect('shop.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO orders (user_id, username, item_name) VALUES (?, ?, ?)", (user_id, username, item_name))
    conn.commit()
    conn.close()

    bot.answer_callback_query(call.id, "Товар добавлен в заказ!")
    bot.send_message(call.message.chat.id, f"✅ Вы успешно заказали: {item_name}. Наш менеджер скоро напишет вам.")


# ПАНЕЛЬ АДМИНИСТРАТОРА (/admin)
@bot.message_handler(commands=['admin'])
def admin_panel(message):
    # Простая проверка на админа

    # Читаем заказы из базы
    conn = sqlite3.connect('shop.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, item_name FROM orders")
    orders = cursor.fetchall()
    conn.close()

    if not orders:
        bot.send_message(message.chat.id, "Заказов пока нет 🤷‍♂️")
        return

    text = "📦 **Список заказов:**\n\n"
    for order in orders:
        text += f"ID: {order[0]} | Клиент: @{order[1]} | Товар: {order[2]}\n"

    bot.send_message(message.chat.id, text)


# Запуск бота
if __name__ == '__main__':
    print("Бот запущен. Нажми Ctrl+C для остановки.")
    bot.polling(none_stop=True)
