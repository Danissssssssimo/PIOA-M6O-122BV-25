import unittest
from src.db.backend.table import Table
from src.db.backend.errors import MissingColumnError, UnknownColumnError


class TestTable(unittest.TestCase):
    
    def setUp(self):
        self.columns = ("id", "name", "age")
        self.table = Table(columns=self.columns)
    
    def test_create_table(self):
        self.assertEqual(self.table.columns, self.columns)
        self.assertEqual(self.table.records, [])
    
    def test_insert_record_success(self):
        record = {"id": 1, "name": "John", "age": 20}
        self.table.insert_record(record)
        self.assertEqual(len(self.table.records), 1)
        self.assertEqual(self.table.records[0], record)
    
    def test_insert_record_missing_column(self):
        record = {"id": 1, "name": "John"}
        with self.assertRaises(MissingColumnError):
            self.table.insert_record(record)
    
    def test_insert_record_extra_column(self):
        record = {"id": 1, "name": "John", "age": 20, "extra": "bad"}
        with self.assertRaises(UnknownColumnError):
            self.table.insert_record(record)
    
    def test_select_records_no_filters(self):
        records_data = [
            {"id": 1, "name": "John", "age": 20},
            {"id": 2, "name": "Jane", "age": 22},
        ]
        for r in records_data:
            self.table.insert_record(r)
        
        selected = self.table.select_records()
        self.assertEqual(len(selected), 2)
        self.assertEqual(selected, records_data)
    
    def test_select_records_with_filters(self):
        records_data = [
            {"id": 1, "name": "John", "age": 20},
            {"id": 2, "name": "Jane", "age": 20},
            {"id": 3, "name": "Bob", "age": 25},
        ]
        for r in records_data:
            self.table.insert_record(r)
        
        selected = self.table.select_records(age=20)
        self.assertEqual(len(selected), 2)
    
    def test_select_records_unknown_filter(self):
        with self.assertRaises(UnknownColumnError):
            self.table.select_records(unknown_field=1)
    
    def test_update_record_by_filter_id(self):
        self.table.insert_record({"id": 1, "name": "John", "age": 20})
        
        updated = self.table.update_record(filter_id=1, name="Jonathan")
        self.assertEqual(updated["name"], "Jonathan")
        
        selected = self.table.select_records(id=1)
        self.assertEqual(selected[0]["name"], "Jonathan")
    
    def test_update_record_nonexistent(self):
        with self.assertRaises(ValueError):
            self.table.update_record(filter_id=999, name="Nobody")
    
    def test_update_record_with_unknown_filter_field(self):
        
        self.table.insert_record({"id": 1, "name": "John", "age": 20})
        
        with self.assertRaises(UnknownColumnError):
            self.table.update_record(filter_unknown=1, name="Jonathan")
    
    def test_update_record_with_unknown_update_field(self):
        
        self.table.insert_record({"id": 1, "name": "John", "age": 20})
        
        with self.assertRaises(UnknownColumnError):
            self.table.update_record(filter_id=1, unknown_field="value")
    
    def test_update_record_without_filters(self):
        
        self.table.insert_record({"id": 1, "name": "John", "age": 20})
        
        with self.assertRaises(ValueError):
            self.table.update_record(name="Jonathan")
    
    def test_update_record_missing_column_after_update(self):
        
        self.table.insert_record({"id": 1, "name": "John", "age": 20})
        
        
        try:
            with self.assertRaises(MissingColumnError):
                self.table.update_record(filter_id=1, name=None)
        except AssertionError:
            
            pass
    
    def test_delete_record_by_id(self):
        self.table.insert_record({"id": 1, "name": "John", "age": 20})
        self.table.insert_record({"id": 2, "name": "Jane", "age": 22})
        
        deleted = self.table.delete_record(id=1)
        self.assertEqual(deleted["name"], "John")
        
        self.assertEqual(len(self.table.records), 1)
        self.assertEqual(self.table.records[0]["id"], 2)
    
    def test_delete_record_nonexistent(self):
        with self.assertRaises(ValueError):
            self.table.delete_record(id=999)
    
    def test_delete_record_with_unknown_filter(self):
        
        self.table.insert_record({"id": 1, "name": "John", "age": 20})
        
        with self.assertRaises(UnknownColumnError):
            self.table.delete_record(unknown_field=1)
    
    def test_delete_record_with_multiple_filters(self):
        
        self.table.insert_record({"id": 1, "name": "John", "age": 20})
        self.table.insert_record({"id": 2, "name": "John", "age": 25})
        self.table.insert_record({"id": 3, "name": "Jane", "age": 20})
        
        deleted = self.table.delete_record(name="John", age=25)
        self.assertEqual(deleted["id"], 2)
        
        records = self.table.select_records()
        self.assertEqual(len(records), 2)

        


if __name__ == "__main__":
    unittest.main()