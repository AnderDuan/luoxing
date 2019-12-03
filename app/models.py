# -*- coding:utf-8 -*-

from .db import MySqlClass
from .config import CONFIG
import sqlalchemy
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import time

db = MySqlClass(CONFIG.MYSQL['host'], CONFIG.MYSQL['port'],
                CONFIG.MYSQL['user'], CONFIG.MYSQL['password'],
                CONFIG.MYSQL['database'])

source_db = {}

# source_db = {
#     'sgrdb':
#     MySqlClass(CONFIG.SGRDB['host'],
#                CONFIG.SGRDB['port'],
#                CONFIG.SGRDB['user'],
#                CONFIG.SGRDB['password'],
#                CONFIG.SGRDB['database'],
#                pool_size=5),
#     'gbase':
#     MySqlClass(CONFIG.GBASE['host'],
#                CONFIG.GBASE['port'],
#                CONFIG.GBASE['user'],
#                CONFIG.GBASE['password'],
#                CONFIG.GBASE['database'],
#                pool_size=5)
# }


class Search(object):
    def __init__(self):
        pass

    def search(self, keyword, page):
        sql = '''Select * From 
                (Select *
                From `dasset_tables`
                where table_name = '{0}'
                Union
                Select *
                From `dasset_tables`
                where TABLE_COMMENT like '%{0}%' or table_name like '%{0}%'
                Limit {1},10) t1 
                LEFT JOIN dasset_system_names t2 
                on t1.`TABLE_SCHEMA` like CONCAT("%",t2.`name`)
                '''.format(keyword, (page - 1) * 10)
        print(sql)
        result = db.select(sql)
        return result

    def search_picture(self, keyword):
        sql = '''Select *
                From `url_team`
                where tb_name like '%{0}%'
                '''.format(keyword)
        result = db.select(sql)
        return result

    def count(self, keyword):
        sql = '''Select Count(*) as cnt From `dasset_tables` 
            where TABLE_COMMENT like '%{0}%' or table_name like '%{0}%'
            order by update_time desc Limit 10;
        '''.format(keyword)
        result = db.select(sql)[0]['cnt']
        return result


class Asset(object):
    def __init__(self):
        pass

    def systems(self):
        sql = '''select DISTINCT TABLE_SCHEMA from `dasset_tables`'''
        result = db.select(sql)
        return result

    def tables(self, dbname):
        sql = '''Select *,format(RAND()*100,0) as down,format(RAND()*100,0) as seen
                From `dasset_tables` Where TABLE_SCHEMA='{0}' 
                Order By UPDATE_TIME desc limit 50
                '''.format(dbname)
        result = db.select(sql)
        return result

    def system_maps(self, sys_name):
        sql = "select * from `dasset_system_names` where name = '{0}'".format(
            sys_name)
        result = db.select(sql)
        if result:
            return result[0]['system']
        else:
            return None


class Tables(object):
    def __init__(self):
        pass

    def get_schema_and_table_by_id(self, table_id):
        sql = '''
            Select * From `dasset_tables` Where id ={0}
        '''.format(table_id)
        result = db.select(sql)
        return result

    def tables(self, schema, table):
        sql = "Select * From `dasset_columns` Where TABLE_SCHEMA='{0}' and TABLE_NAME='{1}'".format(
            schema, table)
        # print(sql)
        result = db.select(sql)
        return result

    def get_blur_tables(self, schema, table):
        sql = '''
            SELECT * FROM `dasset_columns` where table_name='{0}' and table_schema like '%{1}%'
        '''.format(table, schema)
        result = db.select(sql)
        return result

    def table_info(self, schema, table):
        sql = '''
                Select Count(*) as col_num From `dasset_columns`  Where TABLE_SCHEMA='{0}' and TABLE_NAME='{1}'
            '''.format(schema, table)
        result1 = db.select(sql)
        if len(result1) == 0:
            sql = '''
                Select Count(*) as col_num From `dasset_columns`  Where TABLE_SCHEMA like '%{0}%' and TABLE_NAME='{1}'
            '''.format(schema, table)
            result1 = db.select(sql)
        sql = '''
            Select t1.*,CURDATE() as date,t2.system
            From `dasset_tables` t1 left join `dasset_system_names` t2 on t1.table_schema=t2.table_schema
            Where t1.TABLE_SCHEMA='{0}' and t1.TABLE_NAME='{1}'
        '''.format(schema, table)
        result2 = db.select(sql)
        if len(result2) == 0:
            sql = '''
                Select t1.*,CURDATE() as date,t2.system
                From `dasset_tables` t1 left join `dasset_system_names` t2 on t1.table_schema=t2.table_schema
                Where t1.TABLE_SCHEMA like '%{0}%' and t1.TABLE_NAME='{1}'
            '''.format(schema, table)
            # print(sql)
            result2 = db.select(sql)
        result = {}
        result['col_num'] = result1[0]
        if len(result2) != 0:
            result['col_info'] = result2[0]
        result['columns'] = self.get_blur_tables(schema, table)
        return result

    def table_column_bloods(self, table):
        sql = '''
            SELECT * FROM `dasset_columns_blood` where table_target_name='{0}'
        '''.format(table)
        result = db.select(sql)
        return result

    def table_column_influence(self, table):
        sql = '''
            SELECT * FROM `dasset_columns_blood` where source_table_name='{0}'
        '''.format(table)
        result = db.select(sql)
        return result

    def table_connections(self, table):
        sql = '''
            SELECT * FROM `dasset_tables_connections` where main_table_name='{0}' or relate_table_name='{0}'
        '''.format(table)
        result = db.select(sql)
        return result

    def table_data(self, schema, table):
        if source_db:
            sql = '''
                Select * From `{0}`.`{1}` Limit 100
            '''.format(schema, table)
            try:
                if schema == 'qy_190215':
                    result = source_db['gbase'].select(sql,
                                                       source_type='gbase')
                else:
                    result = source_db['sgrdb'].select(sql)
                return result
            except:
                return []
        else:
            return []

    def table_process(self, table_id):
        sql = '''
            Select * From `qyw_data_assets_check` Where `table_id`={0}
        '''.format(table_id)
        result = db.select(sql)
        return result


class Themes(object):
    def __init__(self):
        pass

    def themes(self, cim_id_lv1):
        sql = "select * from `dasset_models` order by id"
        cim_lv1_list = db.select(sql)
        sql = '''
            SELECT distinct theme_id,theme_name,theme_name_lv2 
            FROM `dasset_themes_lv2` where theme_id={0}
        '''.format(cim_id_lv1)
        cim_lv2_list = db.select(sql)
        return cim_lv1_list, cim_lv2_list

    def tables(self, cim_id_lv1, cim_id_lv2, page):
        limit = (page - 1) * 12
        sql = '''Select *,format(RAND()*4+1,0) as down,format(RAND()*4+1,0) as seen
                From `dasset_themes_lv2` Where theme_id={0} and theme_name_lv2='{1}'
                LIMIT {2}, 12
        '''.format(cim_id_lv1, cim_id_lv2, limit)
        result = db.select(sql)
        sql = '''Select count(*) as cnt
            From `dasset_themes_lv2` Where theme_id={0} and theme_name_lv2='{1}'
        '''.format(cim_id_lv1, cim_id_lv2)
        count = db.select(sql)[0]['cnt']
        return result, count

    def assetsCheck(self, model_id):
        sql = '''Select *,format(RAND()*100,0) as down,format(RAND()*100,0) as seen
                From `qyw_data_assets_check` Where model_id='{0}' 
                Order By UPDATE_TIME desc 
                LIMIT 10
                '''.format(model_id)
        result = db.select(sql)
        return result

    def systems(self):
        sql = '''
            SELECT
                source_system,
                count(DISTINCT table_name_en) AS num
            FROM
                `qyw_data_assets_check`
            GROUP BY
                source_system
            HAVING
                source_system != ''
            order by 
                num DESC
        '''
        result = db.select(sql)
        return result

    # def process(self, system_name):
    #     sql = '''
    #         Select Distinct process_name from `qyw_data_assets_check` where `source_system`='{0}' and `process_name` !=''
    #     '''.format(system_name)
    #     result = db.select(sql)
    #     return result

    def qyw_tables(self, lv_1_operation, lv_2_operation, lv_3_operation,
                   process_name):
        sql = '''
            SELECT
                source_system,
                table_name_ch,
                table_name_en,
                lv_1_operation,
                lv_2_operation,
                lv_3_operation,
                link_name,
                business_info,
                count(*) AS col_num
            FROM
                `qyw_data_assets_check`
            WHERE
                lv_1_operation = '{0}'
            AND lv_2_operation = '{1}'
            AND lv_3_operation = '{2}'
            AND process_name = '{3}'
            and table_name_en!=''
            GROUP BY
                source_system,
                table_name_ch,
                table_name_en,
                lv_1_operation,
                lv_2_operation,
                lv_3_operation,
                link_name,
                business_info
        '''.format(lv_1_operation, lv_2_operation, lv_3_operation,
                   process_name)
        result = db.select(sql)
        # print(sql)
        return result

    def table_info(self, lv1, lv2, lv3, process_name, link_name, business_info,
                   table_name_en):
        sql = '''
                SELECT
                    *
                FROM
                    `qyw_data_assets_check`
                WHERE
                    lv_1_operation ='{0}' and lv_2_operation='{1}' and lv_3_operation ='{2}' 
                    And table_name_en = '{3}' and process_name='{4}' and link_name='{5}'
                    And business_info='{6}'
        '''.format(lv1, lv2, lv3, table_name_en, process_name, link_name,
                   business_info)
        result = db.select(sql)

        if len(result) != 0:
            table_id = result[0]['table_id']
            sql = '''
                Select * from `dasset_tables` Where id={0}
            '''.format(table_id)
            table = db.select(sql)
            sql = '''
                Select * From `dasset_columns` Where table_id={0}
            '''.format(table_id)
            columns = db.select(sql)
            # return result, table
        else:
            table = [{}]
            columns = []

        sql = '''
            Select * From `dasset_columns_blood` Where source_table_name='{0}'
        '''.format(table_name_en)
        influences = db.select(sql)

        sql = '''
            Select * From `dasset_columns_blood` Where table_target_name='{0}'
        '''.format(table_name_en)
        bloods = db.select(sql)

        table_schema = table[0]['table_schema']
        table_name = table[0]['table_name']

        sql = '''
            Select * From `{0}`.`{1}` Limit 100
        '''.format(table_schema, table_name)
        if source_db:
            table_data = source_db['sgrdb'].select(sql)
        else:
            table_data = []

        sql = '''
                SELECT * FROM `dasset_tables_connections`
                where main_table_name='{0}' or relate_table_name='{0}'
        '''.format(table_name)
        connections = db.select(sql)

        return result, table[
            0], influences, columns, table_data, connections, bloods

    def lv_1_operation(self):
        sql = '''
            Select DISTINCT lv_1_operation From `qyw_data_assets_check` 
        '''
        result = db.select(sql)
        return result

    def lv_2_operation(self, lv_1_operation):
        sql = '''
            SELECT DISTINCT lv_2_operation FROM `qyw_data_assets_check`  where lv_1_operation='{0}'
        '''.format(lv_1_operation)
        result = db.select(sql)
        return result

    def lv_3_operation(self, lv_1_operation, lv_2_operation):
        sql = '''
            SELECT DISTINCT lv_3_operation FROM `qyw_data_assets_check`  where lv_1_operation='{0}' and lv_2_operation = '{1}'
        '''.format(lv_1_operation, lv_2_operation)
        result = db.select(sql)
        return result

    def process(self, lv_1_operation, lv_2_operation, lv_3_operation):
        sql = '''
            SELECT DISTINCT
                process_name
            FROM
                `qyw_data_assets_check` 
            WHERE
                lv_1_operation = '{0}' 
                AND lv_2_operation = '{1}'
                and lv_3_operation = '{2}'
        '''.format(lv_1_operation, lv_2_operation, lv_3_operation)
        result = db.select(sql)
        return result


class SQLs(object):
    def level1(self):
        sql = '''
            Select Distinct `business_system` From `usually_sqls`
        '''
        result_lv1 = db.select(sql)
        return result_lv1

    def level2(self, level1):
        sql = '''
            Select Distinct major from `usually_sqls` where `business_system`='{0}'
        '''.format(level1)
        result_lv2 = db.select(sql)
        return result_lv2

    def sqls(self, level1, level2):
        sql = '''
            Select * From `usually_sqls` where `business_system`='{0}' and major = '{1}'
        '''.format(level1, level2)
        result_sqls = db.select(sql)
        return result_sqls

    def get_sql_by_id(self, id):
        sql = '''
            Select * From `usually_sqls` Where id={0}
        '''.format(id)
        return db.select(sql)


class Services(object):
    def __init__(self):
        pass

    def get_bootstrap_icons(self):
        sql = '''
            Select * From `bootstrap_icons` 
        '''
        result = db.select(sql)
        return result


class UserLogin(object):
    def login(self, user_id, password):
        sql = '''
            SELECT
                t1.user_id,t1.user_name,t2.role_id,t3.role_name
            FROM
                `user_info` t1
                LEFT JOIN `user_role` t2 ON t1.user_id = t2.user_id
                left join `role` t3 on t2.role_id = t3.id
            WHERE t1.user_id='{0}' and t1.passwd='{1}'
        '''.format(user_id, password)
        result = db.select(sql)
        return result

    def logout(self):
        pass


class Apply(object):
    def __init__(self, table_name):
        self.__table__ = table_name

    def add(self, new_apply):
        db.insert_dic(new_apply, self.__table__)

    def delete(self, id):
        db.delete("delete from `{0}` Where `id`={1}".format(
            self.__table__, id))


class DbModel(object):
    def __init__(self, table_name):
        self.__table__ = table_name

    def select(self, where="", skip="", limit=""):
        sql = '''
            Select * From `{0}`
        '''.format(self.__table__)
        if where:
            sql += ''' Where {0} '''.format(where)

        if skip:
            if limit:
                sql += ''' Limit {0},{1}'''.format(skip, limit)
        elif limit:
            sql += ''' Limit {0}'''.format(limit)

        result = db.select(sql)
        for item in result:
            for key in item:
                # print(key, item[key], type(item[key]))
                if str(type(item[key])) == "<class 'datetime.date'>" or str(
                        type(item[key])) == "<class 'datetime.datetime'>":
                    item[key] = str(item[key])

        return result

    def update(self, dic_data):
        db.insert_dic(dic_data, self.__table__, replace=True)

    def insert(self, dic_data):
        db.insert_dic(dic_data, self.__table__)

    def delete(self, id):
        sql = '''
            Delete from {0} Where `id`={1}
        '''.format(self.__table__, id)
        db.delete(sql)

    def deletes(self, ids):
        # delete_ids = ids.split(",")
        for id in ids:
            self.delete(id)

    def count(self):
        sql = '''
                Select count(*) as cnt from {0} 
                '''.format(self.__table__)
        result = db.select(sql)[0]['cnt']
        return result


# 购物车信息的类
class ShopCar(object):
    # 查找状态为0的数据根据用户id如果有数据返回集合 没有数据返回40
    def find_status_by_uid(self, user_id):
        sql = '''
            select * from `dasset_apply_order` where `user_id`='{0}' and `status`='000'
        '''.format(user_id)
        result = db.select(sql)
        return result

    def is_table_exists_in_order_detail(self, order_id, table_id, table_name):
        sql = '''
            Select * From dasset_apply_order_detail
            Where order_id='{0}' and table_id='{1}' and table_name='{2}' and is_delete=0
        '''.format(order_id, table_id, table_name)
        result = db.select(sql)
        if len(result) == 0:
            return False
        else:
            return True

    # 保存一条order信息
    def save_order(self, data):
        current_order = self.find_status_by_uid(data['user_id'])
        detail_data = {}
        save_order = {}
        detail_data['table_id'] = data['table_id']
        detail_data['table_name'] = data['table_name']
        detail_data['source_system'] = data['source_system']
        if len(current_order) == 0:
            save_order['order_id'] = '{0}__{1}'.format(data['user_id'],
                                                       int(time.time()))
            save_order['order_time'] = str(datetime.now())[:19]
            save_order['user_id'] = data['user_id']
            save_order['status'] = "000"
            db.insert_dic(save_order, "dasset_apply_order")
            detail_data['order_id'] = save_order['order_id']
        else:
            detail_data['order_id'] = current_order[0]['order_id']

        # 判断明细表中是否有table
        if self.is_table_exists_in_order_detail(detail_data['order_id'],
                                                detail_data['table_id'],
                                                detail_data['table_name']):
            return '已经存在'
        else:
            db.insert_dic(detail_data, 'dasset_apply_order_detail')

    # 修改前端提交的订单申请修改order表
    def update_order_info(self, data):
        sql = '''
            Update `dasset_apply_order`
            Set `order_time`='{0}',`approve_uid`='{1}',`status`='{2}',`apply_reason`='{3}',
            `apply_content`='{4}' where order_id='{5}'
        '''.format(data['order_time'], data['approve_uid'], data['status'],
                   data['apply_reason'], data['apply_content'],
                   data['order_id'])
        db.update(sql)
        return "200"

    # 如果订单完成或者删除detail表删完了就把status改成600
    def update_status_order(self, status, userId):
        orderId = self.findOrderByUid(userId)
        sql = '''
            update dasset_apply_order set `status`='{0}' where order_id='{1}'
        '''.format(status, orderId)
        db.update(sql)

    # 批量修改detail表的is_delete
    def deletes(self, ids):
        for id in ids:
            print(id)
            self.delete_detail_item(id)

    # 单个修改is_delete
    def delete_detail_item(self, id):
        sql = '''
                update `dasset_apply_order_detail` set `is_delete`='1' where `id`='{0}'
        '''.format(id)
        db.update(sql)

    # 根基user_id查order表的order_id然后根据order_id查detail的信息
    def find_detail_by_userid(self, user_id):
        sql = '''
            select * from dasset_apply_order_detail where order_id=
            (select order_id from dasset_apply_order where `user_id`='{0}' and `status`='000') 
            and is_delete='0';
        '''.format(user_id)
        result = db.select(sql)
        return result

    # 根据uid来查找转态是0的order
    def findOrderByUid(self, userId):
        sql = '''
            select order_id from dasset_apply_order where `user_id`='{0}' and `status`='0'
        '''.format(userId)
        orderId = db.select(sql)[0]['order_id']
        return orderId

    #    查找有审批权限的人名

    def findApproves(self):
        sql = '''
            select * from user_info where `user_id` in (select `user_id` from user_role where `role_id`=2)
        '''
        approves = db.select(sql)
        return approves


# API信息的类
class DataApi(object):
    def api_type_list(self):
        sql = '''
            Select distinct type From `dasset_apis`
        '''
        result = db.select(sql)
        return result

    # 查找dasset_apis表相对应的数据  因为没有方法重载，只能用逻辑
    def apis(self, api_type):
        sql = '''
            select * from `dasset_apis` where `type`='{0}'
        '''.format(api_type)
        data = db.select(sql)
        count = len(data)
        return data, count

    def api_detail(self, api_id):
        sql = '''
            Select * From dasset_apis where id={0}
        '''.format(api_id)
        result = db.select(sql)
        return result

    # 申请操作
    def updateApplyApi(self, data, user_id, api_id):
        saveData = {}
        saveData['approve_uid'] = data['approve_uid']
        saveData['apply_reason'] = data['apply_reason']
        saveData['api_id'] = api_id
        saveData['apply_uid'] = user_id
        now_time = datetime.now()
        date_str = datetime.strftime(now_time, '%Y-%m-%d %H:%M:%S')
        saveData['apply_time'] = date_str
        saveData['status'] = 100
        try:
            db.insert_dic(saveData, "dasset_apply_apis")
            return "200"
        except Exception as e:
            print(e)
            print("错误了")
            return "40"


# 数据表表相关信息的类
class Reports(object):
    def majors(self):
        sql = '''
            Select distinct major from dasset_reports
        '''
        result = db.select(sql)
        return result

    # 加载全部的数据报表
    def reports(self, major):
        sql = '''
            select * from dasset_reports where major='{0}'
        '''.format(major)
        print(sql)
        result = db.select(sql)
        return result


class QywTables(object):
    def get_all_menu(self):
        sql = '''
            SELECT DISTINCT
                lv_1_operation,
                lv_2_operation,
                lv_3_operation,
                process_name,
                link_name,
                business_info,
                source_system 
            FROM
                qyw_data_assets_check t1
        '''
        result = db.select(sql)
        return result

    # 按照来源系统查询
    def get_menu_source_system(self):
        sql = '''
            SELECT 
                source_system,count(*) as cnt
            FROM
                qyw_data_assets_check t1
            Group BY
                source_system
            ORDER BY
                cnt DESC
        '''
        result = db.select(sql)
        return result

    # 按照业务查询
    def get_menu_by_operation(self):
        sql = '''
            Select
                lv_1_operation,
                lv_2_operation,
                lv_3_operation,
                count(*) as cnt
            FROM
                `qyw_data_assets_check` 
            GROUP BY
                lv_1_operation,
                lv_2_operation,
                lv_3_operation
            ORDER BY
                cnt DESC
        '''
        result = db.select(sql)
        return result

    # 按照流程查询
    def get_menu_by_process(self):
        sql = '''
            SELECT DISTINCT
                process_name as lv_1_operation,
                link_name as lv_2_operation,
                business_info as lv_3_operation
            FROM
                `qyw_data_assets_check` 
        '''
        result = db.select(sql)
        return result

    # 按照业务系统获取数据表
    def get_tables_by_system(self, source_system):
        sql = '''
            SELECT
                lv_1_operation,lv_2_operation,lv_3_operation,
                process_name,link_name,business_info,source_system,
                table_name_en,table_name_ch,table_id,t1.import_level,t2.level_order,
                count( * ) as col_num
            FROM
                `qyw_data_assets_check` t1 left join `dasset_import_level_order` t2 on t1.`import_level` = t2.`import_level`
            WHERE
                source_system = '{0}' and table_name_en!=''
            GROUP BY
                lv_1_operation,lv_2_operation,lv_3_operation,
                process_name,link_name,business_info,source_system,
                table_name_en,table_name_ch,table_id,t1.import_level,t2.level_order
            Order BY
                t2.level_order DESC
        '''.format(source_system)
        result = db.select(sql)
        return result

    # 按照业务等级获取数据表
    def get_tables_by_operation(self, lv_1_operation, lv_2_operation,
                                lv_3_operation):
        sql = '''
            SELECT
                lv_1_operation,lv_2_operation,lv_3_operation,
                process_name,link_name,business_info,source_system,
                table_name_en,table_name_ch,table_id,t1.import_level,t2.level_order,
                count( * ) as col_num
            FROM
                `qyw_data_assets_check` t1 left join `dasset_import_level_order` t2 on t1.`import_level` = t2.`import_level`
            WHERE
                lv_1_operation = '{0}'
            AND lv_2_operation = '{1}'
            AND lv_3_operation = '{2}'
            AND table_name_en!=''
            GROUP BY
                lv_1_operation,lv_2_operation,lv_3_operation,
                process_name,link_name,business_info,source_system,
                table_name_en,table_name_ch,table_id,t1.import_level,t2.level_order
            Order BY
                t2.level_order DESC
        '''.format(lv_1_operation, lv_2_operation, lv_3_operation)
        result = db.select(sql)
        return result

    def get_tables_by_process(self, lv_1_operation, lv_2_operation,
                              lv_3_operation):
        sql = '''
            SELECT
                lv_1_operation,lv_2_operation,lv_3_operation,
                process_name,link_name,business_info,source_system,
                table_name_en,table_name_ch,table_id,t1.import_level,t2.level_order,
                count( * ) as col_num
            FROM
                `qyw_data_assets_check` t1 left join `dasset_import_level_order` t2 on t1.`import_level` = t2.`import_level`
            WHERE
                process_name = '{0}'
            AND link_name = '{1}'
            AND business_info = '{2}'
            AND table_name_en!=''
            GROUP BY
                lv_1_operation,lv_2_operation,lv_3_operation,
                process_name,link_name,business_info,source_system,
                table_name_en,table_name_ch,table_id,t1.import_level,t2.level_order
            Order BY
                t2.level_order DESC
        '''.format(lv_1_operation, lv_2_operation, lv_3_operation)
        result = db.select(sql)
        return result

    def table_info(self, lv1, lv2, lv3, process_name, link_name, business_info,
                   table_name_en):
        sql = '''
                SELECT *
                FROM
                    `qyw_data_assets_check`
                WHERE
                    lv_1_operation ='{0}' and lv_2_operation='{1}' and lv_3_operation ='{2}' 
                    And table_name_en = '{3}' and process_name='{4}' and link_name='{5}'
                    And business_info='{6}'
        '''.format(lv1, lv2, lv3, table_name_en, process_name, link_name,
                   business_info)
        result = db.select(sql)
        print(sql)
        return result

    def lv_1_operation(self):
        sql = '''
            Select DISTINCT lv_1_operation From `qyw_data_assets_check` 
        '''
        result = db.select(sql)
        return result

    def lv_2_operation(self, lv_1_operation):
        sql = '''
            SELECT DISTINCT lv_2_operation FROM `qyw_data_assets_check`  where lv_1_operation='{0}'
        '''.format(lv_1_operation)
        result = db.select(sql)
        return result

    def lv_3_operation(self, lv_1_operation, lv_2_operation):
        sql = '''
            SELECT DISTINCT lv_3_operation FROM `qyw_data_assets_check`  where lv_1_operation='{0}' and lv_2_operation = '{1}'
        '''.format(lv_1_operation, lv_2_operation)
        result = db.select(sql)
        return result

    #  以下三个方法用于动态表头
    def process_name(self):
        sql = '''
            Select DISTINCT process_name as lv_1_operation From `qyw_data_assets_check` 
        '''
        result = db.select(sql)
        return result

    def link_name(self, process_name):
        sql = '''
            SELECT DISTINCT link_name as lv_2_operation 
            FROM `qyw_data_assets_check`  where process_name='{0}'
        '''.format(process_name)
        result = db.select(sql)
        return result

    def business_info(self, process_name, link_name):
        sql = '''
            SELECT DISTINCT business_info as lv_3_operation
            FROM `qyw_data_assets_check`  where process_name='{0}' and link_name = '{1}'
        '''.format(process_name, link_name)
        result = db.select(sql)
        return result

    # 以下方法用于动态显示左侧导航栏
    def get_left_menu_system(self):
        return self.get_menu_source_system()[0:3]

    def get_left_menu_operation(self):
        sql = '''
            Select lv_1_operation,count(*) as cnt
            from `qyw_data_assets_check`
            group by lv_1_operation
            order by cnt desc
            limit 3
        '''
        result = db.select(sql)
        return result


class Messages(object):
    def create_message(self, msg):
        db.insert_dic(msg, 'dasset_user_messages')

    def set_read(self, id):
        sql = '''
            Update `dasset_user_messages` Set `status` = '1'
        '''
        db.update(sql)


class IndexShow(object):
    def selectSql(self):
        sql = '''
            select * from usually_sqls
        '''
        result = db.select(sql)
        return result

    def selectDatatable(self):
        sql = '''
            select * from dasset_reports
        '''
        result = db.select(sql)
        return result

    def selectDataAPI(self, limit=True):
        if limit:
            sql = '''
                select * from dasset_apis
            '''
        result = db.select(sql)
        return result


def apiupdate(table, id, status, oid):
    if id:
        sql = '''
            UPDATE 
                {0}
            SET
                status={1}
            WHERE
                id={2}
        '''.format(table, status, id)
    else:
        sql = '''
                    UPDATE 
                        {0}
                    SET
                        status={1}
                    WHERE
                        order_id="{2}"
                '''.format(table, status, oid)
    result = db.update(sql)
    print(result)
    return "状态修改成功"


def role_update(table, user_role, user_id):
    sql = '''
        UPDATE 
            {0}
        SET
            role_id={1}
        WHERE
            user_id='{2}'
    '''.format(table, user_role, user_id)

    result = db.update(sql)
    print(result)
    return "角色分配成功"


def select_role(table1, table2, table3):
    sql = '''
        SELECT 
            *
        FROM 
            `{0}` AS user 
        JOIN 
            `{1}` AS user_role 
        JOIN 
            `{2}` AS role
        ON 
            user.user_id = user_role.user_id
        AND 
            user_role.role_id = role.id
    '''.format(table1, table2, table3)
    result = db.select(sql)
    return result


def cat_message(table_name, count, message):
    if count:
        sql = '''
        SELECT 
            count(*) AS count
        FROM 
            `{0}` 
        WHERE 
            to_uid="{1}"
        AND 
            status=0;
        '''.format(table_name, count)
    elif message:
        sql = '''
                SELECT 
                    id,msg,from_uid,msg_time,status
                FROM 
                    `{0}` 
                WHERE 
                    to_uid="{1}"
                AND 
                    status=0;
                '''.format(table_name, message)
    result = db.select(sql)
    return result


def change_read(read):
    sql = '''
       UPDATE 
         dasset_user_messages   
       SET 
           status=1 
       where id={0}
    '''.format(read)
    db.update(sql)
    return "已读"


class Collect(object):

    # 加入收藏
    def save_collect(self, user_id, type, thing_id, source_table):
        try:
            result = self.select_check(user_id, source_table, thing_id)
            if result == "200":
                sql = '''
                    INSERT INTO dasset_collect (
                        user_id, type, thing_id, 
                        source_table, is_delete
                    )VALUES(
                           '{0}',{1},{2},'{3}',0 
                    ) 
                '''.format(user_id, type, thing_id, source_table)
                print(sql)
                db.insert(sql)
                return "200"
            else:
                return result
        except Exception as e:
            print(e)
            return "40"

    # 返回200说明没有检查到可以保存 返回已存在就是真的存在有 返回40就是报错了
    def select_check(self, user_id, source_table, thing_id):
        try:
            sql = '''
                SELECT * FROM 
                    dasset_collect
                WHERE
                    user_id='{0}' and is_delete=0 and source_table='{1}' and thing_id='{2}'
            '''.format(user_id, source_table, thing_id)
            print(sql)
            dic = db.select(sql)
            if dic.__len__() != 0:
                return "已经存在"
            else:
                return "200"
        except Exception as e:
            print(e)
            return "40"

    # 查找收藏的thing_id对应的真正数据
    def select_all_collect(self, table_name, user_id):
        try:
            sql = '''
                SELECT * FROM
                    {0}
                WHERE 
                    id in (select thing_id from dasset_collect where user_id='{1}' and is_delete=0 and source_table='{0}')
            '''.format(table_name, user_id)
            print(sql)
            resultDic = db.select(sql)
            if resultDic.__len__() == 0:
                return "40"
            else:
                return resultDic
        except Exception as e:
            print(e)
            return "出错了请联系管理员"

    def update_is_delete(self, type, thing_id):
        try:
            sql = '''
                update dasset_collect 
                set is_delete=1
                where type = {0} and thing_id = {1}
            '''.format(type, thing_id)
            print(sql)
            db.update(sql)
            return "200"
        except Exception as e:
            print(e)
            return "40"


class Standard(object):
    def standard_code(self, model_name):
        if model_name == 'all':
            sql = '''
                SELECT
                    simple_name,model_name,class_code,
                    GROUP_CONCAT(concat(code_content,":",code_desc)) as code_content
                FROM
                    `dasset_standard_code`
                group by 
                    simple_name,model_name,class_code
            '''
        else:
            sql = '''
                SELECT
                    simple_name,model_name,class_code,
                    GROUP_CONCAT(concat(code_content,":",code_desc)) as code_content
                FROM
                    `dasset_standard_code`
                where
                    `model_name` = '{0}'
                group by 
                    simple_name,model_name,class_code
            '''.format(model_name)
        result = db.select(sql)
        return result

    def get_menu(self):
        sql = '''
            select model_name,count(*) as cnt 
            from (SELECT distinct model_name,class_code FROM `dasset_standard_code`) as t
            GROUP BY model_name order by cnt DESC
        '''
        result = db.select(sql)
        return result

    def get_belong_tables_by_column(self, column_name):
        sql = '''
            SELECT * FROM `dasset_columns` where COLUMN_NAME='{0}'
        '''.format(column_name)
        db.select(sql)
        result = db.select(sql)
        return result


class Govern(object):
    def get_govern_rules(self):
        sql = '''
            Select * From `dasset_govern_rules` where problem_count is not null;
        '''
        result = db.select(sql)
        return result


class Through(object):
    def get_menu(self):
        sql = '''
            SELECT DISTINCT process_name FROM `dasset_through_tables`
        '''
        result = db.select(sql)
        return result

    def get_tables_by_process(self, process_name):
        sql = '''
            SELECT t1.*,t2.system 
            FROM `dasset_through_tables` t1
            left join dasset_system_names t2 on t1.source_system=t2.table_schema
            where process_name='{0}'
            order by process_name,link_name
        '''.format(process_name)
        db.select(sql)
        result = db.select(sql)

        tree = {}
        for item in result:
            if item['link_name'] not in tree:
                tree[item['link_name']] = [item]
            else:
                tree[item['link_name']].append(item.copy())
        return tree

    def get_image_url_by_process(self, process_name):
        sql = '''
            SELECT * FROM `dasset_through_table_images` where process_name='{0}'
        '''.format(process_name)
        result = db.select(sql)
        return result