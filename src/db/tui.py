

def _print_menu() -> None:
    print("\n=== База студентов ===")
    print("1. Добавить запись")
    print("2. Показать все записи")
    print("3. Найти записи по фильтру")
    print("4. Обновить запись")
    print("5. Удалить запись")
    print("0. Выход")


def _read_int(prompt: str) -> int:
    while True:
        raw = input(prompt).strip()
        try:
            return int(raw)
        except ValueError:
            print("Ошибка: введите целое число.")


def _read_optional_int(prompt: str) -> int | None:
    while True:
        raw = input(prompt).strip()
        if raw == "":
            return None
        try:
            return int(raw)
        except ValueError:
            print("Ошибка: введите целое число или оставьте поле пустым.")


def _print_records(records: list[tuple[int, str, str, int, str]]) -> None:
    if not records:
        print("Записи не найдены")
        return
    
    print("\nРезультаты:")
    for record in records:
        print(f"  ID: {record[0]} | Имя: {record[1]} | Фамилия: {record[2]} | Возраст: {record[3]} | Пол: {record[4]}")


class TUI:
    def __init__(self) -> None:
        from src.db.backend.memory import MemoryDatabase
        from src.db.backend.file import FileDatabase
        
        print("\nВыберите тип базы данных:")
        print("1. In-memory (данные в оперативной памяти)")
        print("2. File database (сохранение в файл)")

        choice = input("Введите номер: ").strip()
        
        if choice == "2":
            self.database = FileDatabase()
            print("Используется файловая база данных")
        else:
            self.database = MemoryDatabase()
            print("Используется память (данные не сохранятся после закрытия)")
        
        # Получаем или создаём таблицу студентов
        self.table_name = "students"
        try:
            self.student_table = self.database._load_table(self.table_name)
        except:
            # Таблицы нет — создаём новую с нужными колонками
            from src.db.backend.table import Table
            columns = ("id", "first_name", "second_name", "age", "sex")
            self.student_table = Table(columns=columns)
            self.database._save_table(self.table_name, self.student_table)

        def _add_student(self) -> None:
            print("\n=== Добавление записи ===")

            student_id = _read_int("ID: ")
            first_name = input("Имя: ").strip()
            second_name = input("Фамилия: ").strip()
            age = _read_int("Возраст: ")
            sex = input("Пол (М/Ж): ").strip()

            try:
                # Проверяем, нет ли уже такого ID
                existing = self.student_table.select_records(id=student_id)
                if existing:
                    print(f" Ошибка: Запись с id={student_id} уже существует.")
                    return

                # Создаём словарь-запись
                record = {
                    "id": student_id,
                    "first_name": first_name,
                    "second_name": second_name,
                    "age": age,
                    "sex": sex,
                }
                
                self.student_table.insert_record(record)
                self.database._save_table(self.table_name, self.student_table)
                print(f" Запись добавлена: {record}")

            except Exception as exc:
                print(f" Ошибка: {exc}")

    def _show_all_students(self) -> None:
        print("\n=== Все записи ===")
        records = self.student_table.select_records()
        _print_records(records)

    def _find_students_by_filter(self) -> None:
        print("\n=== Поиск по фильтру ===")
        print("(Enter = пропустить поле)")

        student_id = _read_optional_int("ID: ")
        first_name = input("Имя: ").strip() or None
        second_name = input("Фамилия: ").strip() or None
        age = _read_optional_int("Возраст: ")
        sex = input("Пол (М/Ж): ").strip() or None

        records = self.student_table.select_records(
            student_id=student_id,
            first_name=first_name,
            second_name=second_name,
            age=age,
            sex=sex,
        )
        _print_records(records)

    def _update_student(self) -> None:
        print("\n=== Обновление записи ===")
        
        student_id = _read_int("ID записи для обновления: ")
        
        existing = self.student_table.select_records(id=student_id)
        if not existing:
            print(f"✗ Запись с ID={student_id} не найдена")
            return
        
        print("(Enter = оставить без изменений)")
        
        updates = {"filter_id": student_id}  
        
        first_name = input("Новое имя: ").strip()
        if first_name:
            updates["first_name"] = first_name
        
        second_name = input("Новая фамилия: ").strip()
        if second_name:
            updates["second_name"] = second_name
        
        age = _read_optional_int("Новый возраст: ")
        if age is not None:
            updates["age"] = age
        
        sex = input("Новый пол (М/Ж): ").strip()
        if sex:
            updates["sex"] = sex

        try:
            updated = self.student_table.update_record(**updates)
            self.database._save_table(self.table_name, self.student_table)
            print(f"✓ Запись обновлена: {updated}")
        except Exception as exc:
            print(f"✗ Ошибка: {exc}")

    def _delete_student(self) -> None:
        print("\n=== Удаление записи ===")
        
        student_id = _read_int("ID записи для удаления: ")

        try:
            # Сначала показываем, что удаляем
            to_delete = self.student_table.select_records(student_id=student_id)
            if not to_delete:
                print(f"✗ Запись с ID={student_id} не найдена")
                return
            
            print(f"Будет удалена запись: {to_delete[0]}")
            confirm = input("Подтвердите удаление (y/n): ").strip().lower()
            
            if confirm == 'y':
                deleted = self.student_table.delete_record(student_id)
                print(f"✓ Запись удалена: {deleted}")
                # Сохраняем изменения
                self.database._save_table(self.table_name, self.student_table)
            else:
                print("Удаление отменено")

        except ValueError as exc:
            print(f"✗ Ошибка: {exc}")

    def run(self) -> None:
        print("\n=== Добро пожаловать в систему управления студентами ===")
        
        while True:
            _print_menu()
            action = input("Выберите действие: ").strip()

            if action == "1":
                self._add_student()
            elif action == "2":
                self._show_all_students()
            elif action == "3":
                self._find_students_by_filter()
            elif action == "4":
                self._update_student()
            elif action == "5":
                self._delete_student()
            elif action == "0":
                print("Выход из программы. До свидания!")
                break
            else:
                print("Неизвестная команда. Попробуйте снова (0-5).")


# Точка входа
def run() -> None:
    app = TUI()
    app.run()


if __name__ == "__main__":
    run()