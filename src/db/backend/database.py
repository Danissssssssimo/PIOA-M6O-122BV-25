from abc import ABC, abstractmethod
from typing import Any
from .table import Table
from .errors import TableNotFoundError, TableAlreadyExistsError


class Database(ABC):
    """Абстрактный интерфейс для базы данных с CRUD операциями."""

    # ========== Методы управления таблицами ==========

    @abstractmethod
    def _table_exists(self, table_name: str) -> bool:
        """Проверяет существование таблицы."""
        pass

    @abstractmethod
    def _load_table(self, table_name: str) -> Table:
        """Загружает таблицу из хранилища."""
        pass

    @abstractmethod
    def _save_table(self, table_name: str, table: Table) -> None:
        """Сохраняет таблицу в хранилище."""
        pass

    # ========== Публичный CRUD-интерфейс ==========

    def create_table(self, table_name: str, columns: tuple[str, ...]) -> None:
        """Создаёт новую таблицу с указанными колонками."""
        if self._table_exists(table_name):
            raise TableAlreadyExistsError(
                f"Таблица '{table_name}' уже существует."
            )
        self._save_table(table_name, Table(columns))

    def create_record(self, table_name: str, record: dict[str, Any]) -> dict[str, Any]:
        """Создаёт новую запись в таблице."""
        table = self._load_table(table_name)
        table.insert_record(record)
        self._save_table(table_name, table)
        return record

    def select_records(self, table_name: str, **filters: Any) -> list[dict[str, Any]]:
        """Возвращает записи из таблицы, соответствующие фильтрам."""
        table = self._load_table(table_name)
        return table.select_records(**filters)

    def update_record(self, table_name: str, **updates: Any) -> dict[str, Any]:
        """Обновляет запись в таблице. Фильтр должен содержать filter_* поля."""
        table = self._load_table(table_name)
        updated = table.update_record(**updates)
        self._save_table(table_name, table)
        return updated

    def delete_record(self, table_name: str, **filters: Any) -> dict[str, Any]:
        """Удаляет запись из таблицы по фильтру."""
        table = self._load_table(table_name)
        deleted = table.delete_record(**filters)
        self._save_table(table_name, table)
        return deleted