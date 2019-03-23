from config.config_app import DB_USER, DB_NAME, STANDARD_SEARCH_OFFSET
from utils import StrOrInt
from typing import List, Dict
import psycopg2 as pg


def create_db() -> None:
    """
    Create standard databases for the Tinder App
    """

    with pg.connect(dbname=DB_NAME, user=DB_USER) as conn:
        with conn.cursor() as cur:
            cur.execute("""CREATE TABLE IF NOT EXISTS tinder_result(
                        id serial PRIMARY KEY,
                        first_name varchar(50) NOT NULL,
                        last_name varchar(50) NOT NULL,
                        vk_link varchar(100) UNIQUE NOT NULL);""")

            cur.execute("""CREATE TABLE IF NOT EXISTS tinder_black_list(
            id serial PRIMARY KEY,
            first_name varchar(50),
            last_name varchar(50),
            vk_link varchar(100) UNIQUE NOT NULL);""")

            cur.execute("""CREATE TABLE IF NOT EXISTS tinder_favorite_list(
                        id serial PRIMARY KEY,
                        second_id INTEGER NOT NULL REFERENCES tinder_result(id));""")

            cur.execute("""CREATE TABLE IF NOT EXISTS last_run_state(
                        id serial PRIMARY KEY,
                        vk_id INTEGER UNIQUE NOT NULL,
                        desired_age_from INTEGER,
                        desired_age_to INTEGER,
                        current_offset INTEGER);""")


def init_user_in_last_run_state(user_vk_id: StrOrInt) -> None:
    """
    Initializes the TinderUser in the last_run_state table

    :param user_vk_id: vk_id of TinderUser (vk_id from the VK site)
    """

    with pg.connect(dbname=DB_NAME, user=DB_USER) as conn:
        with conn.cursor() as cur:
            cur.execute("""INSERT INTO last_run_state (vk_id, current_offset, desired_age_from,
                            desired_age_to) VALUES (%s, %s, %s, %s) ON CONFLICT (vk_id) DO NOTHING """,
                        (int(user_vk_id), int(STANDARD_SEARCH_OFFSET), 0, 0))


def insert_result_to_db(liked_tinder_users: List[Dict]) -> None:
    """
    Insert result the result of the Tinder App

    :param liked_tinder_users: List of dict of tinder user data
    """

    with pg.connect(dbname=DB_NAME, user=DB_USER) as conn:
        with conn.cursor() as cur:
            processed_users = [(user['first_name'], user['last_name'], user['vk_link']) for user in liked_tinder_users]
            cur.executemany("""INSERT INTO tinder_result (first_name, last_name, vk_link)
                                            VALUES (%s, %s, %s) ON CONFLICT (vk_link) DO NOTHING""",
                            processed_users)


def add_to_black_list(person: Dict) -> None:
    """
    Add person to blacklist in database

    :param person: Dict of user data
    :return:
    """

    with pg.connect(dbname=DB_NAME, user=DB_USER) as conn:
        with conn.cursor() as cur:
            cur.execute("""INSERT INTO tinder_black_list (first_name, last_name, vk_link) VALUES (%s, %s, %s)
                        ON CONFLICT (vk_link) DO NOTHING""",
                        (person['first_name'], person['last_name'], person['vk_link'],))

    print(f'person {person["first_name"]} added to black list')


def add_to_favorite_list(person: Dict) -> None:
    """
    Add person to favorite list in database

    :param person: Dict of user data
    """

    with pg.connect(dbname=DB_NAME, user=DB_USER) as conn:
        with conn.cursor() as cur:
            cur.execute("""SELECT id FROM tinder_result WHERE vk_link=%s""", (person['vk_link'],))
            id_user_from_table_tinder_result = cur.fetchone()[0]

            cur.execute("""INSERT INTO tinder_favorite_list (second_id) VALUES (%s)""",
                        (id_user_from_table_tinder_result,))

            print(f'person {person["first_name"]} added to favorite list')


def get_last_desired_age_from(user_id: int) -> int:
    """
    Return value of "desired_age_from" of particular user  from the "last_run_state" table in database

    :param user_id: id (tinder_user_id) particular user
    """

    with pg.connect(dbname=DB_NAME, user=DB_USER) as conn:
        with conn.cursor() as cur:
            cur.execute("""SELECT desired_age_from FROM last_run_state WHERE vk_id=(%s)""",
                        (user_id,))

            return cur.fetchone()[0]


def get_last_desired_age_to(user_id: int) -> int:
    """
    Return value of "desired_age_to" of particular user from the "last_run_state" table in database

    :param user_id: id (tinder_user_id) particular user
    """

    with pg.connect(dbname=DB_NAME, user=DB_USER) as conn:
        with conn.cursor() as cur:
            cur.execute("""SELECT desired_age_from FROM last_run_state WHERE vk_id=(%s)""",
                        (user_id,))

            return cur.fetchone()[0]
