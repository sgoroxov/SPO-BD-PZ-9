from sql_table import SQLTable, db_config

users = SQLTable(db_config, "users")
orders = SQLTable(db_config, "orders")

users.delete_table()
orders.delete_table()

users.create_table([
    {"name": "id", "type": "INT", "auto_increment": True},
    {"name": "name", "type": "TEXT"},
    {"name": "age", "type": "INT"}
])

orders.create_table([
    {"name": "id", "type": "INT", "auto_increment": True},
    {"name": "user_id", "type": "INT"},
    {"name": "product", "type": "TEXT"},
    {"name": "price", "type": "INT"}
])

users.insert_many([
    {"name": "Alice", "age": 25},
    {"name": "Bob", "age": 30}
])

orders.insert_many([
    {"user_id": 1, "product": "Laptop", "price": 1000},
    {"user_id": 1, "product": "Mouse", "price": 50},
    {"user_id": 2, "product": "Keyboard", "price": 150}
])

print("\n--- Все пользователи ---")
print(users.get_all())

print("\n--- Пользователь по id ---")
print(users.get_by_id(1))

print("\n--- Поиск по значению ---")
print(users.get_value("name", "Alice"))

users.update(1, {"age": 26})

print("\n--- После обновления ---")
print(users.get_by_id(1))

# --- JOIN ---

print("\n--- INNER JOIN ---")
users._select = []
users._join = []
users._where = []

print(
    users
    .select("users.id", "name", "product", "price")
    .inner_join("orders", "users.id", "orders.user_id")
    .execute()
)

print("\n--- LEFT JOIN ---")
users._select = []
users._join = []
users._where = []

print(
    users
    .select("users.id", "name", "product", "price")
    .left_join("orders", "users.id", "orders.user_id")
    .execute()
)

# --- UNION ---

print("\n--- UNION ---")
q1 = 'SELECT "id", "name" FROM "users" WHERE "id" = 1'
q2 = 'SELECT "id", "name" FROM "users" WHERE "id" = 2'
users.cursor.execute(f"{q1} UNION {q2}")
print(users.cursor.fetchall())

# --- Query Builder ---

print("\n--- Query Builder: простой SELECT ---")
users._select = []
users._join = []
users._where = []

print(
    users
    .select("users.id", "name")
    .execute()
)

print("\n--- Query Builder: WHERE ---")
users._select = []
users._join = []
users._where = []

print(
    users
    .select("users.id", "name", "age")
    .where('"age" > 20')
    .execute()
)

print("\n--- Query Builder: JOIN ---")
users._select = []
users._join = []
users._where = []

print(
    users
    .select("users.id", "name", "product", "price")
    .inner_join("orders", "users.id", "orders.user_id")
    .execute()
)

users.close()
orders.close()