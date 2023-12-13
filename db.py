from peewee import *


class BotDB:

    def __init__(self, db_file):
        self.conn = SqliteDatabase(db_file)
        self.cursor = self.conn.cursor()

    def add_user(self, user_id, user_name, size, choose, link, city):
        self.cursor.execute('INSERT INTO `user` (`tg_id`, `name`, `size`, `choose`, `link`, `city`)'
                            ' VALUES (?, ?, ?, ?, ?, ?)', (user_id, user_name, size, choose, link, city))

        return self.conn.commit()

    def get_tob(self, tob, user_id):
        self.cursor.execute('UPDATE `user` SET type_of_buy=(?) WHERE tg_id=(?)', (tob, user_id))
        return self.conn.commit()

    def get_photo(self, file_id, user_id):
        self.cursor.execute('INSERT INTO `photo` (`user_id`, `photo`) VALUES (?, ?)', (user_id, file_id))
        return self.conn.commit()

    def select_size(self, size, user_id):
        self.cursor.execute('UPDATE `user` SET size=(?) WHERE tg_id=(?)', (size, user_id))
        return self.conn.commit()

    def add_match(self, seller_id, buyer_id):
        self.cursor.execute('INSERT INTO `match` (`tg_id_buy`, `tg_id_sell`) VALUES (?, ?)',
                            (buyer_id, seller_id))
        return self.conn.commit()

    def check_match_buy(self, buyer_id, seller_id):
        sql_info = """SELECT * FROM match WHERE `tg_id_buy`=? AND `tg_id_sell`=?"""
        data = self.cursor.execute(sql_info, (buyer_id, seller_id, ))
        info = data.fetchone()
        if info is None:
            return False
        else:
            return True

    def cancel_choise(self, user_id):
        sql_delete_choise = """DELETE from `user` WHERE `tg_id` = ?"""
        self.cursor.execute(sql_delete_choise, (user_id, ))
        return self.conn.commit()

    def cancel_photos(self, user_id):
        sql_delete_choise = """DELETE from `photo` WHERE `user_id` = ?"""
        self.cursor.execute(sql_delete_choise, (user_id,))
        return self.conn.commit()

    def cancel_match_buy(self, user_id):
        sql_delete_choise = """DELETE from `match` WHERE `tg_id_buy` = ?"""
        self.cursor.execute(sql_delete_choise, (user_id, ))
        return self.conn.commit()

    def get_status(self, user_id):
        sql_info = """SELECT * FROM user WHERE tg_id=?"""
        data = self.cursor.execute(sql_info, (user_id,))
        info = data.fetchall()
        local_status = None
        for i in info:
            local_status = i[3]
        return local_status

    def get_size(self, user_id):
        sql_info = """SELECT * FROM user WHERE tg_id=?"""
        data = self.cursor.execute(sql_info, (user_id,))
        info = data.fetchall()
        local_size = None
        for i in info:
            local_size = i[2]
        return local_size

    def get_link(self, user_id):
        sql_info = """SELECT * FROM user WHERE tg_id=?"""
        data = self.cursor.execute(sql_info, (user_id,))
        info = data.fetchall()
        local_link = None
        for i in info:
            local_link = i[4]
        return local_link

    def get_info(self, user_id):
        sql_info = """SELECT * FROM user WHERE tg_id=?"""
        data = self.cursor.execute(sql_info, (user_id, ))
        info = data.fetchall()
        local_name = None
        local_size = None
        local_status = None
        local_link = None
        local_city = None
        local_tob = None
        local_namesh = None
        for i in info:
            local_name = i[1]
            local_size = i[2]
            local_status = i[3]
            local_link = i[4]
            local_city = i[5]
            local_tob = i[6]
            local_namesh = i[7]
        if local_status == 'Продавец':
            ancet = f'Имя: {local_name}\nНазвание обуви: {local_namesh}\n' \
                    f'Размер обуви: {local_size}\nГород: {local_city}\n{local_status}\n' \
                    f'{local_tob}\nНаписать: {local_link}'
            return ancet
        else:
            ancet = f'Имя: {local_name}\nРазмер обуви: {local_size}\nГород: {local_city}\n{local_status}\n' \
                    f'{local_tob}\nНаписать: {local_link}'
            return ancet

    def get_info_global(self, user_id):
        sql_info = """SELECT * FROM user WHERE tg_id=?"""
        data = self.cursor.execute(sql_info, (user_id,))
        info = data.fetchall()
        local_name = None
        local_size = None
        local_status = None
        local_city = None
        local_tob = None
        local_namesh = None
        for i in info:
            local_name = i[1]
            local_size = i[2]
            local_status = i[3]
            local_city = i[5]
            local_tob = i[6]
            local_namesh = i[7]
        if local_status == 'Продавец':
            ancet = f'Имя: {local_name}\nНазвание обуви: {local_namesh}\n' \
                    f'Размер обуви: {local_size}\nГород: {local_city}\n' \
                    f'{local_status}\n{local_tob}.'
            return ancet
        else:
            ancet = f'Имя: {local_name}\nРазмер обуви: {local_size}\nГород: {local_city}\n' \
                    f'{local_status}\n{local_tob}.'
            return ancet

    def check_photo(self, user_id):
        sql_info = """SELECT * FROM photo WHERE user_id=?"""
        data = self.cursor.execute(sql_info, (user_id, ))
        info = data.fetchall()
        l_of_photos = []
        for i in info:
            l_of_photos.append(i[1])
        return l_of_photos

    def get_namesh(self, namesh, user_id):
        self.cursor.execute('UPDATE `user` SET shoes=(?) WHERE tg_id=(?)', (namesh, user_id))
        return self.conn.commit()

    def number_photo(self, user_id):
        sql_info = """SELECT * FROM photo WHERE user_id=?"""
        data = self.cursor.execute(sql_info, (user_id,))
        info = data.fetchall()
        l_of_photos_mas = []
        for i in info:
            l_of_photos_mas.append(i[1])
        l_of_photos = len(l_of_photos_mas)
        return l_of_photos

    def count_sellers(self, size):
        sql_id = """SELECT `tg_id` FROM user WHERE (choose='Продавец' and size=?)"""
        tg_id_data = self.cursor.execute(sql_id, (size, ))
        tg_id_info = tg_id_data.fetchall()
        tg_id_list = []
        for i in tg_id_info:
            tg_id_list.append(*i)
        return tg_id_list

    def close(self):
        self.conn.close()
