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

# Добавляем товар с изображением
# product_with_image = (
#     'Сок из ростков пшеницы Витграсс «Vitalis-life».',
#     'Состав: Витграсс, замороженный сок ростков пшеницы 30 порций по 30 мл.',
#     3333,
#     image_to_blob('card.png')  # Преобразуем картинку в бинарный формат
# )
#
# cursor.execute("""
#     INSERT INTO products (title, description, price, image)
#     VALUES (?, ?, ?, ?)
# """, product_with_image)
#
# product_with_image = (
#     'Смузи «Зеленый чиа». 300 мл.',
#     'Состав: семена чиа, пророщенная чечевица, зелёное яблоко, грецкие орехи, петрушка.',
#     333,
#     image_to_blob('card2.jpg')  # Преобразуем картинку в бинарный формат
# )
#
# cursor.execute("""
#     INSERT INTO products (title, description, price, image)
#     VALUES (?, ?, ?, ?)
# """, product_with_image)
#
# cursor.execute("""
#     UPDATE users SET is_owner = 1
# """)

# cursor.execute("""
#     INSERT INTO orders (address, total_price, user_id, status)
#     VALUES ('Донбасс2', 99999, 3, 'new')
# """)
#
# cursor.execute("""
#     INSERT INTO order_products (product_id, order_id, quantity)
#     VALUES (2, 4, 1)
# """)

# Сохраняем изменения
conn.commit()