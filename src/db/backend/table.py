from typing import Any

from .errors import MissingColumnError, UnknownColumnError


class Table:
    """Таблица с фиксированным набором колонок."""

    def __init__(self, columns: tuple[str, ...], records: list[dict[str, Any]] | None = None) -> None:
        self.columns = columns
        self.records: list[dict[str, Any]] = []

        if records is not None:
            for record in records:
                self.insert_record(record)

    def insert_record(self, record: dict[str, Any]) -> None:
        
        missing_columns = [column for column in self.columns if column not in record]
        if missing_columns: 
            raise MissingColumnError(
                f"Отсутствует поле '{missing_columns[0]}' в записи."
            )

        extra_columns = [column for column in record if column not in self.columns]
        if extra_columns:
            raise UnknownColumnError(
                f"Поле '{extra_columns[0]}' не определено в структуре таблицы."
            )

        self.records.append(record.copy())

    def select_records(self, **filters: Any) -> list[dict[str, Any]]:
        
        unknown_filters = [key for key in filters if key not in self.columns]
        if unknown_filters:
            raise UnknownColumnError(
                f"Поле '{unknown_filters[0]}' не определено в структуре таблицы."
            )

        if not filters:
            return [record.copy() for record in self.records]

        result: list[dict[str, Any]] = []
        for record in self.records:
            if all(record.get(key) == value for key, value in filters.items()):
                result.append(record.copy())

        return result
    
    def update_record(self, **updates: Any) -> dict[str, Any]:
       
        
        filters = {}
        new_values = {}
        
        for key, value in updates.items():
            if key.startswith("filter_"):
                filter_key = key[7:]  
                if filter_key not in self.columns:
                    raise UnknownColumnError(f"Поле '{filter_key}' не определено в структуре таблицы.")
                filters[filter_key] = value
            else:
                if key not in self.columns:
                    raise UnknownColumnError(f"Поле '{key}' не определено в структуре таблицы.")
                new_values[key] = value

        if not filters:
            raise ValueError("Не указаны фильтры для поиска записи (используйте filter_*)")

        
        for i, record in enumerate(self.records):
            if all(record.get(k) == v for k, v in filters.items()):
                
                updated_record = record.copy()
                updated_record.update(new_values)
                
                
                missing_columns = [col for col in self.columns if col not in updated_record]
                if missing_columns: 
                    raise MissingColumnError(
                        f"После обновления отсутствует поле '{missing_columns[0]}'"
                    )
                
                self.records[i] = updated_record
                return updated_record.copy()
        
        raise ValueError(f"Запись с фильтрами {filters} не найдена.")

    def delete_record(self, **filters: Any) -> dict[str, Any]:
        
        
        for key in filters:
            if key not in self.columns:
                raise UnknownColumnError(f"Поле '{key}' не определено в структуре таблицы.")
        
        
        for i, record in enumerate(self.records):
            if all(record.get(k) == v for k, v in filters.items()):
                deleted = self.records.pop(i)
                return deleted.copy()
        
        raise ValueError(f"Запись с фильтрами {filters} не найдена.")