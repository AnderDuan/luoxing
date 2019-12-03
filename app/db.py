# -*- coding:utf-8 -*-

import mysql.connector
from mysql.connector import pooling
from mysql.connector import Error


class MySqlClass(object):
    cnn = None
    cur = None
    pool = None

    # 连接数据库`
    def _connect(self, host, port, user, pwd, db, pool_size=5):
        try:
            self.pool = mysql.connector.pooling.MySQLConnectionPool(
                pool_name='mypool',
                pool_size=pool_size,
                pool_reset_session=True,
                host=host,
                port=port,
                user=user,
                password=pwd,
                database=db,
                charset='utf8')
        except SystemError as e:
            print("MySQL连接错误！" + e)

    # 初始化数据库
    def __init__(self,
                 host='127.0.0.1',
                 port=3306,
                 user='root',
                 pwd='root',
                 db='hb_elec',
                 pool_size=32):
        self._connect(host, port, user, pwd, db, pool_size=pool_size)
        # self.cur = self.cnn.cursor(dictionary=True)

    # 关闭数据库连接
    def close(self):
        try:
            self.cur.close()
            self.cnn.close()
        except SystemError:
            print("Closed")

    # 更改默认数据库
    def change_db(self, data_base):
        self.cnn = self.pool.get_connection()
        self.cur = self.cnn.cursor(dictionary=True)
        self.cur.execute('use `%s`' % data_base)
        self.close()

    # SQL查询语句，返回字典的列表
    def select(self, sql_str, source_type=None):
        self.cnn = self.pool.get_connection()
        self.cur = self.cnn.cursor(dictionary=True)
        if sql_str.lower().find("select") >= 0 \
                or sql_str.lower().find("show") >= 0:
            self.cur.execute(sql_str)
            dic = self.cur.fetchall()
            if source_type=='gbase':
                pass
            else:
                self.close()
            return dic
        else:
            print("SQL语句中没有Select")
            self.close()
            return

    # 使用存储过程
    def procedure(self, proc_name, params):
        self.cnn = self.pool.get_connection()
        self.cur = self.cnn.cursor(dictionary=True)
        self.cur.callproc(proc_name, params)
        for result in self.cur.stored_results():
            result_list = result.fetchall()
        self.close()
        return result_list

    # 直接插入字典的列表
    def insert_dic_list(self, table_name, data_list, replace=False):
        for item in data_list:
            self.insert_dic(item, table_name, replace=replace)

    # 用SQL语句删除
    def delete(self, sql_str):
        self.cnn = self.pool.get_connection()
        self.cur = self.cnn.cursor(dictionary=True)
        if sql_str.lower().find('delete') >= 0:
            i = self.cur.execute(sql_str)
            self.cnn.commit()
            self.close()
            return i
        else:
            print('SQL语句中未包含DELETE！')
            self.close()

    # 用SQL语句插入
    def insert(self, sql_str):
        self.cnn = self.pool.get_connection()
        self.cur = self.cnn.cursor(dictionary=True)
        if sql_str.lower().find('insert') >= 0:

            self.cur.execute(sql_str)
            self.cnn.commit()
            self.close()
        else:
            print('SQL语句中未包含INSERT！')
            self.close()

    # 用SQL语句插入，并根据主键替换掉原始记录
    def replace(self, sql_str):
        self.cnn = self.pool.get_connection()
        self.cur = self.cnn.cursor(dictionary=True)
        if sql_str.lower().find('replace') >= 0:
            self.cur.execute(sql_str)
            self.cnn.commit()
            self.close()
        else:
            print('SQL语句中未包含REPLACE！')
            self.close()

    # 插入单个字典
    # self.insert_dic(item, table_name, replace=replace)
    def insert_dic(self, dic, table_name, sys_time=0, replace=False):
        self.cnn = self.pool.get_connection()
        self.cur = self.cnn.cursor(dictionary=True)
        field = []
        value = []
        print(dic)
        for item in dic:
            if dic[item] is not None:
                field.append("`" + str(item) + "`")
                # print item
                # value.append("'" + str(dic[item]) + "'")
                value.append("'%s'" % dic[item])
                # print str(dic[item])
        if 0 != sys_time:
            field.append('sProcTime')
            value.append("'" + str(sys_time) + "'")
        field_str = ','.join(field)
        value_str = ','.join(value)
        if not replace:
            sql_str = 'INSERT INTO `%s`(%s) VALUES(%s)' % (
                table_name, field_str, value_str)
            # print sql_str
            print(sql_str)
            self.insert(sql_str)
        else:
            sql_str = 'REPLACE INTO `%s`(%s) VALUES(%s)' % (
                table_name, field_str, value_str)
            self.replace(sql_str)

    # 插入列表
    def insert_list(self, data_list, table_name, replace=False):
        field = []
        value = []
        sql_str = "Show fields from %s " % table_name
        field_list = self.select(sql_str)
        for item in field_list:
            if item['Field'].lower() != 'id':
                field.append(item['Field'])
        for item in data_list:
            if isinstance(item, str):
                value.append("'" + item + "'")
            else:
                value.append("'" + item + "'")
                # print str(dic[item])

        value_str = ','.join(value)
        field_str = ','.join(field)
        if not replace:
            sql_str = 'INSERT INTO `%s`(%s) VALUES(%s)' % (
                table_name, field_str, value_str)
            # print sql_str
            self.insert(sql_str)
        else:
            sql_str = 'REPLACE INTO `%s`(%s) VALUES(%s)' % (
                table_name, field_str, value_str)
            # print sql_str
            self.replace(sql_str)

    # 用SQL语句更新
    def update(self, sql_str):
        self.cnn = self.pool.get_connection()
        self.cur = self.cnn.cursor(dictionary=True)
        if sql_str.lower().find('update') >= 0 or sql_str.lower().find(
                'replace') >= 0:
            self.cur.execute(sql_str)
            self.cnn.commit()
            self.close()
        else:
            print('SQL语句中未包含UPDATE！')
            self.close()

    # MySQL自带LOAD DATA INFILE 功能实现
    def load_file(self, file_name, table_name, replace=False, code='GBK'):
        self.cnn = self.pool.get_connection()
        self.cur = self.cnn.cursor(dictionary=True)
        field = []
        sql_str = "Show fields from %s " % table_name
        field_list = self.select(sql_str)
        for item in field_list:
            # if item['Field'].lower() != 'id':
            field.append(item['Field'])
        field_str = ','.join(field)
        if not replace:
            rep = ''
        else:
            rep = 'REPLACE'
        sql_str = """
        LOAD DATA LOCAL INFILE '%s'
        %s INTO TABLE `%s`
        Character Set %s
        Fields Terminated By ','
        Ignore 1 Lines
        (%s)
        """ % (file_name, rep, table_name, code, field_str)
        self.cur.execute(sql_str)
        self.cnn.commit()
        self.close()

    # MySQL自动LOAD XML功能实现
    def load_xml(self,
                 file_name,
                 table_name,
                 tag='RC',
                 replace=False,
                 code='utf8',
                 proc_date=0):
        # field = []
        # sql_str = "Show fields from `%s` " % table_name
        # field_list = self.select(sql_str)
        # for item in field_list:
        #     # if item['Field'].lower() != 'id':
        #     field.append(item['Field'])
        # field_str = ','.join(field)
        self.cnn = self.pool.get_connection()
        self.cur = self.cnn.cursor(dictionary=True)
        if not replace:
            rep = ''
        else:
            rep = 'REPLACE'
        sql_str = """
            LOAD XML LOCAL INFILE '%s'
            %s INTO TABLE `%s`
            Character Set %s
            Rows Identified By '<%s>'
            """ % (file_name, rep, table_name, code, tag)
        self.cur.execute(sql_str)
        if 0 != proc_date:
            sql_str = '''
            UPDATE `%s` SET
            `sProcTime` = '%s'
            Where `sProcTime` IS NULL
            ''' % (table_name, str(proc_date))
            self.cur.execute(sql_str)
            self.cnn.commit()
            self.close()


if __name__ == '__main__':
    a = MySqlClass("10.122.227.63", 18000, "luoxing", "lx_666", "luoxing")
    # # a.connect("87.252.15.146","742967","Password","workspace")
    # # sql = "select * From `cc-scheduletable`"
    # # print sql.find("select")
    # dic_1 = a.procedure('credit_summary', ('2017-08-01', '2017-08-10'))
    # print dic_1[0][0]
    # # a.close()
    # # a.load_file('d:/1.csv', 'ccbc_06_creditcard', True)
    # a.load_xml('d:/3.xml', 'center')
    # a.close()
    print(a.select("Select * from `dasset_tables` limit 10;"))
