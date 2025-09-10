import sqlite3

# Подключаемся к базе

# Функция для преобразования изображения в BLOB
def image_to_blob(image_path):
    with open(image_path, 'rb') as f:
        return f.read()

conn = sqlite3.connect('shop.db')
cursor = conn.cursor()


# Добавляем товар без изображения



# cursor.execute("""
#     INSERT INTO products (title, description, price)
#     VALUES (?, ?, ?)
# """, ('Телефон', 'Новый смартфон', 29999.99))

product_with_image = (
    'Топпинг “Vitalis-life” медово-лимонно-имбирный',
    'Состав: Медово-лимонно-имбирный 100% натуральный, с сохранением всех полезных свойств, благодаря самой современной шоковой заморозке.',
    1355,
    image_to_blob('card2.png')  # Преобразуем картинку в бинарный формат
)
# #
cursor.execute("""
    INSERT INTO products (title, description, price, image)
    VALUES (?, ?, ?, ?)
""", product_with_image)
#
# product_with_image = (
#     'Смузи «Зеленый чиа». 300 мл.',
#     'Состав: семена чиа, пророщенная чечевица, зелёное яблоко, грецкие орехи, петрушка.',
#     333,
#     image_to_blob('card2.png')  # Преобразуем картинку в бинарный формат
# )
#
# cursor.execute("""
#     INSERT INTO products (title, description, price, image)
#     VALUES (?, ?, ?, ?)
# """, product_with_image)

cursor.execute("""
    UPDATE users SET role = 'staff'
    WHERE id = 1
""")

# cursor.execute("""
#     INSERT INTO orders (address, total_
#     price, user_id, status)
#     VALUES ('Test', 3333, 3, 'new')
# """)
#
# cursor.execute("""
#     INSERT INTO order_products (product_id, order_id, quantity)
#     VALUES (2, 3, 1)
# """)

# Сохраняем изменения
conn.commit()