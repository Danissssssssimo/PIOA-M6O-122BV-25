import unittest
from src.db.backend.memory import StudentTable
from src.db.backend.errors import InvalidAgeError, DuplicateIDError


class TestMemory(unittest.TestCase):
    
    def setUp(self):
        """Создаём новый экземпляр таблицы перед каждым тестом"""
        self.student_table = StudentTable()
        self.assertIsInstance(self.student_table, StudentTable)
    
    # ========== Тесты для create_record ==========
    
    def test_create_record_success(self):
        test_data = (1, "John", "Doe", 20, "M")
        record = self.student_table.create_record(*test_data)
        self.assertEqual(record, test_data)
    
    def test_create_record_multiple(self):
        cases = [
            (1, "John", "Doe", 20, "M"),
            (2, "Jane", "Smith", 22, "F"),
            (3, "Alice", "Johnson", 19, "F"),
            (4, "Bob", "Brown", 21, "M"),
            (5, "Charlie", "Davis", 18, "M"),
        ]
        for test_data in cases:
            with self.subTest(test_data=test_data):
                record = self.student_table.create_record(*test_data)
                self.assertEqual(record, test_data)
        all_records = self.student_table.select_record()
        self.assertEqual(len(all_records), 5)
    
    def test_create_record_negative_age(self):
        with self.assertRaises(InvalidAgeError) as context:
            self.student_table.create_record(1, "John", "Doe", -5, "M")
        self.assertEqual(str(context.exception), "Поле age не может быть отрицательным.")
    
    def test_create_record_duplicate_id(self):
        self.student_table.create_record(1, "John", "Doe", 20, "M")
        with self.assertRaises(DuplicateIDError) as context:
            self.student_table.create_record(1, "Jane", "Smith", 22, "F")
        self.assertEqual(str(context.exception), "Запись с id=1 уже существует.")
    
    def test_create_record_strips_whitespace(self):
        record = self.student_table.create_record(1, "  John  ", "  Doe  ", 20, "  M  ")
        self.assertEqual(record, (1, "John", "Doe", 20, "M"))
    
    # ========== Тесты для select_record ==========
    
    def test_select_record_no_filters(self):
        test_datas = [(1, "John", "Doe", 20, "M"), (2, "Jane", "Smith", 22, "F")]
        for test_data in test_datas:
            self.student_table.create_record(*test_data)
        records = self.student_table.select_record()
        self.assertEqual(len(records), 2)
        self.assertEqual(records, test_datas)
    
    def test_select_record_empty(self):
        records = self.student_table.select_record()
        self.assertEqual(records, [])
    
    def test_select_record_by_student_id(self):
        test_datas = [(1, "John", "Doe", 20, "M"), (2, "Jane", "Smith", 22, "F")]
        for test_data in test_datas:
            self.student_table.create_record(*test_data)
        records = self.student_table.select_record(student_id=1)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0], test_datas[0])
    
    def test_select_record_by_first_name(self):
        test_datas = [(1, "John", "Doe", 20, "M"), (2, "Jane", "Smith", 22, "F")]
        for test_data in test_datas:
            self.student_table.create_record(*test_data)
        records = self.student_table.select_record(first_name="Jane")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0][1], "Jane")
    
    def test_select_record_by_second_name(self):
        test_datas = [(1, "John", "Doe", 20, "M"), (2, "Jane", "Smith", 22, "F")]
        for test_data in test_datas:
            self.student_table.create_record(*test_data)
        records = self.student_table.select_record(second_name="Smith")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0][2], "Smith")
    
    def test_select_record_by_age(self):
        test_datas = [(1, "John", "Doe", 20, "M"), (2, "Jane", "Smith", 20, "F"), (3, "Bob", "Brown", 25, "M")]
        for test_data in test_datas:
            self.student_table.create_record(*test_data)
        records = self.student_table.select_record(age=20)
        self.assertEqual(len(records), 2)
    
    def test_select_record_by_sex(self):
        test_datas = [(1, "John", "Doe", 20, "M"), (2, "Jane", "Smith", 22, "F")]
        for test_data in test_datas:
            self.student_table.create_record(*test_data)
        records = self.student_table.select_record(sex="F")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0][4], "F")
    
    def test_select_record_multiple_filters(self):
        test_datas = [(1, "John", "Doe", 20, "M"), (2, "John", "Smith", 25, "M"), (3, "Jane", "Doe", 20, "F")]
        for test_data in test_datas:
            self.student_table.create_record(*test_data)
        records = self.student_table.select_record(first_name="John", age=20)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0], test_datas[0])
    
    def test_select_record_no_match(self):
        self.student_table.create_record(1, "John", "Doe", 20, "M")
        records = self.student_table.select_record(age=99)
        self.assertEqual(records, [])
    
    def test_select_record_with_none_values(self):
        self.student_table.create_record(1, "John", "Doe", 20, "M")
        records = self.student_table.select_record(first_name=None)
        self.assertEqual(len(records), 1)
    
    def test_select_record_with_all_filters(self):
        self.student_table.create_record(1, "John", "Doe", 20, "M")
        records = self.student_table.select_record(
            student_id=1, first_name="John", second_name="Doe", age=20, sex="M"
        )
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0][0], 1)
    
    # ========== Тесты для update_record ==========
    
    def test_update_record_first_name(self):
        self.student_table.create_record(1, "John", "Doe", 20, "M")
        updated = self.student_table.update_record(student_id=1, first_name="Jonathan")
        self.assertEqual(updated[1], "Jonathan")
        records = self.student_table.select_record(student_id=1)
        self.assertEqual(records[0][1], "Jonathan")
    
    def test_update_record_second_name(self):
        self.student_table.create_record(1, "John", "Doe", 20, "M")
        updated = self.student_table.update_record(student_id=1, second_name="Smith")
        self.assertEqual(updated[2], "Smith")
    
    def test_update_record_age(self):
        self.student_table.create_record(1, "John", "Doe", 20, "M")
        updated = self.student_table.update_record(student_id=1, age=25)
        self.assertEqual(updated[3], 25)
    
    def test_update_record_sex(self):
        self.student_table.create_record(1, "John", "Doe", 20, "M")
        updated = self.student_table.update_record(student_id=1, sex="F")
        self.assertEqual(updated[4], "F")
    
    def test_update_record_multiple_fields(self):
        self.student_table.create_record(1, "John", "Doe", 20, "M")
        updated = self.student_table.update_record(student_id=1, first_name="Jonathan", age=25)
        self.assertEqual(updated[1], "Jonathan")
        self.assertEqual(updated[3], 25)
    
    def test_update_record_nonexistent(self):
        with self.assertRaises(ValueError) as context:
            self.student_table.update_record(student_id=999, first_name="Nobody")
        self.assertEqual(str(context.exception), "Запись с id=999 не найдена.")
    
    def test_update_record_negative_age(self):
        self.student_table.create_record(1, "John", "Doe", 20, "M")
        with self.assertRaises(InvalidAgeError):
            self.student_table.update_record(student_id=1, age=-5)
    
    def test_update_record_no_changes(self):
        self.student_table.create_record(1, "John", "Doe", 20, "M")
        updated = self.student_table.update_record(student_id=1)
        self.assertEqual(updated, (1, "John", "Doe", 20, "M"))
    
    def test_update_record_strips_whitespace(self):
        self.student_table.create_record(1, "John", "Doe", 20, "M")
        updated = self.student_table.update_record(
            student_id=1, first_name="  Jonathan  ", second_name="  Smith  "
        )
        self.assertEqual(updated[1], "Jonathan")
        self.assertEqual(updated[2], "Smith")
    
    def test_update_record_with_same_values(self):
        self.student_table.create_record(1, "John", "Doe", 20, "M")
        updated = self.student_table.update_record(
            student_id=1, first_name="John", second_name="Doe", age=20, sex="M"
        )
        self.assertEqual(updated, (1, "John", "Doe", 20, "M"))
    
    # ========== Тесты для delete_record ==========
    
    def test_delete_record_success(self):
        self.student_table.create_record(1, "John", "Doe", 20, "M")
        self.student_table.create_record(2, "Jane", "Smith", 22, "F")
        deleted = self.student_table.delete_record(1)
        self.assertEqual(deleted, (1, "John", "Doe", 20, "M"))
        records = self.student_table.select_record()
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0][0], 2)
    
    def test_delete_record_nonexistent(self):
        with self.assertRaises(ValueError) as context:
            self.student_table.delete_record(999)
        self.assertEqual(str(context.exception), "Запись с id=999 не найдена.")
    
    def test_delete_record_last_record(self):
        self.student_table.create_record(1, "John", "Doe", 20, "M")
        deleted = self.student_table.delete_record(1)
        self.assertEqual(deleted, (1, "John", "Doe", 20, "M"))
        records = self.student_table.select_record()
        self.assertEqual(records, [])
    
    def test_delete_record_multiple_calls(self):
        self.student_table.create_record(1, "John", "Doe", 20, "M")
        self.student_table.create_record(2, "Jane", "Smith", 22, "F")
        self.student_table.create_record(3, "Bob", "Brown", 25, "M")
        
        deleted1 = self.student_table.delete_record(2)
        self.assertEqual(deleted1[0], 2)
        deleted2 = self.student_table.delete_record(1)
        self.assertEqual(deleted2[0], 1)
        
        records = self.student_table.select_record()
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0][0], 3)
    
    # ========== Интеграционный тест ==========
    
    def test_full_crud_flow(self):
        self.student_table.create_record(1, "John", "Doe", 20, "M")
        self.student_table.create_record(2, "Jane", "Smith", 22, "F")
        
        records = self.student_table.select_record()
        self.assertEqual(len(records), 2)
        
        self.student_table.update_record(student_id=1, first_name="Jonathan")
        records = self.student_table.select_record(student_id=1)
        self.assertEqual(records[0][1], "Jonathan")
        
        self.student_table.delete_record(1)
        records = self.student_table.select_record()
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0][0], 2)

    def test_edge_cases(self):
        """Краевые случаи"""
        # Возраст = 0
        record = self.student_table.create_record(1, "Zero", "Age", 0, "M")
        self.assertEqual(record[3], 0)
        
        # Пустые строки
        record = self.student_table.create_record(2, "", "", 20, "")
        self.assertEqual(record[1], "")
        self.assertEqual(record[2], "")
        self.assertEqual(record[4], "")
        
        # Обновление возраста на 0
        self.student_table.update_record(student_id=2, age=0)
        
        # Обновление полей на пустые строки
        self.student_table.update_record(student_id=2, first_name="", second_name="", sex="")

    # Добавьте в конец класса TestMemory

    def test_select_record_with_all_none_filters_explicit(self):
        """Все фильтры явно равны None"""
        self.student_table.create_record(1, "John", "Doe", 20, "M")
        self.student_table.create_record(2, "Jane", "Smith", 22, "F")
        
        records = self.student_table.select_record(
            student_id=None,
            first_name=None,
            second_name=None,
            age=None,
            sex=None
        )
        self.assertEqual(len(records), 2)

    def test_select_record_with_mixed_none_and_values(self):
        """Смешанные фильтры (часть None, часть значения)"""
        self.student_table.create_record(1, "John", "Doe", 20, "M")
        self.student_table.create_record(2, "Jane", "Smith", 22, "F")
        self.student_table.create_record(3, "John", "Smith", 25, "M")
        
        records = self.student_table.select_record(
            first_name="John",
            second_name=None,
            age=None
        )
        self.assertEqual(len(records), 2)  # John Doe и John Smith

    def test_update_record_age_zero(self):
        """Обновление возраста на 0 (граничное значение)"""
        self.student_table.create_record(1, "John", "Doe", 20, "M")
        
        updated = self.student_table.update_record(student_id=1, age=0)
        self.assertEqual(updated[3], 0)

    def test_update_record_age_large(self):
        """Обновление возраста на большое значение"""
        self.student_table.create_record(1, "John", "Doe", 20, "M")
        
        updated = self.student_table.update_record(student_id=1, age=150)
        self.assertEqual(updated[3], 150)

    def test_delete_record_all_sequential(self):
        """Последовательное удаление всех записей"""
        self.student_table.create_record(1, "First", "A", 20, "M")
        self.student_table.create_record(2, "Second", "B", 21, "F")
        self.student_table.create_record(3, "Third", "C", 22, "M")
        
        self.student_table.delete_record(1)
        self.student_table.delete_record(2)
        self.student_table.delete_record(3)
        
        records = self.student_table.select_record()
        self.assertEqual(len(records), 0)

    def test_delete_record_twice_same_id(self):
        """Двукратное удаление одного ID (второй раз ошибка)"""
        self.student_table.create_record(1, "John", "Doe", 20, "M")
        
        deleted = self.student_table.delete_record(1)
        self.assertEqual(deleted[0], 1)
        
        with self.assertRaises(ValueError):
            self.student_table.delete_record(1)


if __name__ == "__main__":
    unittest.main()