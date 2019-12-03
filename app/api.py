import psycopg2.extras
import psycopg2
from flask import Blueprint, render_template, request, session
import json
from . import models
from flask import jsonify
from .db import MySqlClass
from .config import CONFIG

api = Blueprint('api', __name__)

CONFIG_pg = {
    'host': "10.122.35.181",
    'port': 19200,
    'user': "qyw",
    'password': 'ogg_4186',
    'database': 'qyw_yjzb'
}

db = MySqlClass(CONFIG.MYSQL['host'], CONFIG.MYSQL['port'], CONFIG.MYSQL['user'],
                CONFIG.MYSQL['password'], CONFIG.MYSQL['database'])


class Postgres(object):
    def __init__(self):
        self.con = psycopg2.connect(host=CONFIG_pg['host'],
                                    port=CONFIG_pg['port'],
                                    user=CONFIG_pg['user'],
                                    password=CONFIG_pg['password'],
                                    database=CONFIG_pg['database'])

        self.curr = self.con.cursor(
            cursor_factory=psycopg2.extras.RealDictCursor)

    def select(self, sql):
        self.curr.execute(sql)
        result = self.curr.fetchall()
        self.con.commit()
        return result

    def close(self):
        self.curr.close()
        self.con.close()


@api.route("/api/pg/<table_name>/")
def pg_query(table_name):
    db = Postgres()
    sql = 'SELECT * FROM "public"."' + table_name + '";'
    print(sql)
    result = db.select(sql)
    rows = [str(dict(item)) for item in result]
    db.close()
    return jsonify(rows)


@api.route("/api/my/<table_name>/")
def my_query(table_name):
    sql = 'SELECT * FROM `{0}` limit 5;'.format(table_name)
    print(sql)
    result = db.select(sql)
    rows = [str(dict(item)) for item in result]
    # db.close()
    return jsonify(rows)