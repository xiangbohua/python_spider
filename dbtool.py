#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

import logging
import pymysql


class MySQLCommand(object):
    def __init__(self, host, port, user, passwd, db):
        self.host = host
        self.port = port
        self.user = user
        self.password = passwd
        self.db = db
        self.auto_commit = True

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.closeMysql()


    def begin(self):
        try:
            self.conn.begin()
            self.auto_commit = False
        except:
            self.auto_commit = True
            raise

    def rollback(self):
        if self.auto_commit == True :
            try:
                self.conn.rollback()
            except:
                raise
            finally:
                self.auto_commit = True

    def commit(self):
        try:
            self.conn.commit()
        except:
            raise
        finally:
            self.auto_commit = True

    def connect(self):
        try:
            self.conn = pymysql.connect(host=self.host, port=self.port, user=self.user, passwd=self.password,
                                        db=self.db, charset='utf8')
            self.cursor = self.conn.cursor()
        except:
            print('connect mysql error.')
            raise

    def select(self, sql):
        try:
            self.cursor.execute(sql)
            rows = self.cursor.fetchall()
            return rows
        except:
            print(sql + ' execute failed.')
            raise

    def insert(self, table, column_value):
        column = ''
        value = ''

        if isinstance(column_value, (dict)):
            for col, val in column_value.items():
                col = str(col)
                val = str(val).replace("'", "\\'")

                column += "`" + col + "`,"
                if value == '':
                    value += '('
                value += "'" + val + "',"
            value = value[:-1] + ')'

        elif isinstance(column_value, (list)):
            if len(column_value) > 0:
                for col,val in column_value[0].items():
                    col = col
                    column += "`" + col + "`,"

            for d in column_value:
                valueOne = ''
                for col, val in d.items():
                    if valueOne == '':
                        valueOne += '('
                    valueOne += "'" + str(val).replace("'", "\\'") + "',"
                valueOne = valueOne[:-1] + ")"
                value += valueOne + ","
            value = value[:-1]

        sql = "INSERT INTO " + table + " (" + column[:-1] + ") " + "VALUES " + value
        try:
            self.cursor.execute(sql)
            if self.auto_commit == True:
                self.conn.commit()

        except:
            self.conn.rollback()
            print("insert failed." + sql)
            raise

    def update(self, table, where, column_value):
        setStatement = ''
        for col, val in column_value.items():
            setStatement += col + " = '" + str(val) + "',"

        sql = "UPDATE " + table + " SET " + setStatement[:-1] + " WHERE " + where
        try:
            self.cursor.execute(sql)
            if self.auto_commit == True:
                self.conn.commit()
                # print("update 成功:" + sql)
        except:
            self.conn.rollback()
            print('update 失败:' + sql)
            raise

    def count(self, table, where = ''):
        sql = "select count(*) from " + table
        if len(where) > 0:
            sql +=  " where " + where

        count = self.select(sql)[0][0]
        return count

    def closeMysql(self):
        self.cursor.close()
        self.conn.close()


