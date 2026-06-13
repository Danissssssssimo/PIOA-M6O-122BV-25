def create_record():
    """Добавляет новую запись в существующую таблицу"""
    pass

def select_record():
    """Возвращает записи, подходящие под запрос или фильтр"""
    pass

def update_record():
    """Обновляет поля существующей записи по идентификатору или фильтру""" 
    pass

def delete_record():
    """Удаляет запись по идентификатору или фильтру"""
    pass


type StudentRecord = tuple[int, str, str, int, str]

Student: list[StudentRecord] = []

def create_record(
        student_id: int,
        first_name: str,
        second_name: str,
        age: int,
        sex: str,
) -> StudentRecord:
    
    if age < 0:
        raise ValueError("Поле age не может быть отрицательным")
    
    if any(record[0] == student_id for record in Student):
        raise ValueError(f"Запись с id={student_id} уже существует.")
    
    new_record: StudentRecord = (
        student_id,
        first_name.strip(),
        second_name.strip(),
        age,
        sex.strip(),
    )

    Student.append(new_record)

    return new_record

def select_record(
        student_id: int | None = None,
        first_name: str | None = None,
        second_name: str | None = None,
        age: int | None = None,
        sex: str | None = None,
) -> list[StudentRecord]:
    
    if (
        student_id is None
        and first_name is None
        and second_name is None
        and age is None
        and sex is None
    ):
        return Student.copy()
    
    result: list[StudentRecord] = []

    for record in Student:

        if student_id is not None and record[0] != student_id:
            continue
        if first_name is not None and record[1] != first_name:
            continue
        if second_name is not None and record[2] != second_name:
            continue
        if age is not None and record[3] != age:
            continue
        if sex is not None and record[4] != sex:
            continue

        result.append(record)
    return result
def update_record(
        student_id: int | None = None,
        first_name: str | None = None,
        second_name: str | None = None,
        age: int | None = None,
        sex: str | None = None,
    ) -> StudentRecord:

    index = -1
    for i, record in enumerate(Student):
        if record[0] == student_id:
            index = i
            break
    
    if index == -1:
        raise ValueError(f"Запись с id={student_id} не найдена.")
    
    current = Student[index]
    
    new_first_name = first_name if first_name is not None else current[1]
    new_second_name = second_name if second_name is not None else current[2]
    new_age = age if age is not None else current[3]
    new_sex = sex if sex is not None else current[4]

    if new_age < 0:
        raise ValueError("Поле age не может быть отрицательным")
    
    updated_record: StudentRecord = (
        student_id,
        new_first_name.strip(),
        new_second_name.strip(),
        new_age,
        new_sex.strip(),
    )

    Student[index] = updated_record

    return updated_record

def delete_record(student_id: int) -> StudentRecord:
    for i, record in enumerate(Student):
        if record[0] == student_id:
            deleted = Student.pop(i)
            return deleted
    raise ValueError(f"Запись с id={student_id} не найдена")






