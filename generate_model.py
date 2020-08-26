#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
# @Time    : 2020/8/26 14:15
# @Author  : Ryu
# @Site    : 
# @File    : sss.py
# @Software: PyCharm
# @function: 
'''
'''
文件用来根据mysql数据库表自动生成Django对应的模型类
'''

import pymysql
import os.path

host = 'localhost'
port = 3306
user = 'root'
password = 'root'
database = 'test'
# table = 'auth_group,auth_group_permissions'#此处若指定，则生成单表的模型，若没指定，则生成该数据库下所有表的模型
table = ''

dicts = {
    'int':'IntegerField',
    'varchar':'CharField',
    'char':'CharField',
    'bigint':'BigIntegerField',
    'text':'TextField',
    'datetime':'DateTimeField',
    'longtext': 'TextField',
    'smallint': 'SmallIntegerField',
    'tinyint':'BooleanField',
    'decimal':'DecimalField',
    'double':'FloatField',
    'date':'DateField',
    'time':'TimeField',
}

def getCursorConn(host=host,port=port,user=user,password=password,database=database):
    """
    连接数据库返回cursor和conn
    :return:
    """
    pymysql.install_as_MySQLdb()
    conn=pymysql.connect(host=host, port=port, user=user, password=password,database=database,charset="utf8")
    cursor=conn.cursor()
    return cursor,conn


def closeCurseConn(cursor,conn):
    """
    关闭之前打开的cursor，conn
    :param cursor:
    :param conn:
    :return:
    """
    cursor.close()
    conn.close()

import re
if __name__ == '__main__':
    cursor,conn = getCursorConn(host,port,user,password,database)
    # 指定的模型文件生成位置
    fname = 'model.py'
    #用来判断生成模型的个数
    if table == '':
        sql = 'show tables'
        cursor.execute(sql)
        result = cursor.fetchall()
        # 判断文件是否存在,若不存在则创建
        if not os.path.exists(fname):
            fd = open(fname, mode="w", encoding="utf-8")
            fd.close()
        with open(fname,'r+') as f:
            f.truncate()#清空文件内容
            f.write('from django.db import models\n\n')
    else:
        try:
            table_list = table.split(',')
            result = [(t,) for t in table_list]
        except Exception as e:
            result = [(table,)]

    with open('model.py','a') as f:

        for res in result:

            sql = f"select column_name,column_comment,data_type,column_type  from information_schema.columns where table_name='{res[0]}' and table_schema='{database}'"
            cursor.execute(sql)
            result1 = cursor.fetchall()
            f.write(f'class {res[0]}:\n')
            for i in result1:
                res1 = re.findall(r"\d+\.?\d*", i[3])
                model_char = dicts[i[2]]
                te = '()' if res1 == None or len(res1) == 0 else f'(max_length = {res1[0]})'
                temp = f'{i[0]} = models.{model_char}{te}'
                f.write(f'\t{temp}\n')

            f.write(f'\n\tclass Meta:\n')
            f.write(f'\t\tdb_table = "{res[0]}"\n\n')

    closeCurseConn(cursor,conn)
    print('任务文件已生成,请注意查收,数据库链接通道已关闭!')