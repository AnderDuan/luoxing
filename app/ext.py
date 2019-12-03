# -*- coding:utf-8 -*-
from flask import session, redirect, url_for
from functools import wraps


def is_login(func):
    @wraps(func)
    def check_login(*args, **kwargs):
        if 'user_id' in session:
            return func(*args, **kwargs)
        else:
            return redirect('/login/')

    return check_login


def power(func):
    @wraps(func)
    def check_power(*args, **kwargs):
        print(session)
        role_id = session['user_id']['role_id']
        if role_id != 1:
            return func(*args, **kwargs)
        else:
            return redirect('/index/')

    return check_power
