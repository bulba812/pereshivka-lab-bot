from database import init_db, add_product_admin, get_products, get_all_products

print("🧪 Тестируем database.py...")

# 1. Инициализация БД
init_db()
print("✅ 1. init_db() — OK")

# 2. Добавляем тестовый товар
product_id = add_product_admin("Куртка Stone Island", 25000, "M,L", "test_photo_id")
print(f"✅ 2. add_product_admin() — OK (ID: {product_id})")

# 3. Получаем доступные товары
products = get_products()
print(f"✅ 3. get_products() — OK ({len(products)} товаров)")

# 4. Получаем ВСЕ товары (для админа)
all_products = get_all_products()
print(f"✅ 4. get_all_products() — OK ({len(all_products)} товаров)")

print("\n🎉 database.py РАБОТАЕТ ПЕРФЕКТНО!")
