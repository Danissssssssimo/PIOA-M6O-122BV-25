import unittest
import tempfile
import shutil
from src.db.backend.memory import MemoryDatabase
from src.db.backend.file import FileDatabase


class TestDatabase(unittest.TestCase):
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    # ========== Тесты для MemoryDatabase ==========
    
    def test_memory_crud_flow(self):
        db = MemoryDatabase()
        table_name = "users"
        columns = ("id", "name", "age")
        
        # Create table
        db.create_table(table_name, columns)
        
        # Create record
        record = {"id": 1, "name": "John", "age": 20}
        db.create_record(table_name, record)
        
        # Read record
        records = db.select_records(table_name, id=1)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["name"], "John")
        
        # Update record
        db.update_record(table_name, filter_id=1, name="Jonathan")
        records = db.select_records(table_name, id=1)
        self.assertEqual(records[0]["name"], "Jonathan")
        
        # Delete record
        db.delete_record(table_name, id=1)
        records = db.select_records(table_name)
        self.assertEqual(len(records), 0)
    
    # ========== Тесты для FileDatabase ==========
    
    def test_file_crud_flow(self):
        db = FileDatabase(directory=self.temp_dir)
        table_name = "users"
        columns = ("id", "name", "age")
        
        db.create_table(table_name, columns)
        
        record = {"id": 1, "name": "John", "age": 20}
        db.create_record(table_name, record)
        
        records = db.select_records(table_name, id=1)
        self.assertEqual(len(records), 1)
        
        db.update_record(table_name, filter_id=1, name="Jonathan")
        records = db.select_records(table_name, id=1)
        self.assertEqual(records[0]["name"], "Jonathan")
        
        db.delete_record(table_name, id=1)
        records = db.select_records(table_name)
        self.assertEqual(len(records), 0)


if __name__ == "__main__":
    unittest.main()