import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()

DB_PATH = "shop.db"

def init_db():
    """Инициализация БД и создание таблицы products"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price INTEGER NOT NULL,
            sizes TEXT,
            photo_file_id TEXT,
            is_available INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ База данных инициализирована")

def get_products():
    """Получить все доступные товары"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, name, price, sizes, photo_file_id 
        FROM products 
        WHERE is_available = 1
        ORDER BY created_at DESC
    ''')
    
    products = cursor.fetchall()
    conn.close()
    return products

def get_all_products():
    """Получить ВСЕ товары (для админа)"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, name, price, sizes, photo_file_id, is_available 
        FROM products 
        ORDER BY created_at DESC
    ''')
    
    products = cursor.fetchall()
    conn.close()
    return products

def add_product_admin(name, price, sizes, photo_file_id):
    """Добавить товар (только админ)"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO products (name, price, sizes, photo_file_id, is_available)
        VALUES (?, ?, ?, ?, 1)
    ''', (name, price, sizes, photo_file_id))
    
    conn.commit()
    product_id = cursor.lastrowid
    conn.close()
    print(f"✅ Товар добавлен: ID={product_id}")
    return product_id

def remove_product(product_id):
    """Удалить товар по ID"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM products WHERE id = ?', (product_id,))
    deleted = cursor.rowcount
    conn.commit()
    conn.close()
    
    if deleted:
        print(f"✅ Товар ID={product_id} удалён")
        return True
    return False

def mark_sold(product_id):
    """Отметить товар как проданный"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('UPDATE products SET is_available = 0 WHERE id = ?', (product_id,))
    updated = cursor.rowcount
    conn.commit()
    conn.close()
    
    if updated:
        print(f"✅ Товар ID={product_id} помечен как продан")
        return True
    return False

def get_product_by_id(product_id):
    """Получить товар по ID"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,))
    product = cursor.fetchone()
    conn.close()
    return product
def mark_sold(product_id):
    """Отметить товар как проданный"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('UPDATE products SET is_available = 0 WHERE id = ?', (product_id,))
    updated = cursor.rowcount
    conn.commit()
    conn.close()
    
    if updated:
        print(f"✅ Товар ID={product_id} помечен как продан")
        return True
    return False

# Инициализация при импорте ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ←
init_db()

# Инициализация при импорте
init_db()
