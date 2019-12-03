import numpy as np
import json
from flask import Blueprint, render_template, request, session, Response, make_response
from flask import jsonify
from .db import MySqlClass
from .config import CONFIG
from . import models
import os
import xlrd
import uuid
from .ext import is_login
from datetime import datetime
import time

restful = Blueprint('restful', __name__)

ALLOWED_EXTENSIONS = ['xlsx']

db = MySqlClass(CONFIG.MYSQL['host'], CONFIG.MYSQL['port'], CONFIG.MYSQL['user'],
                CONFIG.MYSQL['password'], CONFIG.MYSQL['database'])


# 加载数据资产的第一次请求后端
@restful.route("/restful/relations/<table_schema>/<table_name>/")
def relatations(table_schema, table_name):
    # 初始化本表
    data = {}
    links = []
    nodes = []
    node = {
        'category': '当前表',
        'x': np.random.rand() * 150,
        'y': np.random.rand() * 150,
        # 'x': 150,
        # 'y': 150,
        'name': table_name,
        'symbolSize': 30,
        'symbol': 'image:///static/images/favicon.ico',
        'itemStyle': {
            'color': '#60acfc'
        },
        'value': '/tables/{0}/{1}/'.format(table_schema, table_name)
        # 'label': {
        #     'normal': {'show': True}
        # }
    }
    nodes.append(node.copy())
    link = {}

    # 表关联关系表
    sql = '''
        Select * From(
        SELECT distinct relate_table_name FROM `dasset_tables_connections` t 
        where t.main_table_name='{0}' or t.relate_table_name='{0}') a
        Where a.relate_table_name!='{0}'
    '''.format(table_name)
    result = db.select(sql)
    # for item in result 相当于java的foreach 在result集合里每一个元素是item
    for item in result:
        # 声明两个变量node 跟link
        node = {}
        link = {}
        # node是{'category': 随机整数1到10}
        node['category'] = np.random.randint(1, 10)
        # node是{'x': 随机数0.999999*300以内}
        node['x'] = np.random.rand() * 300
        node['y'] = np.random.rand() * 300
        node['symbolSize'] = np.random.rand() * 5 + 5
        # 每次循环取出item里面的relate_table_name的值赋值给node里name属性
        node['name'] = item['relate_table_name']
        node['itemStyle'] = {'color': '#ff7c7c'}  # {'color': '#32d3eb'}
        node['value'] = '/tables/{0}/{1}/'.format(table_schema, table_name)
        # node['label']['normal']['show'] = True

        link['target'] = table_name
        link['source'] = item['relate_table_name']
        link['value'] = '/tables/{0}/{1}/'.format(table_schema, table_name)
        link['lineStyle'] = {'width': np.random.rand() * 5 + 5}
        # print(node)
        nodes.append(node.copy())
        links.append(link.copy())

    # 本表字段的关系
    sql = '''
        SELECT * FROM `dasset_columns` t  where t.TABLE_NAME='{0}' and t.table_schema='{1}'
    '''.format(table_name, table_schema)
    result = db.select(sql)
    for item in result:
        node = {}
        link = {}
        node['category'] = np.random.randint(1, 10)
        node['name'] = item['TABLE_NAME'] + "/" + item['COLUMN_NAME']
        node['x'] = np.random.rand() * 300
        node['y'] = np.random.rand() * 300
        node['symbolSize'] = np.random.rand() * 5 + 5
        node['itemStyle'] = {'color': '#32d3eb'}  # 'color': '#ff7c7c'
        node['value'] = '/tables/{0}/{1}/'.format(table_schema, table_name)

        link['source'] = item['TABLE_NAME'] + "/" + item['COLUMN_NAME']
        link['target'] = table_name
        link['value'] = '/tables/{0}/{1}/'.format(table_schema, table_name)

        nodes.append(node.copy())
        links.append(link.copy())

    data['links'] = links
    data['nodes'] = nodes
    return jsonify(data)


@restful.route("/restful/echarts/")
def echats():
    return render_template("echarts.html")


# 通过业务一级、业务二级、业务三级、流程名称、环节名称、表名称获取该表的详细字段与关联关系
@restful.route(
    "/restful/qyw_tables_connections/<lv1>/<lv2>/<lv3>/<process_name>/<link_name>/<business_info>/<table_name>/"
)
def qyw_tables_connections(lv1, lv2, lv3, process_name, link_name,
                           business_info, table_name):
    # 初始化本表
    data = {}
    links = []
    nodes = []
    node = {
        'category':
        1,
        'x':
        np.random.rand() * 300,
        'y':
        np.random.rand() * 300,
        'name':
        table_name,
        'symbolSize':
        40,
        'itemStyle': {
            'color': '#60acfc'
        },
        'value':
        '/process_table_column/{0}/{1}/{2}/{3}/{4}/{5}/{6}/'.format(
            lv1, lv2, lv3, process_name, link_name, business_info, table_name)
        # 'label': {
        #     'normal': {'show': True}
        # }
    }
    nodes.append(node.copy())
    link = {}

    sql = '''
        SELECT distinct relate_table_name FROM `dasset_tables_connections` t where t.main_table_name='{0}'
    '''.format(table_name)
    result = db.select(sql)

    # 表血缘关系
    for item in result:
        node = {}
        link = {}
        node['category'] = np.random.randint(1, 10)
        node['x'] = np.random.rand() * 300
        node['y'] = np.random.rand() * 300
        node['symbolSize'] = np.random.rand() * 20 + 20
        node['name'] = item['relate_table_name']
        node['itemStyle'] = {'color': '#32d3eb'}
        # node['label']['normal']['show'] = True

        link['target'] = table_name
        link['source'] = item['relate_table_name']
        link['value'] = np.random.rand() * 10 + 20
        link['lineStyle'] = {'width': np.random.rand() * 5 + 5}
        # print(node)
        nodes.append(node.copy())
        links.append(link.copy())

    # 本表字段的关系
    sql = '''
        SELECT * FROM `qyw_data_assets_check` t  where t.TABLE_NAME_EN='{0}'
        and t.lv_1_operation='{1}' and t.lv_2_operation='{2}' 
        and t.lv_3_operation='{3}' And t.process_name='{4}'
        And t.link_name = '{5}' And t.business_info='{6}'
    '''.format(table_name, lv1, lv2, lv3, process_name, link_name,
               business_info)
    # print(sql)
    result = db.select(sql)
    for item in result:
        node = {}
        link = {}
        node['category'] = np.random.randint(1, 10)
        node['name'] = item['table_name_en'] + "/" + item['column']
        node[
            'value'] = '/process_table_column/{0}/{1}/{2}/{3}/{4}/{5}/{6}'.format(
                item['lv_1_operation'], item['lv_2_operation'],
                item['lv_3_operation'], item['process_name'],
                item['link_name'], item['business_info'],
                item['table_name_en'])
        node['x'] = np.random.rand() * 300
        node['y'] = np.random.rand() * 300
        node['symbolSize'] = np.random.rand() * 5 + 5
        node['itemStyle'] = {'color': '#ff7c7c'}

        link['source'] = item['table_name_en'] + "/" + item['column']
        link['target'] = table_name
        # link['value'] = np.random.rand() * 5 + 5
        link[
            'value'] = '/process_table_column/{0}/{1}/{2}/{3}/{4}/{5}/{6}/'.format(
                item['lv_1_operation'], item['lv_2_operation'],
                item['lv_3_operation'], item['process_name'],
                item['link_name'], item['business_info'],
                item['table_name_en'])

        nodes.append(node.copy())
        links.append(link.copy())

    data['links'] = links
    data['nodes'] = nodes
    return jsonify(data)


# 表详情页的血缘关系表和关联关系表的展示图
@restful.route("/restful/bloods/<schema_name>/<table_name>/")
def bloods(schema_name, table_name):
    # 初始化本表 ####################################################################################
    data = {}
    links = []
    nodes = []
    node = {
        'category': "当前表",
        'x': np.random.rand() * 10 + 300,
        'y': np.random.rand() * 10 + 150,
        'name': table_name,
        'symbolSize': 40,
    }
    nodes.append(node.copy())
    link = {}

    # 表关系表 --------------------------------------------------------------------------------------------
    sql = '''
        Select * From (
        SELECT distinct relate_table_name FROM `dasset_tables_connections` t
        where t.main_table_name='{0}' or t.relate_table_name='{0}') as a
        where relate_table_name!='{0}'
    '''.format(table_name)
    result = db.select(sql)
    for item in result:
        node = {}
        link = {}
        node['category'] = '关联表'
        node['x'] = np.random.rand() * 10 + 350
        node['y'] = np.random.rand() * 300
        node['symbolSize'] = np.random.rand() * 20 + 20
        node['name'] = item['relate_table_name']
        link['target'] = table_name
        link['source'] = item['relate_table_name']
        link['value'] = '关联表'
        link['lineStyle'] = {'width': np.random.rand() * 5 + 5}
        nodes.append(node.copy())
        links.append(link.copy())
        sql = '''
            SELECT * FROM `dasset_columns` t  where t.TABLE_NAME='{0}' and t.TABLE_SCHEMA='{1}'
        '''.format(item['relate_table_name'], schema_name)
        sub_result = db.select(sql)
        for sub in sub_result:
            sub_node = {}
            sub_link = {}
            sub_node['category'] = '关联表字段'
            sub_node['name'] = sub['TABLE_NAME'] + "/" + sub['COLUMN_NAME']
            sub_node['x'] = np.random.rand() * 50 + 50
            sub_node['y'] = np.random.rand() * 300
            sub_node['symbolSize'] = np.random.rand() * 5 + 5
            sub_link['source'] = sub['TABLE_NAME'] + "/" + sub['COLUMN_NAME']
            sub_link['target'] = item['relate_table_name']
            sub_link['value'] = "关联表字段"

            nodes.append(sub_node.copy())
            links.append(sub_link.copy())

    # 本表字段的关系 ------------------------------------------------------------------------------
    sql = '''
        SELECT * FROM `dasset_columns` t  where t.TABLE_NAME='{0}' and t.TABLE_SCHEMA='{1}'
    '''.format(table_name, schema_name)
    result = db.select(sql)
    for item in result:
        node = {}
        link = {}
        node['category'] = '当前表字段'
        node['name'] = item['TABLE_NAME'] + "/" + item['COLUMN_NAME']
        node['x'] = np.random.rand() * 50 + 50
        node['y'] = np.random.rand() * 300
        node['symbolSize'] = np.random.rand() * 5 + 5
        link['source'] = item['TABLE_NAME'] + "/" + item['COLUMN_NAME']
        link['target'] = table_name
        link['value'] = "当前表字段"

        nodes.append(node.copy())
        links.append(link.copy())

    # 血缘关系表 -----------------------------------------------------------------------------------
    sql = '''
        Select lower(source_table_name) as source_table_name 
        From `dasset_tables_blood` Where target_table_name = '{0}'
    '''.format(table_name)
    result = db.select(sql)
    for item in result:
        node = {}
        link = {}

        node['category'] = '血缘表'
        node['name'] = item['source_table_name']
        node['x'] = np.random.rand() * -10 - 300
        node['y'] = np.random.rand() * 10 + 150
        node['symbolSize'] = np.random.rand() * 10 + 40
        # node['itemStyle'] = {
        #     'color': '#9287e7'
        # }

        link['source'] = item['source_table_name']
        link['target'] = table_name
        link['value'] = '血缘表'
        link['lineStyle'] = {'width': np.random.rand() * 5 + 5}

        nodes.append(node.copy())
        links.append(link.copy())

    # 血缘字段表 #########################################################################################
    sql = '''
        SELECT
            distinct
            LOWER( table_target_name ) AS table_target_name,
            lower( target_column_name ) AS target_column_name,
            lower(source_table_name) as source_table_name,
            lower( source_column_name ) AS source_column_name 
        FROM
            `dasset_columns_blood` 
        WHERE
            table_target_name = '{0}'
    '''.format(table_name)
    result = db.select(sql)
    for item in result:
        node = {}
        link = {}

        node['category'] = '血缘字段'
        node['name'] = item['target_column_name'] + \
                       "/" + item['source_column_name']
        node['x'] = np.random.rand() * -50 - 50
        node['y'] = np.random.rand() * 300
        node['symbolSize'] = np.random.rand() * 5 + 5
        # node['itemStyle'] = {
        #     'color': '#9287e7'
        # }

        link['source'] = item['target_column_name'] + \
                         "/" + item['source_column_name']
        link['target'] = item['table_target_name'] + \
                         "/" + item['target_column_name']
        link['value'] = '血缘字段'

        nodes.append(node.copy())
        links.append(link.copy())

        link = {}
        link['source'] = item['source_table_name']
        link['target'] = item['target_column_name'] + \
                         "/" + item['source_column_name']
        link['value'] = '血缘字段'

        links.append(link)

    data['links'] = links
    data['nodes'] = nodes
    return jsonify(data)


@restful.route("/restful/content_tree/")
def content_tree():
    tree = {}
    tree['name'] = "数据资产目录"
    sql = "Select `model_name` as `name`,id as value From `dasset_models`"
    result_cim = db.select(sql)
    for item in result_cim:
        item['value'] = '/themes_menu/?id={0}'.format(item['value'])
    sql = "Select Distinct source_system as `name` from `qyw_data_assets_check` where source_system!=''"
    result_system = db.select(sql)
    tree['children'] = [{
        'name':
        '主题',
        'children': [{
            'name': 'CIM',
            'children': result_cim
        }
                     # {'name':'业务主题','children':result_system}
                     ]
    }]
    sub_tree = []
    for item in result_system:
        sql = '''
            SELECT distinct process_name as `name` 
            FROM `qyw_data_assets_check` where source_system='{0}' and process_name!=""
        '''.format(item['name'])
        result_system = db.select(sql)
        for k in result_system:
            k['value'] = "/systems_menu/?id={0}&process_name={1}".format(
                item['name'], k['name'])
        sub_tree.append({'name': item['name'], 'children': result_system})
    tree['children'][0]['children'].append({
        'name': '业务主题',
        'children': sub_tree
    })

    sql = '''
        SELECT
            t1.`system` AS `name`,
            t2.table_schema AS `value`       
        FROM
            dasset_system_names t1
            LEFT JOIN ( SELECT DISTINCT table_schema FROM dasset_tables ) t2 ON t2.table_schema LIKE concat( "%", t1.`name`, "%" )
    '''
    result = db.select(sql)
    for item in result:
        item['name'] = item['name'] + item['value']
        item['value'] = "/assets/?name={0}".format(item['value'])
    tree['children'].append({'name': '系统', 'children': result})
    return jsonify(tree)


@restful.route("/restful/content_tree/system_menu/")
def content_tree_system_menu():
    sql = '''
        SELECT distinct source_system FROM `qyw_data_assets_check`
    '''
    systems = db.select(sql)
    all_tree = {'name': '数据系统', 'children': []}
    for system in systems:
        tree = {'name': system['source_system'], 'children': []}
        sql = '''
            SELECT DISTINCT lv_1_operation,lv_2_operation,lv_3_operation,process_name 
            FROM `qyw_data_assets_check` where process_name!='' and source_system='{0}'
        '''.format(system['source_system'])
        result = db.select(sql)
        sub_tree = {}
        for item in result:
            if item['lv_1_operation'] in sub_tree:
                if item['lv_2_operation'] in sub_tree[item['lv_1_operation']]:
                    if item['lv_3_operation'] in sub_tree[
                            item['lv_1_operation']][item['lv_2_operation']]:
                        sub_tree[item['lv_1_operation']][
                            item['lv_2_operation']][
                                item['lv_3_operation']].append(
                                    item['process_name'])
                    else:
                        sub_tree[item['lv_1_operation']][
                            item['lv_2_operation']][item['lv_3_operation']] = [
                                item['process_name']
                            ]
                else:
                    sub_tree[item['lv_1_operation']][
                        item['lv_2_operation']] = {
                            item['lv_3_operation']: [item['process_name']]
                        }
            else:
                sub_tree[item['lv_1_operation']] = {
                    item['lv_2_operation']: {
                        item['lv_3_operation']: [item['process_name']]
                    }
                }
        # print(sub_tree)
        lv_1_tree = []
        for lv1 in sub_tree:
            lv_2_tree = []
            for lv2 in sub_tree[lv1]:
                lv_3_tree = []
                for lv3 in sub_tree[lv1][lv2]:
                    lv_4_tree = []
                    # print(lv3)
                    for lv4 in sub_tree[lv1][lv2][lv3]:
                        value = lv4
                        lv_4_tree.append({
                            'name': lv4,
                            'value': value,
                            'itemStyle': {
                                'color': '#60acfc',
                                'borderColor': '#60acfc'
                            }
                        })
                    lv_3_tree.append({
                        'name': lv3,
                        'children': lv_4_tree,
                        'itemStyle': {
                            'color': '#32d3eb',
                            'borderColor': '#32d3eb'
                        }
                    })
                lv_2_tree.append({
                    'name': lv2,
                    'children': lv_3_tree,
                    'itemStyle': {
                        'color': '#feb64d',
                        'borderColor': '#feb64d'
                    }
                })
            lv_1_tree.append({
                'name': lv1,
                'children': lv_2_tree,
                'itemStyle': {
                    'color': '#9287e7',
                    'borderColor': '#9287e7'
                }
            })
        tree['children'] = lv_1_tree
        all_tree['children'].append(tree)
    return jsonify(all_tree)


@restful.route("/restful/assets_contents/")
def assets_contents():
    data = {}
    links = []
    nodes = []
    link = {}
    node = {}
    sql = '''
        SELECT * FROM `dasset_models` where model_name!=''
    '''
    result = db.select(sql)
    for item in result:
        node = {}
        node['name'] = item['model_name']
        # node['value'] = item['id']
        # node['x'] = np.random.rand() * 60
        node['x'] = item['id']
        node['y'] = np.random.rand() * 60
        # node['symbolSize'] = np.random.rand() * 30 + 100
        node['label'] = {'normal': {'show': True}}
        node['itemStyle'] = {'color': '#60acfc'}
        for k in result:
            if k != item:
                link['target'] = item['model_name']
                link['source'] = k['model_name']
                links.append(link.copy())

        nodes.append(node)

    data['nodes'] = nodes
    data['links'] = links
    return jsonify(data)


# 判断登录的业务逻辑
@restful.route("/restful/login/", methods=['POST'])
def login():
    user_id = request.form.get("user_id")
    password = request.form.get("password")
    user_login = models.UserLogin()
    user = user_login.login(user_id, password)
    print(user)
    if len(user) == 0:
        return '您的用户名或密码错误'
    else:
        session['user_id'] = user[0]
        resp = Response()
        resp.set_cookie("user_id", user_id)
        return "登陆成功"


@restful.route("/restful/qyw_tables/menu/operation/")
def qyw_menus_operation():
    lv1 = request.args.get("lv1")
    lv2 = request.args.get("lv2")
    model = models.QywTables()
    if not lv2:
        menu_lv_2 = model.lv_2_operation(lv1)
        lv2 = menu_lv_2[0]['lv_2_operation']
        menu_lv_3 = model.lv_3_operation(lv1, lv2)
        menu = {
            'lv2': [item['lv_2_operation'] for item in menu_lv_2],
            'lv3': [item['lv_3_operation'] for item in menu_lv_3]
        }
        return jsonify(menu)
    else:
        menu_lv_3 = model.lv_3_operation(lv1, lv2)
        return jsonify([item['lv_3_operation'] for item in menu_lv_3])


@restful.route("/restful/qyw_tables/menu/process/")
def qyw_menus_process():
    lv1 = request.args.get("lv1")
    lv2 = request.args.get("lv2")
    model = models.QywTables()
    if not lv2:
        menu_lv_2 = model.link_name(lv1)
        lv2 = menu_lv_2[0]['lv_2_operation']
        menu_lv_3 = model.business_info(lv1, lv2)
        menu = {
            'lv2': [item['lv_2_operation'] for item in menu_lv_2],
            'lv3': [item['lv_3_operation'] for item in menu_lv_3]
        }
        return jsonify(menu)
    else:
        menu_lv_3 = model.business_info(lv1, lv2)
        return jsonify([item['lv_3_operation'] for item in menu_lv_3])


@restful.route('/restful/api/<table_name>/')
def api_apply(table_name):
    func = request.args.get("do")
    data = request.args.get('data')
    where = request.args.get('where', "")
    limit_num = request.args.get("limit", "")
    skip_num = request.args.get("skip", "")
    apply = models.DbModel(table_name)
    if data:
        data = data.replace("[[[and]]]", "&")
        data = json.loads(data, strict=False)
    if func == "insert":
        apply.insert(data)
        return '增加成功'
    elif func == "update":
        apply.update(data)
        return '修改成功'
    elif func == "deletes":
        apply.deletes(data)
        return "批量删除成功"
    # 删除表根据id
    elif func == "delete":
        delete_data = data['id']
        apply.delete(delete_data)
        return '删除成功'
    elif func == "select":
        if where:
            result = apply.select(where=where.replace('"', ''),
                                  limit=limit_num,
                                  skip=skip_num)
        else:
            result = apply.select(limit=limit_num, skip=skip_num)
        return jsonify(result)


# 用于判断文件后缀
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


# basedir = os.path.abspath(os.path.dirname(__file__))


@restful.route('/restful/upload/<table_name>/', methods=['POST'])
def upload(table_name):
    # 从表单的file字段获取文件，file为该表单的name值
    f = request.files['file']
    print(f.filename)

    # 获取文件拆分之后的后缀
    fname = f.filename.split(".", 1)[-1]
    # 判断该文件的后缀是否是符合规定的 xlsx文件
    if fname not in ALLOWED_EXTENSIONS:
        print("不符合规定")
        return "402"

    print(fname)
    # 如果符合就生成uuid在拼接上后缀生成新的文件名
    new_fname = uuid.uuid1().__str__() + "." + fname
    print(new_fname)

    # file_dir = os.path.join(basedir, 'uploads')

    # 如果没有该目录就创建一个
    # if not os.path.exists(file_dir):
    #     os.makedirs(file_dir)
    #     #把文件保存到规定的目录下
    f.save("app/static/uploads/" + new_fname)

    path = "app/static/uploads/" + new_fname
    workbook = xlrd.open_workbook(
        path)  # downPath承接上面下载文件的路径，这个读取文件路径都是可以换成自己的
    Data_sheet = workbook.sheets()[0]  # 通过索引获取
    rowNum = Data_sheet.nrows  # sheet行数
    colNum = Data_sheet.ncols  # sheet列数
    print(rowNum)
    print(colNum)
    # 获取model对象
    apply = models.DbModel(table_name)
    # 循环得道想要的字典然后往里添加

    for i in range(1, rowNum):
        # rowlist = []
        dic = {}
        for j in range(colNum):
            dic[Data_sheet.cell_value(0, j)] = Data_sheet.cell_value(i, j)
        # 插入操作
        apply.insert(dic)
        # rowlist.append({}Data_sheet.cell_value(i, j))

    return str(rowNum - 1)


# 分页
@restful.route('/restful/paging/<table_name>/', methods=['GET'])
def paging(table_name):
    # 获取前端是要干啥
    func = request.args.get("do")
    # 初始化model模板
    apply = models.DbModel(table_name)
    # 查询总数操作
    if func == "count_num":
        result = apply.count()
        return str(result)


# 添加购物车
@restful.route('/restful/shopcar/save_order/')
def save_order():
    data = json.loads(request.args.get("data"))
    # 判断为空么
    if data is None:
        return "400"
    model = models.ShopCar()
    code = model.save_order(data)
    if code == '已经存在':
        return '已经存在'
    else:
        return '200'


# 根据用户ID获取购物车的物品
@restful.route('/restful/shopcar/list/<user_id>/', methods=['GET'])
def show_shopcar_list(user_id):
    service = models.ShopCar()
    result = service.find_detail_by_userid(user_id)
    return jsonify(result)


# 获取用户表里的审批角色
@restful.route('/restful/shopcar/approve/', methods=['GET'])
def approves():
    service = models.ShopCar()
    approves = service.findApproves()
    return jsonify(approves)


# 审批业务，修改order表
@restful.route('/restful/shopcar/updateinfo/')
def updateinfo():
    data = request.args.get('data')
    data = data.replace("[[[and]]]", "&")
    data = json.loads(data, strict=False)
    # 订单表时间
    data['order_time'] = str(datetime.now())[:19]
    data['status'] = "100"
    service = models.ShopCar()
    # 执行修改
    result = service.update_order_info(data)
    return jsonify(result)


@restful.route("/restful/shopcar/delete_item/")
@is_login
def delete_item():
    detail_id = request.args.get("id")
    model = models.ShopCar()
    model.delete_detail_item(detail_id)
    return '200'


# 数据报表相关的请求
@restful.route('/get_reports_by_major/')
def findDataByReprots():
    model = models.Reports()
    majors = model.majors()
    major = request.args.get("major", majors[0]['major'])
    data = model.reports(major)
    return jsonify(data)


@restful.route('/restful/upimage/<table_name>/', methods=['POST'])
def upImage(table_name):
    data = request.args.get('data')
    if data:
        data = json.loads(data, strict=False)
        uid = session['user_id']['user_id']
        print(uid)
        data['create_uid'] = uid
        print(data)
        apply = models.DbModel(table_name)
        apply.insert(data)
        return "上传成功"
    else:
        IMAGE_FORMAT = ['jpg', 'png', 'gif', 'jpeg']
        f = request.files['file']
        print(f.filename)
        fname = f.filename.split(".", 1)[-1]
        if fname not in IMAGE_FORMAT:
            print("不符合规定")
            return "402"
        #new_fname = uuid.uuid1().__str__() + "." + fname
        new_fname = datetime.now().timestamp().__str__().split(".")[0]
        f.save("app/static/upimages/" + new_fname)
        # path = "app/static/upimages/" + new_fname
        return new_fname


@restful.route('/restful/flow_control/<table_name>/')
def flowControl(table_name):
    id = request.args.get("id")
    oid = request.args.get("oid")
    data = request.args.get("data")
    result = models.apiupdate(table_name, id, data, oid)
    return result


@restful.route(
    '/restful/user_control/<table_name1>/<table_name2>/<table_name3>/')
def user_control(table_name1, table_name2, table_name3):
    result = models.select_role(table_name1, table_name2, table_name3)
    return jsonify(result)


@restful.route('/restful/user_control/<table_name>/')
def userRole(table_name):
    user_id = request.args.get("user_id")
    role_id = request.args.get("role_id")
    result = models.role_update(table_name, role_id, user_id)
    return result


@restful.route('/restful/messages/')
def messages():
    query_type = request.args.get('query_type', "create")
    model = models.Messages()
    if query_type == 'create':
        msg = request.args.get("msg")
        msg = json.loads(msg)
        msg['msg_time'] = str(datetime.now())[:19]
        msg['status'] = '0'
        model.create_message(msg)
        return '200'
    elif query_type == 'set_read':
        msg_id = request.args.get("id")
        model.set_read(msg_id)
        return '200'


@restful.route('/restful/message/<table_name>/')
def user_message(table_name):
    count = request.args.get("count")
    message = request.args.get("message")
    if count:
        count = session['user_id']['user_id']
    if message:
        message = session['user_id']['user_id']
    result = models.cat_message(table_name, count, message)
    return jsonify(result)


@restful.route('/restful/change_read/')
def read():
    read = request.args.get("read")
    result = models.change_read(read)
    return result


@restful.route("/restful/map/<schema_name>/<table_name>/")
def table_map(schema_name, table_name):
    data = {}
    # 表关系表 --------------------------------------------------------------------------------------------
    sql = '''
        SELECT
        CASE
                relate_table_name 
                WHEN '{0}' THEN
                lower( main_table_name ) ELSE lower( relate_table_name ) 
            END AS table_name,
        CASE
                
                WHEN substr( relation_columns, 1, 1 ) = '(' THEN
                REPLACE (
                    REPLACE (
                        REPLACE ( REPLACE ( lower(relation_columns), "(", concat( main_table_name, "." ) ), "=", concat( '=', relate_table_name, '.' ) ),
                        " ",
                        "" 
                    ),
                    ")",
                    "" 
                ) ELSE lower( relation_columns ) 
            END AS relation_columns 
        FROM
            ( SELECT * FROM `dasset_tables_connections` WHERE relate_table_name = '{0}' OR main_table_name = '{0}' AND relation_columns != '' ) t
    '''.format(table_name)
    result = db.select(sql)
    data['connection_tables'] = result.copy()
    data['connection_table_columns'] = {}
    for item in result:
        sql = '''
            SELECT distinct * FROM `dasset_columns` t  where t.TABLE_NAME='{0}' and t.TABLE_SCHEMA='{1}'
        '''.format(item['table_name'], schema_name)
        sub_result = db.select(sql)
        data['connection_table_columns'][
            item['table_name']] = sub_result.copy()

    # 本表字段的 ------------------------------------------------------------------------------
    sql = '''
        SELECT distinct lower(TABLE_NAME) as table_name,lower(COLUMN_NAME) as column_name
        FROM `dasset_columns` t  where t.TABLE_NAME='{0}' and t.TABLE_SCHEMA='{1}'
    '''.format(table_name, schema_name)
    result = db.select(sql)
    data['current_table_columns'] = result.copy()

    # 血缘关系表 -----------------------------------------------------------------------------------
    sql = '''
        Select distinct lower(source_table_name) as source_table_name 
        From `dasset_tables_blood` Where target_table_name = '{0}'
    '''.format(table_name)
    result = db.select(sql)
    data['blood_tables'] = result.copy()
    data['blood_table_columns'] = {}
    # 血缘字段表 #########################################################################################
    for item in result:
        sql = '''
            SELECT
                distinct
                LOWER( table_target_name ) AS table_target_name,
                lower( target_column_name ) AS target_column_name,
                lower(source_table_name) as source_table_name,
                lower( source_column_name ) AS source_column_name 
            FROM
                `dasset_columns_blood` 
            WHERE
                table_target_name = '{0}' and source_table_name = '{1}'  and `source_column_name` !=""
        '''.format(table_name, item['source_table_name'])
        sub_result = db.select(sql)
        data['blood_table_columns'][
            item['source_table_name']] = sub_result.copy()

    # 影响关系表 -----------------------------------------------------------------------------------
    sql = '''
        Select distinct lower(target_table_name) as target_table_name 
        From `dasset_tables_blood` Where source_table_name='{0}'
    '''.format(table_name)
    result = db.select(sql)
    data['influence_tables'] = result.copy()
    data['influence_table_columns'] = {}
    # 影响字段表 #########################################################################################
    for item in result:
        sql = '''
            SELECT
                distinct
                LOWER( table_target_name ) AS table_target_name,
                lower( target_column_name ) AS target_column_name,
                lower(source_table_name) as source_table_name,
                lower( source_column_name ) AS source_column_name 
            FROM
                `dasset_columns_blood` 
            WHERE
                table_target_name = '{1}' and source_table_name = '{0}'  and `source_column_name` !=""
        '''.format(table_name, item['target_table_name'])
        sub_result = db.select(sql)
        data['influence_table_columns'][
            item['target_table_name']] = sub_result.copy()

    return jsonify(data)


@restful.route(
    "/restful/map/qyw_tables_connections/<lv1>/<lv2>/<lv3>/<process_name>/<link_name>/<business_info>/<table_name>/"
)
def table_map_qyw(lv1, lv2, lv3, process_name, link_name, business_info,
                  table_name):
    data = {}
    # 表关系表 --------------------------------------------------------------------------------------------
    sql = '''
        SELECT
        CASE
                relate_table_name 
                WHEN '{0}' THEN
                lower( main_table_name ) ELSE lower( relate_table_name ) 
            END AS table_name,
        CASE
                
                WHEN substr( relation_columns, 1, 1 ) = '(' THEN
                REPLACE (
                    REPLACE (
                        REPLACE ( REPLACE ( lower(relation_columns), "(", concat( main_table_name, "." ) ), "=", concat( '=', relate_table_name, '.' ) ),
                        " ",
                        "" 
                    ),
                    ")",
                    "" 
                ) ELSE lower( relation_columns ) 
            END AS relation_columns 
        FROM
            ( SELECT * FROM `dasset_tables_connections` WHERE relate_table_name = '{0}' OR main_table_name = '{0}' AND relation_columns != '' ) t
    '''.format(table_name)
    result = db.select(sql)
    data['connection_tables'] = result.copy()
    data['connection_table_columns'] = {}
    for item in result:
        sql = '''
            SELECT distinct * FROM `dasset_columns` t  where t.TABLE_NAME='{0}'
        '''.format(item['table_name'])
        sub_result = db.select(sql)
        data['connection_table_columns'][
            item['table_name']] = sub_result.copy()

    # 本表字段的关系 ------------------------------------------------------------------------------
    sql = '''
        SELECT distinct lower(TABLE_NAME_EN) as table_name,lower(`column`) as column_name,table_id
        FROM `qyw_data_assets_check` t  where t.TABLE_NAME_EN='{0}'
        and t.lv_1_operation='{1}' and t.lv_2_operation='{2}' 
        and t.lv_3_operation='{3}' And t.process_name='{4}'
        And t.link_name = '{5}' And t.business_info='{6}'
    '''.format(table_name, lv1, lv2, lv3, process_name, link_name,
               business_info)
    result = db.select(sql)
    table_id = result[0]['table_id']
    sql = '''
        SELECT distinct lower(TABLE_NAME) as table_name,lower(COLUMN_NAME) as column_name
        FROM `dasset_columns` t  where t.table_id={0}
    '''.format(table_id)

    result = db.select(sql)
    data['current_table_columns'] = result.copy()

    # 血缘关系表 -----------------------------------------------------------------------------------
    sql = '''
        Select distinct lower(source_table_name) as source_table_name 
        From `dasset_tables_blood` Where target_table_name = '{0}'
    '''.format(table_name)
    result = db.select(sql)
    data['blood_tables'] = result.copy()
    data['blood_table_columns'] = {}
    # 血缘字段表 #########################################################################################
    for item in result:
        sql = '''
            SELECT
                distinct
                LOWER( table_target_name ) AS table_target_name,
                lower( target_column_name ) AS target_column_name,
                lower(source_table_name) as source_table_name,
                lower( source_column_name ) AS source_column_name 
            FROM
                `dasset_columns_blood` 
            WHERE
                table_target_name = '{0}' and source_table_name = '{1}'  and `source_column_name` !=""
        '''.format(table_name, item['source_table_name'])
        sub_result = db.select(sql)
        data['blood_table_columns'][
            item['source_table_name']] = sub_result.copy()

    # 影响关系表 -----------------------------------------------------------------------------------
    sql = '''
        Select distinct lower(target_table_name) as target_table_name 
        From `dasset_tables_blood` Where source_table_name='{0}'
    '''.format(table_name)
    result = db.select(sql)
    data['influence_tables'] = result.copy()
    data['influence_table_columns'] = {}
    # 影响字段表 #########################################################################################
    for item in result:
        sql = '''
            SELECT
                distinct
                LOWER( table_target_name ) AS table_target_name,
                lower( target_column_name ) AS target_column_name,
                lower(source_table_name) as source_table_name,
                lower( source_column_name ) AS source_column_name 
            FROM
                `dasset_columns_blood` 
            WHERE
                table_target_name = '{1}' and source_table_name = '{0}'  and `source_column_name` !=""
        '''.format(table_name, item['target_table_name'])
        sub_result = db.select(sql)
        data['influence_table_columns'][
            item['target_table_name']] = sub_result.copy()

    return jsonify(data)


# 展示数据地图的json
@restful.route("/restful/map/all/")
def system_map():
    data = {}
    sql = '''
        Select * From `dasset_system_names`
    '''
    systems = db.select(sql)
    data['systems'] = {}
    for item in systems:
        sql = '''
            SELECT * FROM `dasset_tables` where table_schema like "%{0}" limit 5
        '''.format(item['name'])
        tables = db.select(sql)
        data['systems'][item['name']] = tables.copy()

    sql = '''Select * From `dasset_models`'''
    cim = db.select(sql)
    data['cim'] = {}
    for item in cim:
        sql = '''
            Select distinct theme_name_lv2 From `dasset_themes_lv2` where theme_id={0}
        '''.format(item['id'])
        sub_cim = db.select(sql)
        data['cim'][item['simple_name']] = {}
        for sub in sub_cim:
            sql = '''
                select * From `dasset_themes_lv2` where `theme_id`={0} And theme_name_lv2='{1}' Limit 5
            '''.format(item['id'], sub['theme_name_lv2'])
            tables = db.select(sql)
            data['cim'][item['simple_name']][
                sub['theme_name_lv2']] = tables.copy()

    sql = '''
        Select * From `dasset_schema_connections`
    '''
    connections = db.select(sql)
    data['connections'] = connections
    return jsonify(data)
