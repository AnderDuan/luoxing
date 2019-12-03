from flask import Blueprint, render_template, request
from .ext import power
from . import models
import json

admin = Blueprint('admin', __name__)


@admin.route("/admin/manage/apply/")
@power
def asset():
    return render_template('admin/manage/apply.html',
                           classID='nav-apply-table',
                           navID='manage')


@admin.route("/admin/manage/tables/")
@power
def tables():
    return render_template("admin/manage/tables.html",
                           classID="nav-manage-tables",
                           navID='manage')


@admin.route("/admin/manage/connections/")
@power
def themes():
    return render_template("admin/manage/connections.html",
                           classID="nav-manage-connections",
                           navID='manage')


@admin.route("/admin/manage/bloods/")
@power
def bloods():
    return render_template("admin/manage/bloods.html",
                           classID="nav-manage-bloods",
                           navID='manage')


@admin.route("/admin/manage/sqls/")
@power
def sqls():
    return render_template("admin/manage/sqls.html",
                           classID="nav-manage-sqls",
                           navID='manage')


@admin.route("/admin/manage/reports/")
@power
def reports():
    return render_template("admin/manage/reports.html",
                           classID="nav-manage-reports",
                           navID='manage')


@admin.route("/admin/manage/newuser")
@power
def newuser():
    return render_template("admin/manage/newuser.html",
                           classID="nav-manage-newuser")


@admin.route("/admin/manage/userrole")
@power
def userrole():
    return render_template("admin/manage/userrole.html",
                           classID="nav-manage-userrole")


@admin.route("/admin/manage/beg")
def beg():
    return render_template("admin/manage/beg.html", classID="nav-manage-beg")


@admin.route("/admin/manage/reprots/")
@power
def reprots():
    return render_template("admin/manage/upreprots.html",
                           classID="nav-manage-reprots")


@admin.route("/admin/manage/upapi/")
@power
def upapi():
    return render_template("admin/manage/upapi.html",
                           classID="nav-manage-upapi")


@admin.route("/admin/manage/flow/")
@power
def applyflow():
    return render_template("admin/manage/flow.html", classID="nav-manage-flow")
