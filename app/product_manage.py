from typing import Dict

class ProductManager:
    _instance = None
    user_products: Dict[int, Dict[int, int]] = {}  # {user_id: {product_id: quantity}}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def add_product(self, user_id: int, product_id: int):
        """Добавляет продукт в корзину пользователя"""
        if user_id not in self.user_products:
            self.user_products[user_id] = {}
        self.user_products[user_id][product_id] = self.user_products[user_id].get(product_id, 0) + 1

    def remove_product(self, user_id: int, product_id: int):
        """Удаляет продукт из корзины пользователя"""
        if user_id in self.user_products and product_id in self.user_products[user_id]:
            self.user_products[user_id][product_id] -= 1
            if self.user_products[user_id][product_id] <= 0:
                del self.user_products[user_id][product_id]

    def get_products(self, user_id: int) -> Dict[int, int]:
        """Возвращает все продукты пользователя"""
        return self.user_products.get(user_id, {})

    def clear_products(self, user_id: int):
        """Очищает корзину пользователя"""
        if user_id in self.user_products:
            del self.user_products[user_id]