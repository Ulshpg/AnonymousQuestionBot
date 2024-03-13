import aiosqlite, asyncio

# Функция для создания базы данных
async def create_database():
    async with aiosqlite.connect('user_database.db') as db:
        cursor = await db.cursor()
        await cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            ID INTEGER UNIQUE,
            NAME TEXT,
            USERNAME TEXT
        )
        ''')
        await db.commit()

# Функция для вставки данных по ID во второй и третий столбцы
async def insert_data(id, name, username):
    async with aiosqlite.connect('user_database.db') as db:
        cursor = await db.cursor()
        await cursor.execute('''
        REPLACE INTO users (ID, NAME, USERNAME)
        VALUES (?, ?, ?)
        ''', (id, name, username))
        await db.commit()

# Функция для получения данных по ID
async def get_data(id):
    async with aiosqlite.connect('user_database.db') as db:
        cursor = await db.cursor()
        await cursor.execute('SELECT NAME, USERNAME FROM users WHERE ID = ?', (id,))
        result = await cursor.fetchone()
    return result

async def get_username_by_id(user_id):
    async with aiosqlite.connect("user_database.db") as db:
        cursor = await db.cursor()
        await cursor.execute("SELECT USERNAME FROM users WHERE ID = ?", (user_id,))
        username = await cursor.fetchone()
        if username:
            return username[0]  # Возвращает значение USERNAME
        else:
            return "Отсутствует"  # Если пользователь с указанным ID не найден, возвращает None

async def get_all_vips():
    async with aiosqlite.connect('user_database.db') as db:
        cursor = await db.cursor()
        await cursor.execute('SELECT ID FROM vip')
        ids = [row[0] for row in await cursor.fetchall()]
    return ids

async def add_vip(id):
    async with aiosqlite.connect('user_database.db') as db:
        cursor = await db.cursor()
        await cursor.execute('REPLACE INTO vip (ID) VALUES (?)', (id,))
        await db.commit()
    return await get_all_vips()

# async def get_all_id():
#     async with aiosqlite.connect('user_database.db') as db:
#         cursor = await db.cursor()
#         await cursor.execute('SELECT ID FROM users')
#         ids = [row[0] for row in await cursor.fetchall()]
#     return ids

# async def update_table_to_zero():
#     async with aiosqlite.connect('user_database.db') as db:
#         cursor = await db.cursor()
#         await cursor.execute(f'UPDATE users SET INP = 0, OUTP = 0')
#         await db.commit()

# async def get_value_count(column: str, user_id):
#     async with aiosqlite.connect("user_database.db") as db:
#         cursor = await db.cursor()
#         await cursor.execute(f"SELECT {column} FROM users WHERE ID = ?", (user_id,))
#         current_value = await cursor.fetchone()
#         return current_value[0]

# async def changing_count_messages(column, user_id):
#     async with aiosqlite.connect("user_database.db") as db:
#         cursor = await db.cursor()
#         current_value = await get_value_count(column, user_id)
#         if current_value:
#             new_value = current_value + 1
#             await cursor.execute(f'UPDATE users SET {column} = ? WHERE ID = ?', (new_value, user_id))
#             await db.commit()

# print(asyncio.run(changing_count_messages("OUTP", 6504205024)))