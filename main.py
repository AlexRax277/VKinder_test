from random import randrange
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import datetime
import sqlite3
from operator import itemgetter


token_group = ''
token_user = ''
vk_group = vk_api.VkApi(token=token_group)
vk_user = vk_api.VkApi(token=token_user)
longpoll = VkLongPoll(vk_group)


class VkUser:
    def __init__(self, user_id):
        self.user_id = user_id

    def user_info(self):
        user_info = vk_group.method("users.get", {"user_ids": self.user_id,
                                                  "fields": 'sex, bdate, city, relation'})
        return user_info

    def get_name(self):
        first_name = self.user_info()[0]['first_name']
        return first_name

    def get_age(self):
        if 'bdate' in self.user_info()[0].keys():
            bdate = self.user_info()[0]['bdate']
            list_bdate = bdate.split('.')
            if len(list_bdate) == 3:
                age = datetime.date.today().year - int(list_bdate[2])
                return age, True
            else:
                return 'Возраст неизвестен!', False
        else:
            return 'Возраст неизвестен!', False

    def get_sex(self):
        sex = self.user_info()[0]['sex']
        return sex

    def get_city(self):
        if 'city' in self.user_info()[0].keys():
            city = self.user_info()[0]['city']['id']
            return city, True
        else:
            return 'Город неизвестен!', False

    def get_relation(self):
        if 'relation' in self.user_info()[0].keys():
            relation = self.user_info()[0]['relation']
            return relation, True
        else:
            return 'Семейное положение скрыто!', False

    @staticmethod
    def write_msg(user_id, message):
        vk_group.method('messages.send', {'user_id': user_id, 'message': message, 'random_id': randrange(10 ** 7), })

    def parameters_fot_users_search(self, my_age, my_city, my_relation):
        parameters_dict = {'sort': 0, 'count': 20, 'fields': 'photo_id, photo_max_orig', 'country': 1, 'has_photo': 1}
        if VkUser.get_sex(self) == 1:
            parameters_dict['sex'] = 2
        else:
            parameters_dict['sex'] = 1
        if VkUser.get_city(self)[1]:
            parameters_dict['city'] = VkUser.get_city(self)[0]
        else:
            parameters_dict['hometown'] = my_city
        if VkUser.get_relation(self)[1]:
            parameters_dict['status'] = VkUser.get_relation(self)[0]
        else:
            parameters_dict['status'] = my_relation
        if VkUser.get_age(self)[1]:
            parameters_dict['age_from'] = str(VkUser.get_age(self)[0])
            parameters_dict['age_to'] = parameters_dict['age_from']
        else:
            parameters_dict['age_from'] = my_age
            parameters_dict['age_to'] = parameters_dict['age_from']
        return parameters_dict

    @staticmethod
    def search_candidates(parameters_dict):
        my_list = vk_user.method('users.search', parameters_dict)
        return my_list

    @staticmethod
    def create_list_candidates(my_list):
        list_candidates = []
        for candidate in my_list['items']:
            while len(list_candidates) <= 2:
                if not candidate['is_closed']:
                    list_candidates.append(candidate)
                break
        return list_candidates

    @staticmethod
    def parameters_for_candidates_get_photos():
        parameters_dict = {'album_id': 'profile', 'extended': 1, 'photo_sizes': 1, 'count': 100}
        return parameters_dict

    @staticmethod
    def get_candidates_photos(list_candidates):
        list_photos_candidates = []
        for candidate in list_candidates:
            parameters_dict = VkUser.parameters_for_candidates_get_photos()
            parameters_dict['owner_id'] = candidate['id']
            photos_candidate = vk_user.method('photos.get', parameters_dict)
            list_data_photo = []
            for data in photos_candidate['items']:
                data_photo = {'photo_max': data['sizes'][-1]['url'], 'likes': data['likes']['count'],
                              'comments': data['comments']['count']}
                list_data_photo.append(data_photo)
            sorted_photo = sorted(list_data_photo, key=itemgetter('likes'))[-4:]
            if int(sorted_photo[0]['likes']) == int(sorted_photo[1]['likes']):
                if int(sorted_photo[0]['comments']) > int(sorted_photo[1]['comments']):
                    sorted_photo.pop(1)
                else:
                    sorted_photo.pop(0)
            else:
                sorted_photo.pop(0)
            candidate_photos_dict = {'id': candidate['id'], 'photo': sorted_photo}
            list_photos_candidates.append(candidate_photos_dict)
        return list_photos_candidates


def create_db(list_photos_candidates, user_id):
    for candidate in list_photos_candidates:
        link = 'https://vk.com/id' + str(candidate['id'])
        album_photo = candidate['photo']
        for photo in album_photo:
            photo = photo['photo_max']
            with sqlite3.connect(f'D:\Учеба в IT\Py_advanced\Diplom_VKinder\VKinder\database-{user_id}.db') as db:
                cursor = db.cursor()
                table_links = """CREATE TABLE IF NOT EXISTS table_links(id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                                link TEXT)"""
                table_photo = """CREATE TABLE IF NOT EXISTS table_photo(link_id TEXT, photo TEXT, 
                                                                FOREIGN KEY (link_id) REFERENCES table_links(id))"""
                cursor.execute(table_links)
                cursor.execute(f"""SELECT link FROM table_links WHERE link = '{link}'""")
                if cursor.fetchone() is None:
                    cursor.execute("""INSERT INTO table_links(link) VALUES(?) """, (link,))
                else:
                    print(f"Человек с таким id: {candidate['id']} уже есть в таблице1")
                cursor.execute(f"""SELECT id FROM table_links WHERE link = '{link}'""")
                link_id = cursor.fetchone()[0]
                cursor.execute(table_photo)
                cursor.execute(f"""INSERT INTO table_photo(link_id, photo) VALUES('{link_id}', '{photo}')""")
                db.commit()
    return "Процесс завершен!"


def start_bot():
    while True:
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                request = event.text
                user = VkUser(event.user_id)
                if request == "привет":
                    user.write_msg(event.user_id, f"Хай, {user.get_name()}!\nСейчас подберем тебе пару)\nСекундочку...")
                    if not user.get_age()[1]:
                        user.write_msg(event.user_id, "Введите возраст:")
                        for my_event in longpoll.listen():
                            if my_event.type == VkEventType.MESSAGE_NEW:
                                if my_event.to_me:
                                    age = my_event.text
                                    break
                    else:
                        age = user.get_age()[0]
                    if not user.get_city()[1]:
                        user.write_msg(event.user_id, "Введите город:")
                        for my_event in longpoll.listen():
                            if my_event.type == VkEventType.MESSAGE_NEW:
                                if my_event.to_me:
                                    city = my_event.text
                                    break
                    else:
                        city = user.get_city()[0]
                    if not user.get_relation()[1]:
                        user.write_msg(event.user_id, "Введите номер категории СП"
                                                      "(1 — не женат (не замужем),"
                                                      " 5 — всё сложно,"
                                                      " 6 — в активном поиске):")
                        for my_event in longpoll.listen():
                            if my_event.type == VkEventType.MESSAGE_NEW:
                                if my_event.to_me:
                                    relation = my_event.text
                                    break
                    else:
                        relation = user.get_relation()[0]
                    parameters_for_searching = user.parameters_fot_users_search(age, city, relation)
                    result_for_searching = user.search_candidates(parameters_for_searching)
                    result_top_3 = user.create_list_candidates(result_for_searching)
                    list_photos_result_top_3 = user.get_candidates_photos(result_top_3)
                    db = create_db(list_photos_result_top_3, event.user_id)
                    user.write_msg(event.user_id, f"Так! Ну смотри, вот что мы нашли\n")
                    for i in list_photos_result_top_3:
                        user.write_msg(event.user_id, f"Кандидат : https://vk.com/id{i['id']}\n")
                        for x in i['photo']:
                            user.write_msg(event.user_id, f"Фото: {x['photo_max']}")
                elif request == "пока":
                    user.write_msg(event.user_id, "Пока((")
                else:
                    user.write_msg(event.user_id, "Не поняла вашего ответа...")


if __name__ == '__main__':
    start_bot()
