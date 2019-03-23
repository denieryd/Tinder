from config.config_app import SERVICE_TOKEN, VERSION_VK_API, PATH_TO_DATA_FOR_TEST, OAUTH_LINK
from utils import reg_exp_pattern_access_token, StrOrInt, retry_on_error, RetryException
from typing import Dict, List, Union

import re
import requests
import time


class VkMachinery:
    _version_vk_api = VERSION_VK_API
    _access_token_of_user = None

    @classmethod
    def initialize_vk_api(cls, debug):
        access_token = cls._get_access_token(debug=debug)
        VkMachinery._access_token_of_user = access_token

    @classmethod
    def _get_access_token(cls, debug) -> Union[str, bytes]:
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

    @classmethod
    def _get_updated_params(cls, params: Dict[str, str]) -> Dict[str, str]:
        require_params = {'v': cls._version_vk_api,
                          'access_token': cls._access_token_of_user}
        if params is None:
            return require_params
        else:
            params.update(require_params)
            return params

    @classmethod
    @retry_on_error(5)
    def send_request(cls, method: str, params_of_query: Dict[str, str] = None):
        """
        Send request to the VK API and return a result

        :param str method: Any method from VK API
        :param dict params_of_query: additional params for request
        :return: result of requests.get(...).json()
        """
        params_of_query = cls._get_updated_params(params_of_query)

        req = requests.get(f'https://api.vk.com/method/{method}', params=params_of_query).json()
        if 'error' in req and req['error']['error_code'] == 6:
            # Error 6 is to many request.There is can be more errors
            time.sleep(0.5)
            raise RetryException
        return req

    @classmethod
    def users_search(cls, config: Dict[str, StrOrInt]) -> List[Dict]:
        """
        Send request user.search to VK API and return its result

        :param config: config which use for search similar people
        :return: List of dict of data similar people
        """

        params_of_request = {'count': config['count_for_search'],
                             'fields': f'sex={(config["sex"] % 2) + 1},city={config["city"]},'
                             f'age_from={config["desired_age_from"]},age_to={config["desired_age_to"]}',
                             'offset': config['offset_for_search']}

        params_of_request = cls._get_updated_params(params_of_request)
        print('Waiting please.. We are searching')

        req = cls.send_request(method='users.search', params_of_query=params_of_request)
        return req['response']['items']

    @classmethod
    def get_processed_data_of_tinder_users(cls, searched_users: List[Dict]) -> List[Dict]:
        """
        Get List of Tinder users and return it processed

        :param List searched_users: List of dict of data
        :return: List of dict of extended data for future initialization
         Tinder Users. Closed profiles will be dropped.
        """

        opened_tinder_user_ids = []

        for searched_user in searched_users:
            if searched_user['is_closed'] is False:
                opened_tinder_user_ids.append(str(searched_user['id']))

        get_users_param = {
            'access_token': SERVICE_TOKEN,
            'v': VERSION_VK_API,
            'user_ids': ','.join(opened_tinder_user_ids),
            'fields': 'sex,bdate,city,country,activities,interests,music,movies,books'
        }

        data_of_tinder_users = cls.send_request('users.get', params_of_query=get_users_param)['response']
        return data_of_tinder_users
