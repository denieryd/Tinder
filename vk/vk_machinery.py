from config.config_app import VERSION_VK_API, PATH_TO_DATA_FOR_TEST, OAUTH_LINK
from utils import reg_exp_pattern_access_token, StrOrInt, retry_on_error, RetryException, VkException
from typing import Dict, List, Union
from datetime import datetime

import re
import requests
import time


class VkMachinery:
    _version_vk_api = VERSION_VK_API

    def __init__(self):
        self._access_token_of_user = None

    def initialize_vk_api(self, debug=False):
        access_token = self._get_access_token(debug=debug)
        self._access_token_of_user = access_token

    def _get_access_token(self, debug) -> Union[str, bytes]:
        """
        It get users's token and put it in field of instance
        """

        if debug:
            with open(PATH_TO_DATA_FOR_TEST, encoding='utf8') as f:
                link_after_oauth = f.readline()
        else:
            link_after_oauth = input(f'1.Follow this link: {OAUTH_LINK}\n'
                                     '2.Confirm the intentions\n'
                                     '3.Copy the address of the browser string and paste it here, please: ')

        return re.match(reg_exp_pattern_access_token, link_after_oauth).group('user_token').strip()

    def _get_updated_params(self, params: Dict[str, str]) -> Dict[str, str]:
        require_params = {'v': self._version_vk_api,
                          'access_token': self._access_token_of_user}
        if params is None:
            return require_params
        else:
            params.update(require_params)
            return params

    @retry_on_error(4)
    def send_request(self, method: str, params_of_query: Dict[str, str] = None):
        """
        Send request to the VK API and return a result

        :param str method: Any method from VK API
        :param dict params_of_query: additional params for request
        :return: result of requests.get(...).json()
        """
        params_of_query = self._get_updated_params(params=params_of_query)

        req = requests.get(f'https://api.vk.com/method/{method}', params=params_of_query).json()
        if 'error' in req and req['error']['error_code'] == 6:
            # Error 6 is to many request.There is can be more errors
            time.sleep(0.2)
            raise RetryException
        elif 'error' in req:
            raise VkException(req['error']['error_msg'])
        return req

    def users_search(self, config: Dict[str, StrOrInt]) -> List[Dict]:
        """
        Send request user.search to VK API and return its result

        :param config: config which use for search similar people
        :return: List of dict of data similar people
        """

        params_of_request = {'count': config['count_for_search'],
                             'fields': f'sex={(config["sex"] % 2) + 1},city={config["city"]},'
                             f'age_from={config["desired_age_from"]},age_to={config["desired_age_to"]}',
                             'offset': config['offset_for_search']}

        params_of_request = self._get_updated_params(params=params_of_request)
        print('Waiting please.. We are searching')

        req = self.send_request(method='users.search', params_of_query=params_of_request)
        return req['response']['items']

    def _more_process(self, data_of_tinder_users, main_user_config):
        age_from = main_user_config['desired_age_from']
        age_to = main_user_config['desired_age_to']

        users = []
        for tinder_user in data_of_tinder_users:
            if 'bdate' not in tinder_user:
                continue
            if len((tinder_user['bdate']).split('.')) != 3:
                continue
            days, months, years = tinder_user['bdate'].split('.')

            if age_from <= datetime.now().year - int(years) <= age_to:
                users.append(tinder_user)

        return users

    def get_processed_data_of_tinder_users(self, searched_users: List[Dict], main_user_config: Dict) -> List[Dict]:
        """
        Get List of Tinder users and return it processed

        :param List searched_users: List of dict of data
        :param main_user_config: Config of Main User
        :return: List of dict of extended data for future initialization
         Tinder Users. Closed profiles will be dropped.
        """

        opened_tinder_user_ids = []

        for searched_user in searched_users:
            if searched_user['is_closed'] is False:
                opened_tinder_user_ids.append(str(searched_user['id']))

        get_users_param = {
            'user_ids': ','.join(opened_tinder_user_ids),
            'fields': 'sex,bdate,city,country,activities,interests,music,movies,books'
        }

        data_of_tinder_users = self.send_request('users.get', params_of_query=get_users_param)['response']
        data_of_tinder_users = self._more_process(data_of_tinder_users, main_user_config)
        return data_of_tinder_users
