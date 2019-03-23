from vk.vk_machinery import VkMachinery
from tinder_users import TinderUser, MainUser
from config.config_app import BASE_DIR

import unittest
import os

os.chdir(BASE_DIR)
VkMachinery.initialize_vk_api(debug=True)


class TestVkMachinery(unittest.TestCase):
    def setUp(self):
        self.config = {'count_for_search': 0,
                       'sex': 0,
                       'city': 0,
                       'desired_age_from': 0,
                       'desired_age_to': 0,
                       'offset_for_search': 0}

    def test_search_user(self):
        try:
            main_user = MainUser(debug=True)
            main_user_config = main_user.get_search_config_obj()

            res = VkMachinery.users_search(main_user_config)

            self.assertEqual(type(res), type(list()), 'Result must have a type like list')
        except BaseException:
            self.fail("vk_machinery.users_search() raised ExceptionType unexpectedly!")

    def test_arguments_in_get_processed_data_of_tinder_users(self):
        with self.assertRaises(TypeError):
            VkMachinery.get_processed_data_of_tinder_users(1)
            VkMachinery.get_processed_data_of_tinder_users(None)

        try:
            VkMachinery.get_processed_data_of_tinder_users([{'is_closed': True}])
        except TypeError:
            self.fail("vk_machinery.get_processed_data_of_tinder_users() raised TypeError unexpectedly!")


class TestTinderUser(unittest.TestCase):
    def test_init_tinder_user(self):
        with self.assertRaises(TypeError):
            TinderUser([])
            TinderUser('')
            TinderUser(5)
            TinderUser(None)
        try:
            TinderUser()
        except BaseException:
            self.fail("Create TinderUser() raised anyException unexpectedly!")


if __name__ == '__main__':
    unittest.main()
