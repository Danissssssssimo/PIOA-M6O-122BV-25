import unittest
import tempfile
import os
import shutil
import json
from pathlib import Path
from src.db.backend.file import FileDatabase
from src.db.backend.table import Table
from src.db.backend.errors import TableNotFoundError, InvalidStorageDataError


class TestFileDatabase(unittest.TestCase):
    
    def setUp(self):
        """Создаём временную папку для тестов"""
        self.temp_dir = tempfile.mkdtemp()
        self.db = FileDatabase(directory=self.temp_dir)
    
    def tearDown(self):
        """Удаляем временную папку после тестов"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_create_and_load_table(self):
        """Создание и загрузка таблицы"""
        columns = ("id", "name", "age")
        table = Table(columns=columns)
        table.insert_record({"id": 1, "name": "John", "age": 20})
        
        self.db._save_table("users", table)
        loaded = self.db._load_table("users")
        
        self.assertEqual(loaded.columns, columns)
        self.assertEqual(len(loaded.records), 1)
        self.assertEqual(loaded.records[0]["name"], "John")
    
    def test_table_not_found(self):
        """Ошибка при загрузке несуществующей таблицы"""
        with self.assertRaises(TableNotFoundError):
            self.db._load_table("nonexistent")
    
    def test_table_exists(self):
        """Проверка существования таблицы"""
        self.assertFalse(self.db._table_exists("users"))
        
        columns = ("id", "name", "age")
        table = Table(columns=columns)
        self.db._save_table("users", table)
        
        self.assertTrue(self.db._table_exists("users"))
    
    def test_persistence(self):
        """Проверка сохранения данных между экземплярами"""
        # Создаём таблицу и добавляем данные
        columns = ("id", "name", "age")
        table = Table(columns=columns)
        table.insert_record({"id": 1, "name": "John", "age": 20})
        self.db._save_table("users", table)
        
        # Создаём новый экземпляр БД с той же директорией
        new_db = FileDatabase(directory=self.temp_dir)
        loaded_table = new_db._load_table("users")
        
        self.assertEqual(len(loaded_table.records), 1)
        self.assertEqual(loaded_table.records[0]["name"], "John")
    
    def test_save_overwrites(self):
        """Сохранение перезаписывает существующую таблицу"""
        columns = ("id", "name", "age")
        
        table1 = Table(columns=columns)
        table1.insert_record({"id": 1, "name": "John", "age": 20})
        self.db._save_table("users", table1)
        
        table2 = Table(columns=columns)
        table2.insert_record({"id": 2, "name": "Jane", "age": 22})
        self.db._save_table("users", table2)
        
        loaded = self.db._load_table("users")
        self.assertEqual(len(loaded.records), 1)
        self.assertEqual(loaded.records[0]["name"], "Jane")
    
    def test_multiple_tables(self):
        """Работа с несколькими таблицами"""
        columns1 = ("id", "name")
        table1 = Table(columns=columns1)
        table1.insert_record({"id": 1, "name": "John"})
        self.db._save_table("users", table1)
        
        columns2 = ("id", "title")
        table2 = Table(columns=columns2)
        table2.insert_record({"id": 1, "title": "Admin"})
        self.db._save_table("roles", table2)
        
        loaded_users = self.db._load_table("users")
        loaded_roles = self.db._load_table("roles")
        
        self.assertEqual(len(loaded_users.records), 1)
        self.assertEqual(len(loaded_roles.records), 1)
        self.assertEqual(loaded_users.records[0]["name"], "John")
        self.assertEqual(loaded_roles.records[0]["title"], "Admin")
    
    def test_get_table_path(self):
        """Проверка пути к файлу таблицы"""
        table_path = self.db._get_table_path("test_table")
        expected_path = Path(self.temp_dir) / "test_table.json"
        self.assertEqual(table_path, expected_path)

    def test_load_corrupted_json(self):
        """Загрузка повреждённого JSON-файла"""
        from src.db.backend.errors import InvalidStorageDataError
        
        # Создаём нормальную таблицу
        columns = ("id", "name")
        table = Table(columns=columns)
        table.insert_record({"id": 1, "name": "John"})
        self.db._save_table("users", table)
        
        
        table_path = self.db._get_table_path("users")
        with open(table_path, 'w') as f:
            f.write("{corrupted json data")
        
        
        with self.assertRaises(InvalidStorageDataError):
            self.db._load_table("users")

    def test_load_invalid_structure(self):
        """Загрузка файла с неправильной структурой (нет columns или records)"""
        from src.db.backend.errors import InvalidStorageDataError
        
        
        table_path = self.db._get_table_path("bad_table")
        with open(table_path, 'w') as f:
            json.dump({"wrong": "structure"}, f)
        
        with self.assertRaises(InvalidStorageDataError):
            self.db._load_table("bad_table")


if __name__ == "__main__":
    unittest.main()