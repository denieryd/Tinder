from vk.vk_machinery import VkMachinery
from tinder_users import TinderUser, MainUser
from config.config_app import PATH_TO_OUTPUT_RESULT, DEBUG
from database.db import create_db
from database.db import insert_result_to_db, add_to_black_list, add_to_favorite_list

from pprint import pprint
from typing import Dict, List

import json


def tact_of_app(main_user) -> List[Dict]:
    """
    Do one round of the Tinder app.

    :param main_user: Instance of class MainUser(TinderUser)
    """

    list_tinder_users = []

    for tinder_user in TinderUser.get_tinder_users_for_one_round(main_user.count_for_search):
        tinder_user.calculate_matching_score(main_user)
        list_tinder_users.append(tinder_user)

    list_tinder_users.sort(key=lambda usr: usr.score)

    top10_tinder_users = list_tinder_users[-11:]

    # that problem is on the vk side
    # top10.pop(-1)  # we found our self when use vk method users.search

    result_of_matching = []
    for tinder_user in top10_tinder_users:
        result_of_matching.append(tinder_user.get_user_in_dict())

    insert_result_to_db(result_of_matching)
    return result_of_matching


def output_tinder_users(data_of_top10_matching: List[Dict]) -> None:
    """
    Output data of matched Tinder Users to stdout (Name, Photos, ...)

    :param data_of_top10_matching: List of data of Tinder Users
    """

    for ind, data_of_user in enumerate(data_of_top10_matching):
        photos = ''

        for i, ph_link in enumerate(data_of_user['photos']):
            photos = photos + 'photos: {},'.format(ph_link)

        print(f'{ind + 1}.{data_of_user["first_name"]} {data_of_user["last_name"]}, '
              f'vk:{data_of_user["vk_link"]}, {photos}')


def interface_for_black_list(data_of_persons: List[Dict]) -> None:
    """
    Add chosen body to blacklist

    :param data_of_persons: List of data of Tinder Users
    """

    explain_line = 'Get number of person why you want to add to black list'
    chosen_id = _interface_to_add_list(data_of_persons, explain_line)

    add_to_black_list(data_of_persons[chosen_id])


def interface_for_favorite_list(data_of_persons: List[Dict]) -> None:
    """
    Add person to favorite list in database

    :param data_of_persons: a list of data of Tinder Users from which we will choose who to add to the favorite list
    """

    explain_line = 'Get number of person why you want to add to favorite list'
    chosen_id = _interface_to_add_list(data_of_persons, explain_line)

    add_to_favorite_list(data_of_persons[chosen_id])


def _interface_to_add_list(data_of_persons: List[Dict], explanatory_line: str) -> int:
    """
    Help function for function with "interface_for_*_list"

    :param data_of_persons: List of data of Tinder Users from which we will chose one
    :param explanatory_line: A string that explains what we will do with the selected person.
    """

    enumerated_person = list(enumerate(data_of_persons))
    while True:
        chosen_id = input(f'{explanatory_line} '
                          f'from {enumerated_person[0][0] + 1} to {enumerated_person[-1][0] + 1}, please: ')
        try:
            chosen_id = int(chosen_id) - 1
            if chosen_id > enumerated_person[-1][0] or chosen_id < enumerated_person[0][0]:
                raise ValueError
            break
        except ValueError:
            print('You did wrong, repeat please')

    return chosen_id


def output_result_to_json(data_of_top10_matching: List[Dict]) -> None:
    """
    Save result of last search to output.json in current working directory

    :param data_of_top10_matching: List of data of Tinder users
    """

    with open(PATH_TO_OUTPUT_RESULT, encoding='utf8', mode='w') as json_output:
        json.dump(data_of_top10_matching, json_output, indent=2)


def run_app():
    main_user = MainUser()
    main_user_config = main_user.get_search_config_obj()

    turn_on_the_app = True
    while True and turn_on_the_app:
        main_user_config['offset_for_search'] += main_user.count_for_search
        searched_tinder_users = VkMachinery.users_search(config=main_user_config)

        processed_data_of_tinder_users = VkMachinery.get_processed_data_of_tinder_users(
            searched_users=searched_tinder_users)

        for data_of_tinder_user in processed_data_of_tinder_users:
            TinderUser(init_obj=data_of_tinder_user)

        main_user.update_search_offset()
        data_of_top10_matching = tact_of_app(main_user)
        output_tinder_users(data_of_top10_matching)

        while True:
            try:
                command = int(input('What are you want to do?\n'
                                    '1.Continue search\n'
                                    '2.Add to favorite list somebody\n'
                                    '3.Add to black list somebody\n'
                                    '4.Print output(10 JSON objects)\n'
                                    '5.Output again\n'
                                    '6.Quit from the app and output result the app to json file \n'
                                    'Your chose: '))

                if command == 1:
                    break
                elif command == 2:
                    interface_for_favorite_list(data_of_top10_matching)
                elif command == 3:
                    interface_for_black_list(data_of_top10_matching)
                elif command == 4:
                    pprint(json.dumps(data_of_top10_matching))
                elif command == 5:
                    output_tinder_users(data_of_top10_matching)
                elif command == 6:
                    turn_on_the_app = False
                    output_result_to_json(data_of_top10_matching)
                    break
                else:
                    raise ValueError('Invalid input')
            except ValueError:
                print('Invalid input, repeat your try')


if __name__ == '__main__':
    create_db()
    # There is main point of program. And here we initialize VkMachinery.So those who will import VkMachinery
    # will use it initialized
    VkMachinery.initialize_vk_api(debug=DEBUG)
    run_app()
