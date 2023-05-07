import mysql.connector
import json
import logging

logging.basicConfig(filename='app.log', level=logging.INFO)

class TT_Bot_Db_Manager:
    def __init__(self, host, user, password, database):
        self._connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )

    # получить первых 1000 пользователей с БД
    def get_records(self):
        try:
            cursor = self._connection.cursor(dictionary=True)
            query = "SELECT * FROM TestTable LIMIT 1000"
            cursor.execute(query)
            result = cursor.fetchall()
            cursor.close()
            return result
        except mysql.connector.Error as error:
            print(f"Ошибка выполнения запроса к БД: {error}")
            logging.error(f'Ошибка при отправке сообщения: {error}')
            return []
    
    # добавить новых пользователей в БД
    def add_records_from_json_file(self, file):
        # читаем данные из файла
        try:
            records = json.load(file)
        except json.JSONDecodeError:
            logging.error('Не удалось прочитать файл')
            return "Не удалось прочитать файл"
        except FileNotFoundError:
            logging.error('Файл не найден')
            return "Файл не найден"

        # создаём запрос на добавление
        query2 = []
        query2.append("INSERT INTO TestTable (IdTgUser) VALUES ")

        # добавляем значения VALUES чтобы добавить пользователей одним запросом
        for record in records:
            query2.append(f"({record['IdTgUser']}),\n")

        # для последнего VALUES меняем знак , на ; чтобы не было ошибки в запросе
        query2[-1] = query2[-1].replace(',', ';')

        cursor = self._connection.cursor()
        try:
            cursor.execute(''.join(query2))
            self._connection.commit()
        except mysql.connector.Error as error:
            print(f"Ошибка вставки записей в таблицу: TestTable {error}")
            logging.error(f"Ошибка вставки записей в таблицу: TestTable {error}")
            self._connection.rollback()
            return "Не удалось добавить пользователей в БД"
        
        cursor.close()
        return "Пользователи успешно добавлены"
