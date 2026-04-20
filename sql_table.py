import re
import psycopg2
import csv
from typing import List, Dict, Any


class SQLTable:
    def __init__(self, db_config: Dict[str, str], table_name: str, pk: str = "id"):
        self.db_config = db_config
        self._validate_name(table_name)
        self._validate_name(pk)

        self.table_name = table_name
        self.pk = pk

        self.connection = psycopg2.connect(**db_config)
        self.cursor = self.connection.cursor()

    @staticmethod
    def _validate_name(name: str) -> None:
        if not re.fullmatch(r"[A-Za-z0-9_]+", name):
            raise ValueError(f"Недопустимое имя: {name}")

    #  table 

    def create_table(self, columns: list, primary_key=None):
        parts = []
        auto_incr = None

        for column in columns:
            name = column["name"]
            col_type = column["type"]

            self._validate_name(name)

            if column.get("auto_increment", False):
                # SERIAL → современный вариант
                col_def = f'"{name}" INTEGER GENERATED ALWAYS AS IDENTITY'
                auto_incr = name
            else:
                col_def = f'"{name}" {col_type}'

            if not column.get("nullable", True):
                col_def += " NOT NULL"

            if column.get("unique", False):
                col_def += " UNIQUE"

            if "default" in column:
                col_def += f" DEFAULT {column['default']}"

            parts.append(col_def)

        if auto_incr:
            parts.append(f'PRIMARY KEY ("{auto_incr}")')
        elif primary_key:
            self._validate_name(primary_key)
            parts.append(f'PRIMARY KEY ("{primary_key}")')

        body = ",\n ".join(parts)

        query = f'''
        CREATE TABLE IF NOT EXISTS "{self.table_name}" (
        {body}
        );
        '''

        self.cursor.execute(query)
        self.connection.commit()

    #  select 

    def get_all(self):
        self.cursor.execute(f'SELECT * FROM "{self.table_name}"')
        return self.cursor.fetchall()

    def get_by_id(self, value: int):
        self.cursor.execute(
            f'SELECT * FROM "{self.table_name}" WHERE "{self.pk}" = %s',
            (value,)
        )
        return self.cursor.fetchone()

    def get_value(self, column_name: str, value: Any):
        self._validate_name(column_name)
        self.cursor.execute(
            f'SELECT * FROM "{self.table_name}" WHERE "{column_name}" = %s',
            (value,)
        )
        return self.cursor.fetchall()

    #  insert 

    def insert(self, data: Dict[str, Any]):
        columns = list(data.keys())

        for col in columns:
            self._validate_name(col)

        columns_str = ", ".join(f'"{col}"' for col in columns)
        placeholders = ", ".join(["%s"] * len(columns))
        values = tuple(data.values())

        query = f'INSERT INTO "{self.table_name}" ({columns_str}) VALUES ({placeholders})'
        self.cursor.execute(query, values)
        self.connection.commit()

    def insert_many(self, data_list: List[Dict[str, Any]]):
        if not data_list:
            return

        columns = list(data_list[0].keys())

        for col in columns:
            self._validate_name(col)

        # проверка одинаковых ключей
        for row in data_list:
            if list(row.keys()) != columns:
                raise ValueError("Все словари должны иметь одинаковые ключи")

        columns_str = ", ".join(f'"{col}"' for col in columns)
        placeholders = ", ".join(["%s"] * len(columns))
        values = [tuple(row[col] for col in columns) for row in data_list]

        query = f'INSERT INTO "{self.table_name}" ({columns_str}) VALUES ({placeholders})'
        self.cursor.executemany(query, values)
        self.connection.commit()

    #  update 

    def update(self, value: int, data: Dict[str, Any]):
        for col in data.keys():
            self._validate_name(col)

        set_values = ", ".join(f'"{k}" = %s' for k in data.keys())
        values = tuple(data.values()) + (value,)

        query = f'UPDATE "{self.table_name}" SET {set_values} WHERE "{self.pk}" = %s'
        self.cursor.execute(query, values)
        self.connection.commit()

    #  delete 

    def delete_by_id(self, value: int):
        self.cursor.execute(
            f'DELETE FROM "{self.table_name}" WHERE "{self.pk}" = %s',
            (value,)
        )
        self.connection.commit()

    def delete_table(self):
        self.cursor.execute(f'DROP TABLE IF EXISTS "{self.table_name}"')
        self.connection.commit()

    #  info 

    def describe_table(self):
        self.cursor.execute("""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = %s
        """, (self.table_name,))
        return self.cursor.fetchall()

    #  csv 

    def export_csv(self, filename: str):
        self.get_all()
        headers = [desc[0] for desc in self.cursor.description]
        rows = self.cursor.fetchall()

        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)

    def import_csv(self, filename: str):
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            if not reader.fieldnames:
                raise ValueError("CSV без заголовков")

            for col in reader.fieldnames:
                self._validate_name(col)

            self.insert_many(list(reader))

    #  close 

    def close(self):
        self.cursor.close()
        self.connection.close()


# конфиг
db_config = {
    "host": "localhost",
    "port": 5432,
    "user": "user",
    "password": "1234",
    "dbname": "mydb"
}

"""
фильтрация ввода
добавление функций join всех видов
добавление функций uion
автоматизировать добавленные функции
"""