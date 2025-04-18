import sqlite3


def initialize_database():
    conn = sqlite3.connect('shop.db')
    cursor = conn.cursor()

    # Включаем поддержку внешних ключей
    cursor.execute("PRAGMA foreign_keys = ON")

    # Таблица users
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_telegram INTEGER UNIQUE NOT NULL,
            tag_telegram TEXT UNIQUE,
            role TEXT DEFAULT 'user' CHECK(role IN ('user', 'staff', 'owner')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Таблица products
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL CHECK(price >= 0),
            image BLOB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Таблица orders (переименована из "order", так как order - зарезервированное слово)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            address TEXT NOT NULL,
            total_price REAL NOT NULL CHECK(total_price >= 0),
            user_id INTEGER NOT NULL,
            status TEXT DEFAULT 'new' CHECK(status IN ('new', 'processing', 'delivering', 'delivered', 'completed', 'cancelled')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')

    # Таблица order_products (связующая таблица)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS order_products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            order_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL CHECK(quantity > 0),
            FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE RESTRICT,
            FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
            UNIQUE (product_id, order_id)
        )
    ''')

    # Создаем индексы для ускорения поиска
    # cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_telegram ON users(id_telegram)")
    # cursor.execute("CREATE INDEX IF NOT EXISTS idx_order_user ON orders(user_id)")
    # cursor.execute("CREATE INDEX IF NOT EXISTS idx_order_product ON order_products(order_id)")

    conn.commit()
    conn.close()


if __name__ == "__main__":
    initialize_database()