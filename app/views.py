from flask import Blueprint, render_template, request, session, Response, jsonify
from . import models
import json
from .ext import is_login
import os
import time
import re

controller = Blueprint('controller', __name__)


@controller.route("/")
@controller.route("/resources/")
@is_login
def resources():
    query_type = request.args.get("query_type", "source_system")
    model = models.QywTables()
    page = request.args.get("page", 1)
    page = int(page)
    tab = request.args.get("tab", 'profile')
    status = {}
    if page < 1:
        page = 1
    if query_type == "source_system":
        menu = model.get_menu_source_system()
        source_system = request.args.get("source_system",
                                         menu[0]['source_system'])
        tables = model.get_tables_by_system(source_system)
        status['source_system'] = source_system
    elif query_type == 'operation':
        menu = model.get_menu_by_operation()
        lv1 = request.args.get("lv1", menu[0]['lv_1_operation'])
        menu_lv2 = model.lv_2_operation(lv1)
        lv2 = request.args.get("lv2", menu_lv2[0]['lv_2_operation'])
        menu_lv3 = model.lv_3_operation(lv1, lv2)
        lv3 = request.args.get("lv3", menu_lv3[0]['lv_3_operation'])
        status = {'lv1': lv1, 'lv2': lv2, 'lv3': lv3}
        menu_operation = {'lv1': [], 'lv2': [], 'lv3': []}
        for k in menu:
            if k['lv_1_operation'] not in menu_operation['lv1']:
                menu_operation['lv1'].append(k['lv_1_operation'])
            if k['lv_2_operation'] not in menu_operation['lv2'] and k[
                    'lv_1_operation'] == lv1:
                menu_operation['lv2'].append(k['lv_2_operation'])
            if k['lv_3_operation'] not in menu_operation['lv3'] and k[
                    'lv_1_operation'] == lv1 and k['lv_2_operation'] == lv2:
                menu_operation['lv3'].append(k['lv_3_operation'])
        menu = json.dumps(menu_operation)
        tables = model.get_tables_by_operation(lv1, lv2, lv3)
    elif query_type == 'process':
        menu = model.get_menu_by_process()
        lv1 = request.args.get("lv1", menu[0]['lv_1_operation'])
        menu_lv2 = model.link_name(lv1)
        lv2 = request.args.get("lv2", menu_lv2[0]['lv_2_operation'])
        menu_lv3 = model.business_info(lv1, lv2)
        lv3 = request.args.get("lv3", menu_lv3[0]['lv_3_operation'])
        status = {'lv1': lv1, 'lv2': lv2, 'lv3': lv3}
        menu_operation = {'lv1': [], 'lv2': [], 'lv3': []}
        for k in menu:
            if k['lv_1_operation'] not in menu_operation['lv1']:
                menu_operation['lv1'].append(k['lv_1_operation'])
            if k['lv_2_operation'] not in menu_operation['lv2'] and k[
                    'lv_1_operation'] == lv1:
                menu_operation['lv2'].append(k['lv_2_operation'])
            if k['lv_3_operation'] not in menu_operation['lv3'] and k[
                    'lv_1_operation'] == lv1 and k['lv_2_operation'] == lv2:
                menu_operation['lv3'].append(k['lv_3_operation'])
        menu = json.dumps(menu_operation)
        tables = model.get_tables_by_process(lv1, lv2, lv3)
    try:
        left_menu_systems = model.get_left_menu_system()
        left_menu_operation = model.get_left_menu_operation()
    except:
        left_menu_systems = [[],[],[]]
        left_menu_operation =  [[],[],[]]
    count = int((len(tables) - 1) // 12) + 1
    if page > count:
        page = count
    start = (page - 1) * 12
    end = start + 12
    show_tables = tables[start:end]
    return render_template("index/resources/resources.html",
                           title="数据资源",
                           query_type=query_type,
                           status=status,
                           page=page,
                           count=count,
                           tables=show_tables,
                           menu=menu,
                           tab=tab,
                           left_menu_systems=left_menu_systems,
                           left_menu_operation=left_menu_operation)


@controller.route("/cim/")
@is_login
def cim():
    cim_id_lv1 = request.args.get("cim_id_lv1", "1")
    page = request.args.get("page", "1")
    page = int(page)
    if page <= 0:
        page = 1
    theme = models.Themes()
    cim_lv1_list, cim_lv2_list = theme.themes(cim_id_lv1)
    # print(tables)

    cim_id_lv2 = request.args.get("cim_id_lv2",
                                  cim_lv2_list[0]['theme_name_lv2'])
    tables, count = theme.tables(cim_id_lv1, cim_id_lv2, page)
    count = int((count - 1) / 12) + 1
    if page > count:
        page = count
    tables, count = theme.tables(cim_id_lv1, cim_id_lv2, page)
    count = int((count - 1) / 12) + 1
    return render_template("index/cim/cim.html",
                           title="SG-CIM",
                           cim_lv1_list=cim_lv1_list,
                           cim_lv2_list=cim_lv2_list,
                           tables=tables,
                           cim_id_lv1=cim_id_lv1,
                           cim_id_lv2=cim_id_lv2,
                           count=count,
                           page=page)


@controller.route("/bi/")
@is_login
def bi():
    model = models.Reports()
    major_list = model.majors()
    major = request.args.get("major", major_list[0]['major'])
    reports = model.reports(major)
    return render_template("index/service/bi.html",
                           title="BI报表",
                           major=major,
                           major_list=major_list,
                           reports=reports)


@controller.route("/assets/")
@is_login
def asset():
    asset_name = request.args.get("name", "all")
    dbname = ""
    assets = models.Asset()
    result = assets.systems()
    if asset_name == 'all':
        dbname = result[0]['TABLE_SCHEMA']
    else:
        dbname = asset_name
    tables = assets.tables(dbname)
    systems = [{
        'sys_desc': item['TABLE_SCHEMA'].split("_")[1],
        'sys_name': item['TABLE_SCHEMA']
    } for item in result]
    remain_systems = []
    for item in systems:
        k = assets.system_maps(item['sys_desc'])
        if k is not None:
            item['sys_chineses'] = k
            remain_systems.append(item.copy())
    # print(remain_systems)
    return render_template("index/assets/assets.html",
                           title="数据资产",
                           class_id='nav-assets',
                           result=result,
                           tables=tables,
                           asset=dbname,
                           systems=remain_systems)


@controller.route("/assets_tree/")
@is_login
def assets_tree():
    return render_template("index/assets/assets_tree.html",
                           title="数据资源结构",
                           class_id='nav-assets')


@controller.route("/index/")
@is_login
def index():
    service = models.IndexShow()
    sqls = service.selectSql()
    tables = service.selectDatatable()
    apis = service.selectDataAPI()
    return render_template('index/main/index.html',
                           title='数据门户',
                           class_id="nav-home",
                           sqls=sqls,
                           tables=tables,
                           apis=apis)


@controller.route("/search/", methods=['GET'])
@is_login
def search():
    keyword = request.args.get("keyword")
    page = int(request.args.get('page', '1'))
    if page < 1:
        page = 1
    print(keyword)
    search = models.Search()
    cnt = search.count(keyword)
    if cnt == 0:
        page = 1
    elif page > ((cnt - 1) // 10) + 1:
        page = ((cnt - 1) // 10) + 1
    result = search.search(keyword, page)
    data = {'page': page, 'keyword': keyword, 'cnt': cnt, 'data': result}

    # search_picture
    resultPic = search.search_picture(keyword)
    cntp = len(resultPic)
    dataPic = {'keyword': keyword, 'cnt': cntp, 'dataP': resultPic}

    return render_template('index/search/search.html',
                           title='所搜结果',
                           result=data,
                           result2=dataPic)


@controller.route("/tables/<schema>/<table>/")
@is_login
def tables(schema, table):
    table_id = request.args.get('id')
    model = models.Tables()
    if table_id:
        data = model.get_schema_and_table_by_id(table_id)
        if len(data) > 0:
            schema = data[0]['table_schema']
            table = data[0]['table_name']
    result_columns = model.tables(schema, table)
    if len(result_columns) == 0:
        result_columns = model.get_blur_tables(schema, table)
    # print(result)
    if len(result_columns) == 0:
        result_columns = [{
            "TABLE_SCHEMA": schema,
            "TABLE_NAME": table,
            "id": 1
        }]
    table_id = result_columns[0].get('table_id')
    result_table = model.table_info(schema, table)
    result_bloods = model.table_column_bloods(table)
    result_influences = model.table_column_influence(table)
    result_connections = model.table_connections(table)
    try:
        print('table_id', table_id)
        result_process = model.table_process(table_id)[0]
        print(result_process)
    except:
        result_process = {}
    if result_table['columns']:
        result_comment = re.split(
            r"\d）",
            result_table['col_info']['table_comment'].replace(")", "）"))
    else:
        result_comment = ""
    table_data = model.table_data(schema, table)
    return render_template('index/tables/tables.html',
                           title='数据表详情',
                           class_id="nav-home",
                           result_columns=result_columns,
                           result_table=result_table,
                           result_bloods=result_bloods,
                           result_influences=result_influences,
                           result_connections=result_connections,
                           table_comment=result_comment,
                           table_data=table_data,
                           table_process=result_process)


@controller.route("/apply/")
@is_login
def apply():
    db_name = request.args.get("db")
    table_name = request.args.get("table")
    table = models.Tables()
    result = table.table_info(db_name, table_name)
    return render_template("index/apply/apply.html",
                           title="使用申请",
                           db_name=db_name,
                           table_name=table_name,
                           result=result)


@controller.route(
    "/apply_qyw_table/<lv1>/<lv2>/<lv3>/<process_name>/<link_name>/<business_info>/<table_name_en>/"
)
@is_login
def apply_qyw_table(lv1, lv2, lv3, process_name, link_name, business_info,
                    table_name_en):
    theme = models.Themes()
    result = theme.table_info(lv1, lv2, lv3, process_name, link_name,
                              business_info, table_name_en)
    return render_template("index/apply/apply_qyw_table.html",
                           title="使用申请",
                           result=result[0])


@controller.route("/systems_menu/")
@is_login
def systems_menu():
    lv1 = request.args.get("lv1", "设备运检")
    lv2 = request.args.get("lv2", "设备技术管理")
    lv3 = request.args.get("lv3")
    process_name = request.args.get("process_name")
    page = request.args.get("page", "1")
    page = int(page)
    theme = models.Themes()

    # 当前状态数据
    status = {'lv1': lv1, 'lv2': lv2, 'lv3': lv3, 'process_name': process_name}

    # 展示数据
    lv_1_menu = theme.lv_1_operation()
    lv_2_menu = theme.lv_2_operation(lv1)
    lv_3_menu = theme.lv_3_operation(lv1, lv2)
    process = theme.process(lv1, lv2, lv3)
    tables = theme.qyw_tables(lv1, lv2, lv3, process_name)
    menu = {
        'lv1': lv_1_menu,
        'lv2': lv_2_menu,
        'lv3': lv_3_menu,
        'process': process,
        'tables': tables
    }
    # print(tables)
    return render_template("index/assets/systems_menu.html",
                           title="数据资源",
                           class_id='nav-assets',
                           status=status,
                           menu=menu)


@controller.route(
    "/process_table_column/<lv1>/<lv2>/<lv3>/<process_name>/<link_name>/<business_info>/<table_name_en>/"
)
@is_login
def process_table_column(lv1, lv2, lv3, process_name, link_name, business_info,
                         table_name_en):
    # menu_table = request.args.get("menu_table")
    # print(process_name)
    theme = models.Themes()
    result, table, influences, columns, table_data, connections, bloods = theme.table_info(
        lv1, lv2, lv3, process_name, link_name, business_info, table_name_en)
    if len(result) == 0:
        result = [{"process_name": "此表无数据", "table_name_ch": "不存在"}]
    return render_template("index/tables/qyw_tables.html",
                           title="数据资源表详情",
                           result=result,
                           table=table,
                           influences=influences,
                           bloods=bloods,
                           columns=columns,
                           table_data=table_data,
                           connections=connections)


@controller.route("/news/")
@is_login
def news():
    return render_template("index/news/news.html",
                           title="新闻",
                           class_id='nav-news')


@controller.route("/service/")
@is_login
def data_service():
    business_system = request.args.get("business_system", "营销系统")
    major = request.args.get("major", "收费账务")
    model = models.SQLs()
    level1 = model.level1()
    level2 = model.level2(business_system)
    sql = model.sqls(business_system, major)
    model = models.Services()
    icons = model.get_bootstrap_icons()
    return render_template('index/service/service.html',
                           title='数据服务',
                           icons=icons,
                           business_system=business_system,
                           major=major,
                           level1=level1,
                           level2=level2,
                           sql=sql)


@controller.route("/sqls/")
@is_login
def sqls():
    business_system = request.args.get("business_system", "营销系统")
    major = request.args.get("major", "收费账务")
    model = models.SQLs()
    level1 = model.level1()
    level2 = model.level2(business_system)
    sql = model.sqls(business_system, major)
    return render_template("index/service/sqls.html",
                           title="常用SQL",
                           class_id='nav-service',
                           business_system=business_system,
                           major=major,
                           level1=level1,
                           level2=level2,
                           sql=sql)


@controller.route("/login/")
def login():
    data = request.cookies
    print(data)

    return render_template("main/login.html")


@controller.route("/login/clear/")
def session_clear():
    session.clear()
    return "清除成功！"


@controller.route('/getCookie')
def get_cookie():
    cookie = request.cookies
    # user_name = request.cookies.get("user_name")
    # print(session.items())
    data = {'cookie': cookie, 'session': str(session.items())}
    session.clear()
    return jsonify(data)


@controller.route('/apply_api/')
@is_login
def apply_api():
    api_name = request.args.get("api_name")
    # table_name = request.args.get("table")
    # table = models.Tables()
    # result = table.table_info(db_name, table_name)
    return render_template("index/apply/apply_api.html",
                           title="使用申请",
                           api_name=api_name)


@controller.route('/apply_sql/')
@is_login
def apply_sql():
    id = request.args.get("id")
    model = models.SQLs()
    sql = model.get_sql_by_id(id)
    return render_template("index/apply/apply_sql.html",
                           title="使用申请",
                           id=id,
                           sql=sql[0])


@controller.route("/systems_tree/")
@is_login
def systems_tree():
    return render_template(
        "index/assets/systems_tree.html",
        title="数据资源结构",
    )


@controller.route("/test/")
def test():
    with open('app/static/test.txt') as f:
        a = f.read()
    a = os.path.abspath(__file__)
    return a


@controller.route('/datatable/')
@is_login
def datatable():
    return render_template("index/service/datatable.html")


@controller.route("/api/")
@is_login
def data_api():
    api = models.DataApi()
    page = request.args.get("page", "1")
    page = int(page)
    if page <= 0:
        page = 1
    api_type_list = api.api_type_list()
    api_type = request.args.get("api_type", api_type_list[0]['type'])
    apis, count = api.apis(api_type)
    count = int(count / 12) + 1
    if page > count:
        page = count
    return render_template('index/service/api.html',
                           title='Data API',
                           api_type_list=api_type_list,
                           api_type=api_type,
                           apis=apis,
                           page=page,
                           count=count)


@controller.route("/sql/")
@is_login
def data_sql():
    business_system = request.args.get("business_system", "营销系统")
    major = request.args.get("major", "收费账务")
    model = models.SQLs()
    level1 = model.level1()
    level2 = model.level2(business_system)
    sql = model.sqls(business_system, major)
    model = models.Services()
    # icons = model.get_bootstrap_icons()
    return render_template(
        'index/service/sql.html',
        title='SQL',
        # icons=icons,
        business_system=business_system,
        major=major,
        level1=level1,
        level2=level2,
        sql=sql)


@controller.route("/api_detail/")
def dataDetail():
    api_id = request.args.get("id")
    model = models.DataApi()
    api_detail = model.api_detail(api_id)[0]
    return render_template(
        'index/service/api_detail.html',
        title='Data API详情',
        api_detail=api_detail,
    )


@controller.route("/api_shopcar/")
def apiShopCar():
    return render_template('index/service/api_apply.html')


@controller.route("/api/updateinfo/<api_id>/")
def apiInfo(api_id):
    data = {}
    # 把json转换成字典
    data = json.loads(request.args.get("data"))
    # 判断为空么
    if data is None:
        return "40"
    print(data)
    user_id = session['user_id']['user_id']
    service = models.DataApi()
    result = service.updateApplyApi(data, user_id, api_id)
    return result


@controller.route("/shopcar/")
@is_login
def shopcar():
    return render_template("index/tables/shopcar.html", title="数据使用申请")


@controller.route("/test/map/<schema>/<table>/")
def map_test(schema, table):
    return render_template("index/tables/test.html",
                           schema=schema,
                           table=table)


@controller.route("/collect/")
def my_collect():
    user_id = session['user_id']['user_id']
    service = models.Collect()
    tables = service.select_all_collect("dasset_tables", user_id)
    apis = service.select_all_collect("dasset_apis", user_id)
    sqls = service.select_all_collect("usually_sqls", user_id)
    return render_template("index/service/collect.html",
                           tables=tables,
                           apis=apis,
                           sqls=sqls)


@controller.route("/norm/")
@is_login
def norm():
    model_name = request.args.get("model_name", "all")
    model = models.Standard()
    codes = model.standard_code(model_name)
    menu = model.get_menu()
    status = {'menu_select': model_name}
    return render_template("index/norm/norm.html",
                           title="规范代码一览",
                           codes=codes,
                           menu=menu,
                           status=status)


@controller.route("/norm/norm_tables/")
@is_login
def norm_tables():
    column_name = request.args.get("column_name", "isOpen")
    model = models.Standard()
    tables = model.get_belong_tables_by_column(column_name)
    return render_template(
        "index/norm/norm_tables.html",
        title="数据规范",
        tables=tables,
    )


@controller.route("/govern/")
@is_login
def govern():
    model = models.Govern()
    rules = model.get_govern_rules()
    return render_template("index/govern/govern.html",
                           title='数据治理',
                           rules=rules)


@controller.route("/through/")
@is_login
def through():
    model = models.Through()
    menu = model.get_menu()
    process_name = request.args.get("process", menu[0]['process_name'])
    process_tables = model.get_tables_by_process(process_name)
    image = model.get_image_url_by_process(process_name)
    return render_template("index/through/through.html",
                           title='营配贯通',
                           menu=menu,
                           process_tables=process_tables,
                           status=process_name,
                           image=image[0])
