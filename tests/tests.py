import os

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vk.vk_machinery import VkMachinery
from tinder_users import TinderUser, MainUser

import unittest

vk_client = VkMachinery()
vk_client.initialize_vk_api(debug=True)

main_user_config = {'count_for_search': 0,
                    'sex': 0,
                    'city': 0,
                    'desired_age_from': 0,
                    'desired_age_to': 0,
                    'offset_for_search': 0}


class Testvk_client(unittest.TestCase):
    def test_search_user(self):
        try:
            main_user = MainUser(vk_client=vk_client, debug=True)
            main_user_config = main_user.get_search_config_obj()

            main_user_config['desired_age_from'] = main_user_config['desired_age_from'].strip()
            main_user_config['desired_age_to'] = main_user_config['desired_age_to'].strip()

            res = vk_client.users_search(main_user_config)
            self.assertEqual(type(res), type(list()), 'Result must have a type like list')
        except BaseException:
            self.fail("vk_machinery.users_search() raised ExceptionType unexpectedly!")

    def test_arguments_in_get_processed_data_of_tinder_users(self):
        with self.assertRaises(TypeError):
            vk_client.get_processed_data_of_tinder_users(1, main_user_config=main_user_config)
            vk_client.get_processed_data_of_tinder_users(None, main_user_config=main_user_config)

        try:
            vk_client.get_processed_data_of_tinder_users([{'is_closed': True}], main_user_config=main_user_config)
        except TypeError:
            self.fail("vk_machinery.get_processed_data_of_tinder_users() raised TypeError unexpectedly!")


class TestTinderUser(unittest.TestCase):
    def test_init_tinder_user(self):
        try:
            TinderUser(vk_client=vk_client)
            TinderUser(vk_client=vk_client, init_obj=None)

        except BaseException:
            self.fail("Create TinderUser() raised anyException unexpectedly!")


if __name__ == '__main__':
    unittest.main()
