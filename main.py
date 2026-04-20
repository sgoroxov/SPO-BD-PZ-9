from sql_table import SQLTable, db_config


#  ИНИЦИАЛИЗАЦИЯ

users = SQLTable(db_config, "users")
orders = SQLTable(db_config, "orders")

#  СОЗДАНИЕ ТАБЛИЦ

users.create_table([
    {"name": "id", "type": "INT", "auto_increment": True},
    {"name": "name", "type": "TEXT", "nullable": False},
    {"name": "age", "type": "INT"}
])

orders.create_table([
    {"name": "id", "type": "INT", "auto_increment": True},
    {"name": "user_id", "type": "INT"},
    {"name": "product", "type": "TEXT"},
    {"name": "price", "type": "INT"}
])

#  INSERT

users.insert({"name": "Alice", "age": 25})
users.insert({"name": "Bob", "age": 30})

orders.insert_many([
    {"user_id": 1, "product": "Laptop", "price": 1000},
    {"user_id": 1, "product": "Mouse", "price": 50},
    {"user_id": 2, "product": "Keyboard", "price": 150}
])

#  SELECT

print("\n--- Все пользователи ---")
print(users.get_all())

print("\n--- Пользователь по id ---")
print(users.get_by_id(1))

print("\n--- Поиск по значению ---")
print(users.get_value("name", "Alice"))

#  UPDATE

users.update(1, {"age": 26})
print("\n--- После обновления ---")
print(users.get_by_id(1))

#  JOIN

print("\n--- INNER JOIN ---")
print(users.inner_join("orders", "users.id = orders.user_id"))

print("\n--- LEFT JOIN ---")
print(users.left_join("orders", "users.id = orders.user_id"))

#  UNION

print("\n--- UNION ---")
# ВАЖНО: одинаковые колонки!
print(users.union("users", ["id", "name"]))

#  QUERY BUILDER

print("\n--- Query Builder: простой SELECT ---")
print(users.select(["id", "name"]).execute())

print("\n--- Query Builder: WHERE ---")
print(users.select().where("age > 25").execute())

print("\n--- Query Builder: JOIN ---")
print(
    users.select(["users.id", "name", "product", "price"])
    .join("orders", "users.id = orders.user_id")
    .execute()
)

print("\n--- Query Builder: сложный запрос ---")
print(
    users.select(["users.id", "name", "price"])
    .join("orders", "users.id = orders.user_id")
    .where("price > 100")
    .execute()
)

#  CSV

users.export_csv("users.csv")
print("\nCSV экспорт выполнен")

#  ЗАВЕРШЕНИЕ

users.close()
orders.close()
