import unittest
import tempfile
import shutil
from src.db.backend.memory import MemoryDatabase
from src.db.backend.file import FileDatabase
from src.db.backend.table import Table
from src.db.backend.errors import TableNotFoundError


class TestDatabase(unittest.TestCase):
    
    def setUp(self):
        """Создаём временную папку для тестов file database"""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Удаляем временную папку после тестов"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    # ========== Тесты для MemoryDatabase ==========
    
    def test_memory_table_exists(self):
        """Проверка _table_exists у MemoryDatabase"""
        db = MemoryDatabase()
        table_name = "users"
        
        # Не существует
        self.assertFalse(db._table_exists(table_name))
        
        # Создаём таблицу
        columns = ("id", "name")
        table = Table(columns=columns)
        db._save_table(table_name, table)
        
        # Существует
        self.assertTrue(db._table_exists(table_name))
    
    def test_memory_save_and_load_table(self):
        """Проверка _save_table и _load_table у MemoryDatabase"""
        db = MemoryDatabase()
        table_name = "users"
        columns = ("id", "name")
        table = Table(columns=columns)
        table.insert_record({"id": 1, "name": "John"})
        
        db._save_table(table_name, table)
        loaded = db._load_table(table_name)
        
        self.assertEqual(loaded.columns, columns)
        self.assertEqual(len(loaded.records), 1)
        self.assertEqual(loaded.records[0]["name"], "John")
    
    def test_memory_load_nonexistent_table(self):
        """Загрузка несуществующей таблицы из MemoryDatabase"""
        db = MemoryDatabase()
        
        with self.assertRaises(TableNotFoundError):
            db._load_table("nonexistent")
    
    # ========== Тесты для FileDatabase ==========
    
    def test_file_table_exists(self):
        """Проверка _table_exists у FileDatabase"""
        db = FileDatabase(directory=self.temp_dir)
        table_name = "users"
        
        # Не существует
        self.assertFalse(db._table_exists(table_name))
        
        # Создаём таблицу
        columns = ("id", "name")
        table = Table(columns=columns)
        db._save_table(table_name, table)
        
        # Существует
        self.assertTrue(db._table_exists(table_name))
    
    def test_file_save_and_load_table(self):
        """Проверка _save_table и _load_table у FileDatabase"""
        db = FileDatabase(directory=self.temp_dir)
        table_name = "users"
        columns = ("id", "name")
        table = Table(columns=columns)
        table.insert_record({"id": 1, "name": "John"})
        
        db._save_table(table_name, table)
        loaded = db._load_table(table_name)
        
        self.assertEqual(loaded.columns, columns)
        self.assertEqual(len(loaded.records), 1)
        self.assertEqual(loaded.records[0]["name"], "John")
    
    def test_file_load_nonexistent_table(self):
        """Загрузка несуществующей таблицы из FileDatabase"""
        db = FileDatabase(directory=self.temp_dir)
        
        with self.assertRaises(TableNotFoundError):
            db._load_table("nonexistent")



    def test_create_table_success(self):
        """Создание новой таблицы"""
        db = MemoryDatabase()
        table_name = "new_table"
        columns = ("id", "name")
        
        # Таблицы ещё нет
        self.assertFalse(db._table_exists(table_name))
        
        # Создаём таблицу
        db.create_table(table_name, columns)
        
        # Таблица должна существовать
        self.assertTrue(db._table_exists(table_name))
        
        # Проверяем, что таблица правильная
        table = db._load_table(table_name)
        self.assertEqual(table.columns, columns)

    def test_create_table_already_exists(self):
        """Ошибка при создании уже существующей таблицы"""
        from src.db.backend.errors import TableAlreadyExistsError
        
        db = MemoryDatabase()
        table_name = "existing_table"
        columns = ("id", "name")
        
        db.create_table(table_name, columns)
        
        with self.assertRaises(TableAlreadyExistsError):
            db.create_table(table_name, columns)

    def test_memory_insert_record(self):
        """Вставка записи в таблицу через MemoryDatabase"""
        db = MemoryDatabase()
        table_name = "users"
        columns = ("id", "name", "age")
        
        # Создаём таблицу
        db.create_table(table_name, columns)
        
        # Вставляем запись
        record = {"id": 1, "name": "John", "age": 20}
        db.insert_record(table_name, record)
        
        # Проверяем, что запись вставилась
        table = db._load_table(table_name)
        self.assertEqual(len(table.records), 1)
        self.assertEqual(table.records[0]["name"], "John")

    def test_file_insert_record(self):
        """Вставка записи в таблицу через FileDatabase"""
        db = FileDatabase(directory=self.temp_dir)
        table_name = "users"
        columns = ("id", "name", "age")
        
        # Создаём таблицу
        db.create_table(table_name, columns)
        
        # Вставляем запись
        record = {"id": 1, "name": "John", "age": 20}
        db.insert_record(table_name, record)
        
        # Проверяем, что запись вставилась
        table = db._load_table(table_name)
        self.assertEqual(len(table.records), 1)
        self.assertEqual(table.records[0]["name"], "John")
        
        # Создаём новый экземпляр и проверяем, что запись сохранилась
        new_db = FileDatabase(directory=self.temp_dir)
        table = new_db._load_table(table_name)
        self.assertEqual(len(table.records), 1)


if __name__ == "__main__":
    unittest.main()