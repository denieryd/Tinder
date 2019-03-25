from config.config_app import POINT_OF_AGE, POINT_OF_MUSIC, POINT_OF_BOOKS, \
    POINT_OF_FRIEND_UNIT, POINT_OF_GROUP_UNIT, DEBUG
from config.config_app import SERVICE_TOKEN, PATH_TO_DATA_FOR_TEST
from database import db

from typing import Dict, List

import datetime


class TinderUser:
    """
    Common user class in the application
    """

    def __init__(self, vk_client, init_obj: Dict = None, service_token: str = SERVICE_TOKEN):
        self.vk_client = vk_client
        self.service_token = service_token
        self._tinder_user_id = None

        self.first_name = None
        self.last_name = None

        self.sex = None
        self.age = None
        self.country = None
        self.city = None

        self.groups = []
        self.friends = []
        self.top3_photos = []

        self.movies = ''
        self.music = ''
        self.books = ''

        self.score = 0

        if init_obj is not None:
            self.init_tinder_user_from_obj(init_obj)

    def init_tinder_user_from_obj(self, obj: Dict) -> None:
        """
        initialize instance of Tinder User from received data of type of dict

        :param obj: Dict which includes data for initialization instance of TinderUser
        """

        self._tinder_user_id = obj['id']

        self.first_name = obj['first_name']
        self.last_name = obj.get('last_name', 'closed')

        self.country = obj.get('country', 'closed')
        self.sex = obj.get('sex', 'closed')
        self.movies = obj.get('movies', 'closed')
        self.books = obj.get('books', 'closed')
        self.music = obj.get('music', 'closed')

        self.friends = self.get_friend_list()
        self.groups = self.get_group_list()

        try:
            # if user have full birth date (like '17.12.1977') we attempt their data
            # else user have date like '28.5' or '2.11' we reject their date because we do not know how old their
            self.age = self._calculate_age(datetime.datetime.strptime(obj['bdate'], '%d.%m.%Y'))
        except (KeyError, ValueError):
            self.age = 'closed'

    def get_friend_list(self):
        """
        Send request to VK API to get groups and return result

        :return: response from VK API
        """

        params = {'user_id': self._tinder_user_id}
        return self.vk_client.send_request(method='friends.get',
                                           params_of_query=params)['response']['items']

    def get_group_list(self):
        """
        Send request to VK API to get groups and return result

        :return: response from VK API
        """

        params = {'user_id': self._tinder_user_id}
        return self.vk_client.send_request(method='users.getSubscriptions',
                                           params_of_query=params)['response']['groups']['items']

    def calculate_matching_score(self, target_user) -> None:
        """
        Calculate matching score and put it in field of instance

        :param target_user: User for who calculate the similarity
        """

        groups_score = self._get_points_of_groups(target_user.groups)
        friends_score = self._get_points_of_friends(target_user.friends)
        books_score = self._get_points_of_books(target_user.books)
        music_score = self._get_points_of_music(target_user.music)
        age_score = self._get_points_of_age(target_user.desired_age_from, target_user.desired_age_to)

        self.score = groups_score + friends_score + books_score + music_score + age_score

    def _get_points_of_groups(self, other_group_list: List) -> float:
        """
        Calculate similarity by common groups

        :param other_group_list: List of group of another user
        :return: score of similarity
        """

        return POINT_OF_GROUP_UNIT * len((set(self.groups).intersection(set(other_group_list))))

    def _get_points_of_friends(self, other_friend_list: List) -> float:
        """
        Calculate similarity by common friends

        :param other_friend_list: List of friends of another user
        :return: score of similarity
        """

        return POINT_OF_FRIEND_UNIT * len((set(self.friends).intersection(set(other_friend_list))))

    def _get_points_of_music(self, other_music: str) -> float:
        """
        Calculate similarity by common music

        :param other_music: String with music of another user
        :return: score of similarity
        """
        other_music = {word[:-2] for word in set(other_music.split())}
        other_music2 = {word[:-2] for word in set(self.music.split())}
        return POINT_OF_MUSIC * len(other_music.intersection(other_music2))

    def _get_points_of_books(self, other_books: str) -> float:
        """
        Calculate similarity by common books

        :param other_books: String with books of another user
        :return: score of similarity
        """

        other_books = {book[:-2] for book in set(other_books.split())}
        other_books2 = {other_book[:-2] for other_book in set(self.books.split())}
        return POINT_OF_BOOKS * len(other_books.intersection(other_books2))

    def _get_points_of_age(self, age_from: int, age_to: int) -> float:
        """
        Calculate similarity by age

        :param age_from: desired age from
        :param age_to: desired age to
        :return: score for age
        """

        if self.age != 'closed' and age_from <= self.age <= age_to:
            return POINT_OF_AGE
        else:
            return 0.0

    def _calculate_age(self, born):
        today = datetime.date.today()
        return today.year - born.year - ((today.month, today.day) < (born.month, born.day))

    def _get_photos_of_user(self) -> None:
        """
        Get photos of particular user by id with VK API and put they in field of instance
        """

        params = {'owner_id': self._tinder_user_id, 'album_id': 'profile', 'extended': 1}

        photos = self.vk_client.send_request(method='photos.get', params_of_query=params)['response']['items']
        photos.sort(key=lambda photo: int(photo['likes']['count']))

        size = 0
        for ph in photos[-3:]:
            self.top3_photos.append(ph['sizes'][size]['url'])

    def get_user_in_dict(self) -> Dict[str, str]:
        """
        It gives the config of the instance as a dict

        :return: Dict with configuration of instance
        """

        self._get_photos_of_user()

        return {
            'first_name': self.first_name,
            'last_name': self.last_name,
            'vk_link': f'https://vk.com/id{self._tinder_user_id}',
            'photos': self.top3_photos
        }

    @classmethod
    def get_tinder_users_for_one_round(cls, quantity: int) -> List:
        """
        It gives last "quantity" Tinder Users

        :param quantity: quantity of Tinder Users
        :return: List of Tinder users
        """

        return cls._instances_of_tinder_user[-quantity:]

    def __repr__(self):
        return f'Tinder User: name: {self.first_name}, uid: {self._tinder_user_id}'


class MainUser(TinderUser):
    """
    The main class in our application. For it, we will search for similar users, etc.
    """

    def __init__(self, vk_client, count_for_search: int = 15, debug=DEBUG):
        super().__init__(vk_client=vk_client)
        self._user_token = None

        self.screen_name = None
        self.desired_age_from = None
        self.desired_age_to = None
        self.count_for_search = count_for_search
        self.offset_for_search = 0

        self._init_main_user(debug=debug)

    def _init_main_user(self, debug) -> None:
        """
        It initializes instance of Main user
        """

        profile_info = self._get_profile_info()
        self._init_default_params(profile_info)

        db.init_user_in_last_run_state(self._tinder_user_id)
        self._set_additional_params(debug=debug)

    def get_desired_age_from_from_db(self):
        """
        get the "desired_age_from"  from the last run of the app
        """

        return db.get_last_desired_age_from(self._tinder_user_id)

    def get_desired_age_to_from_db(self) -> int:
        """
        get the "desired_age_to" from the last run of the app
        """

        return db.get_last_desired_age_to(self._tinder_user_id)

    def _set_additional_params(self, debug) -> None:
        """
        It ask desired age and put current offset to db. It use this method like additional initialization of instance
        """

        print('There are search settings save only for session')
        if debug:
            with open(PATH_TO_DATA_FOR_TEST, encoding='utf8') as f:
                f.readline()
                self.desired_age_from = f.readline()
                self.desired_age_to = f.readline()
        else:
            print('You can skip follow prompts.Then we will get values from last run ')
            self.desired_age_from = input('Give number for desired min of search age: ')
            self.desired_age_to = input('Give number for desired max of search age: ')

            if not self.desired_age_from:
                self.desired_age_from = self.get_desired_age_from_from_db()
            if not self.desired_age_to:
                self.desired_age_to = self.get_desired_age_to_from_db()

            self.desired_age_from = int(self.desired_age_from)
            self.desired_age_to = int(self.desired_age_to)

        self.offset_for_search = db.get_current_offset(self._tinder_user_id)

    def _init_default_params(self, profile_info: Dict) -> None:
        """
        This is an auxiliary method for the main method with initialization.
        Initializes additional parameters of instance

        :param profile_info: Dict with data for initialization of instance
        """

        self._tinder_user_id = profile_info['id']
        self.first_name = profile_info.get('first_name', 'first name')
        self.last_name = profile_info.get('last_name', 'last name')
        self.sex = profile_info.get('sex', 'unknown gender')
        self.city = '' if 'city' not in profile_info else profile_info['city']['id']
        self.movies = profile_info.get('movies', '')
        self.music = profile_info.get('music', '')
        self.books = profile_info.get('books', '')
        self.age = self._calculate_age(datetime.datetime.strptime(profile_info['bdate'], '%d.%m.%Y'))

        self.friends = self.get_friend_list()
        self.groups = self.get_group_list()

    def _get_profile_info(self) -> Dict:
        """
        Get additional info about instance

        :return: Dict from VK API with additional info of instance
        """

        params_of_request = {'fields': 'sex,bdate,city,country,activities,interests,music,movies,books'}

        items_of_request = 0

        return self.vk_client.send_request(method='users.get',
                                           params_of_query=params_of_request)['response'][items_of_request]

    def update_search_offset(self) -> None:
        """
        Update current offset for search in database
        """

        db.update_current_offset(self.offset_for_search, self._tinder_user_id)

    def get_search_config_obj(self) -> Dict:
        """
        It gives config of instance
        """

        return {'vk_id': self._tinder_user_id,
                'count_for_search': self.count_for_search,
                'sex': self.sex,
                'city': self.city,
                'desired_age_from': self.desired_age_from,
                'desired_age_to': self.desired_age_to,
                'offset_for_search': self.offset_for_search}

    def __repr__(self):
        return f'MainUser: name {self.first_name}'
