import sqlite3

# Устанавливаем соединение с базой данных
connection = sqlite3.connect('tasks.db')
cursor = connection.cursor()

# Создаем таблицу Users
cursor.execute('''
CREATE TABLE IF NOT EXISTS Notes (
id INTEGER PRIMARY KEY,
username TEXT NOT NULL,
text TEXT NOT NULL,
timestamp TEXT NOT NULL,
is_done TEXT NOT NULL)
''')

# Сохраняем изменения и закрываем соединение
connection.commit()
connection.close()