import sqlite3
from datetime import datetime

class InventoryManager:
    def __init__(self, db_name="office_inventory.db"):
        self.db_name = db_name
        self.init_db()
    
    def init_db(self):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS inventory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    purchase_date TEXT NOT NULL,
                    status TEXT NOT NULL,
                    location TEXT NOT NULL,
                    responsible_person TEXT,
                    notes TEXT
                )
            ''')
            conn.commit()
    
    def create_item(self, name, category, quantity, purchase_date, status, location, responsible_person="", notes=""):
        try:
            if not all([name, category, purchase_date, status, location]):
                raise ValueError("Все обязательные поля должны быть заполнены")
            
            if quantity < 0:
                raise ValueError("Количество не может быть отрицательным")
            
            datetime.strptime(purchase_date, '%Y-%m-%d')
            
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO inventory 
                    (name, category, quantity, purchase_date, status, location, responsible_person, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (name, category, quantity, purchase_date, status, location, responsible_person, notes))
                conn.commit()
                print(f"✅ '{name}' добавлен!")
                
        except ValueError as e:
            print(f"❌ Ошибка: {e}")
        except sqlite3.Error as e:
            print(f"❌ Ошибка БД: {e}")
    
    def read_items(self, filters=None):
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                
                query = "SELECT * FROM inventory"
                params = []
                
                if filters:
                    conditions = []
                    for key, value in filters.items():
                        if value:
                            conditions.append(f"{key} LIKE ?")
                            params.append(f"%{value}%")
                    
                    if conditions:
                        query += " WHERE " + " AND ".join(conditions)
                
                query += " ORDER BY name"
                cursor.execute(query, params)
                return cursor.fetchall()
                
        except sqlite3.Error as e:
            print(f"❌ Ошибка чтения: {e}")
            return []
    
    def update_item(self, item_id, **kwargs):
        try:
            if not kwargs:
                print("❌ Нет данных для обновления")
                return
            
            valid_fields = ['name', 'category', 'quantity', 'purchase_date', 'status', 'location', 'responsible_person', 'notes']
            update_fields = []
            params = []
            
            for field, value in kwargs.items():
                if field in valid_fields and value is not None:
                    if field == 'quantity' and value < 0:
                        raise ValueError("Количество не может быть отрицательным")
                    
                    if field == 'purchase_date':
                        datetime.strptime(value, '%Y-%m-%d')
                    
                    update_fields.append(f"{field} = ?")
                    params.append(value)
            
            if not update_fields:
                print("❌ Нет полей для обновления")
                return
            
            params.append(item_id)
            
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute(f'UPDATE inventory SET {", ".join(update_fields)} WHERE id = ?', params)
                
                if cursor.rowcount == 0:
                    print(f"❌ ID {item_id} не найден")
                else:
                    print(f"✅ ID {item_id} обновлен!")
                conn.commit()
                
        except ValueError as e:
            print(f"❌ Ошибка: {e}")
        except sqlite3.Error as e:
            print(f"❌ Ошибка БД: {e}")
    
    def delete_item(self, item_id):
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM inventory WHERE id = ?", (item_id,))
                
                if cursor.rowcount == 0:
                    print(f"❌ ID {item_id} не найден")
                else:
                    print(f"✅ ID {item_id} удален!")
                conn.commit()
                
        except sqlite3.Error as e:
            print(f"❌ Ошибка удаления: {e}")
    
    def display_items(self, items=None):
        if items is None:
            items = self.read_items()
        
        if not items:
            print("📭 Записей не найдено")
            return
        
        print(f"\n{'='*100}")
        print(f"{'ID':<3} {'Название':<15} {'Категория':<12} {'Кол-во':<6} {'Дата':<10} {'Статус':<12} {'Место':<12} {'Ответственный':<12}")
        print(f"{'='*100}")
        
        for item in items:
            print(f"{item[0]:<3} {item[1]:<15} {item[2]:<12} {item[3]:<6} {item[4]:<10} {item[5]:<12} {item[6]:<12} {item[7]:<12}")
        
        print(f"{'='*100}")
        print(f"Всего: {len(items)}")

def main():
    manager = InventoryManager()
    
    while True:
        print("\n🏢 Учет инвентаря")
        print("1. 📋 Показать все")
        print("2. 🔍 Поиск")
        print("3. ➕ Добавить")
        print("4. ✏️  Редактировать")
        print("5. 🗑️  Удалить")
        print("6. 🚪 Выход")
        
        choice = input("\nВыберите действие (1-6): ").strip()
        
        if choice == '1':
            items = manager.read_items()
            manager.display_items(items)
            
        elif choice == '2':
            print("\n🔍 Поиск (оставьте пустым для пропуска)")
            name = input("Название: ").strip()
            category = input("Категория: ").strip()
            status = input("Статус: ").strip()
            location = input("Место: ").strip()
            
            filters = {'name': name, 'category': category, 'status': status, 'location': location}
            items = manager.read_items(filters)
            manager.display_items(items)
            
        elif choice == '3':
            print("\n➕ Добавить предмет")
            try:
                name = input("Название: ").strip()
                category = input("Категория: ").strip()
                quantity = int(input("Количество: ").strip())
                purchase_date = input("Дата (ГГГГ-ММ-ДД): ").strip()
                status = input("Статус: ").strip()
                location = input("Место: ").strip()
                responsible_person = input("Ответственный: ").strip()
                notes = input("Примечания: ").strip()
                
                manager.create_item(name, category, quantity, purchase_date, status, location, responsible_person, notes)
                
            except ValueError as e:
                print(f"❌ Ошибка: {e}")
                
        elif choice == '4':
            try:
                item_id = int(input("\n✏️  ID для редактирования: ").strip())
                
                print("Новые значения (пусто - не менять):")
                name = input("Название: ").strip() or None
                category = input("Категория: ").strip() or None
                quantity_input = input("Количество: ").strip()
                quantity = int(quantity_input) if quantity_input else None
                purchase_date = input("Дата: ").strip() or None
                status = input("Статус: ").strip() or None
                location = input("Место: ").strip() or None
                responsible_person = input("Ответственный: ").strip() or None
                notes = input("Примечания: ").strip() or None
                
                update_data = {
                    'name': name, 'category': category, 'quantity': quantity,
                    'purchase_date': purchase_date, 'status': status, 'location': location,
                    'responsible_person': responsible_person, 'notes': notes
                }
                
                update_data = {k: v for k, v in update_data.items() if v is not None}
                manager.update_item(item_id, **update_data)
                
            except ValueError:
                print("❌ Неверный формат")
                
        elif choice == '5':
            try:
                item_id = int(input("\n🗑️  ID для удаления: ").strip())
                confirm = input(f"Удалить ID {item_id}? (y/N): ").strip().lower()
                if confirm == 'y':
                    manager.delete_item(item_id)
            except ValueError:
                print("❌ Неверный ID")
                
        elif choice == '6':
            print("👋 Выход!")
            break
            
        else:
            print("❌ Неверный выбор")

if __name__ == "__main__":
    main()