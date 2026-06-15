import json
from pathlib import Path

from .database import Database
from .errors import InvalidStorageDataError, TableNotFoundError, StorageIOError
from .table import Table


class FileDatabase(Database):
    """База данных, которая хранит таблицы в JSON-файлах."""

    def __init__(self, directory: str = "data") -> None:
        self.directory = Path(directory)
        try:
            self.directory.mkdir(parents=True, exist_ok=True)
        except OSError as error:
            raise StorageIOError(
                f"Не удалось создать директорию для БД '{directory}': {error}"
            ) from error

    def _get_table_path(self, table_name: str) -> Path:
        return self.directory / f"{table_name}.json"

    def _table_exists(self, table_name: str) -> bool:
        return self._get_table_path(table_name).exists()

    def _load_table(self, table_name: str) -> Table:
        table_path = self._get_table_path(table_name)
        if not table_path.exists():
            raise TableNotFoundError(
                f"Таблица '{table_name}' не существует."
            )
        try:
            with table_path.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except json.JSONDecodeError as error:
            raise InvalidStorageDataError(
                "Файл таблицы содержит некорректный JSON."
            ) from error
        except OSError as error:
            raise StorageIOError(
                f"Ошибка доступа к файлу таблицы '{table_name}': {error}"
            ) from error
        return self._deserialize_table(data)

    def _save_table(self, table_name: str, table: Table) -> None:
        table_path = self._get_table_path(table_name)
        data = self._serialize_table(table)
        try:
            with table_path.open("w", encoding="utf-8") as file:
                json.dump(data, file, indent=2, ensure_ascii=False)
        except OSError as error:
            raise StorageIOError(
                f"Ошибка сохранения таблицы '{table_name}': {error}"
            ) from error

    def _serialize_table(self, table: Table) -> dict:
        return {
            "columns": list(table.columns),
            "records": table.records,
        }

    def _deserialize_table(self, data: dict) -> Table:
        if "columns" not in data or "records" not in data:
            raise InvalidStorageDataError(
                "Файл таблицы имеет некорректную структуру."
            )
        return Table(columns=tuple(data["columns"]), records=data["records"])