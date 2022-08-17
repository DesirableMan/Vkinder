import sqlalchemy as sq
from vk_api.exceptions import ApiError
from keys import group_token, user_token, DSN, V
import sqlalchemy.exc
from Base_db import User, Photo, Vkinder, Message, create_db
import random
import vk_api





def dump_it(session_maker, new_user, photo):
    res = False
    if session_maker:
        session = session_maker()
        session.add(new_user)
        for p in photo:
            session.add(p)
            session.commit()
            res = True
    return res




def make_sex(sex):
    if sex != 0:
        sex = 3 - sex
    return sex


def make_birth_year(user, message):
    if 'bdate' not in user.keys():
        birth_year = None
        while not (isinstance(birth_year, int) and 1900 < birth_year < 2021):
            birth_year = int(message.read('Какой год рождения?'))
    elif len(user['bdate'].split('.')) != 3:
        birth_year = None
        while not (isinstance(birth_year, int) and 1900 < birth_year < 2021):
            birth_year = int(message.read('Какой год рождения?'))
    else:
        birth_year = user['bdate'].split('.')[-1]

    return int(birth_year) + random.randrange(-10, 5)



def make_search(vki, user, message):
    sex = make_sex(user['sex'])
    birth_year = make_birth_year(user, message)
    city = 10

    search_params = {'sort': 1,
                     'is_closed': False,
                     'has_photo': 1,
                     'sex': sex,
                     'birth_year': birth_year,
                     'city': city,
                     'status': 6}


    res = vki.search(search_params)

    return res




def check_user(user):
    if user['is_closed']:
        return False
    param_list = ['id', 'first_name', 'last_name', 'sex', 'bdate', 'city']
    for field in param_list:
        if field not in user.keys():
            return False
    return True


def best_size(sizes_list):
    type_ = ['s', 'm', 'x', 'o', 'p', 'q', 'r', 'y', 'z', 'w']
    size_ = range(1, len(type_) + 1)
    sizes_rating = dict(zip(type_, size_))
    top_size = sorted(sizes_list, key=(lambda item: sizes_rating[item['type']]), reverse=True)[0]
    return top_size



def get_photo(user_owner_id):
    vk_ = vk_api.VkApi(token=user_token)
    try:
        response = vk_.method('photos.get',
                              {
                                  'access_token': user_token,
                                  'v': V,
                                  'owner_id': user_owner_id,
                                  'album_id': 'profile',
                                  'count': 10,
                                  'extended': 1,
                                  'photo_sizes': 1,
                              })
    except ApiError:
        return 'нет доступа к фото'
    users_photos = []
    for i in range(10):
        try:
            users_photos.append(
                [response['items'][i]['likes']['count'],
                 'photo' + str(response['items'][i]['owner_id']) + '_' + str(response['items'][i]['id'])])
        except IndexError:
            users_photos.append(['нет фото.'])
    return users_photos





def get_best_prof_photos(vki, id_):
    req = vki.get_photos(id_)
    top_3_links = None
    if 'items' in req.keys():
        res = vki.get_photos(id_)['items']
        res.sort(key=lambda item: item['likes']['count'], reverse=True)
        top_3 = res[0: min(3, len(res))]
        top_3_links = [best_size(item['sizes'])['url'] for item in top_3]


    return top_3_links




def search_result(id_, vki):
    raw_user = vki.get_user_info(id_)[0]
    if check_user(raw_user):
        new_user = User(user_id=raw_user['id'],
                        first_name=raw_user['first_name'],
                        last_name=raw_user['last_name'],
                        sex=raw_user['sex'],
                        bdate=raw_user['bdate'],
                        city=raw_user['city']['title'])

        photo = [Photo(user_id=new_user.user_id, url=one_url) for one_url in
                 get_best_prof_photos(vki, new_user.user_id)]



        return {'user': new_user, 'photo': photo}
    else:
        return False


def start_vkinder(vki, session_maker):
    x = vki.read_msg()
    new_client = x.user_id
    message = Message(vki, new_client)

    resp = vki.get_user_info(new_client)

    user = resp[0]
    message.write(f"Привет, {user['first_name']}, добро пожаловать в сервис знакомств. Давай найдем для тебя пару.")
    res = make_search(vki, user, message)
    dump_list = []
    for r in res:
        if session_maker:
            already_in_db = session_maker().query(User).filter(User.user_id == r['id']).first()
        else:
            already_in_db = False

        if not already_in_db:
            new_id = search_result(r['id'], vki)
            if not new_id:
                continue
            else:
                message.write(f"Посмотри кого я тебе нашел - {new_id['user']}")
                [message.write(item) for item in new_id['photo']]

                dump_it(session_maker, new_id['user'], new_id['photo'])

                message.write(f"Чтобы продолжить поиски - напиши 'еще', чтобы выйти - напиши 'выход'")
                q = message.read()
                if q == 'выход':
                    message.write(f"До скорой встречи. Заходи еще")
                    break




if __name__ == '__main__':
    try:
        Session = create_db(DSN)
    except sq.exc.OperationalError as error_msg:
        print(error_msg)
        Session = False


    vkinder = Vkinder(token=user_token, group_token=group_token)
    start_vkinder(vkinder, Session)