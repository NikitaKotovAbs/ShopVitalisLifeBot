import sqlite3
from io import BytesIO


def get_available_juices():
    """Получаем список доступных соков из базы данных"""
    conn = sqlite3.connect('app/utils/shop.db')
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT title, description, price, image 
            FROM products 
        """)

        juices = []
        for title, desc, price, image in cursor.fetchall():
            img_obj = BytesIO(image) if image else None
            juices.append({
                'title': title,
                'description': desc,
                'price': price,
                'image': img_obj
            })
        print(juices)
        return juices
    finally:
        conn.close()