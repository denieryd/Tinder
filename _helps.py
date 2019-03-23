import psycopg2 as pg
from config.config_app import DB_USER, DB_NAME


def DROP_ALL_TABLE():
    with pg.connect(dbname=DB_NAME, user=DB_USER) as conn:
        with conn.cursor() as cur:
            cur.execute("""DROP TABLE IF EXISTS last_run_state;""")
            cur.execute("""DROP TABLE IF EXISTS tinder_result;""")
            cur.execute("""DROP TABLE IF EXISTS tinder_black_list;""")
            cur.execute("""DROP TABLE IF EXISTS tinder_favorite_list;""")


DROP_ALL_TABLE()
