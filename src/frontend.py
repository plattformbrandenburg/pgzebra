import cherrypy
from jinja2 import Environment, FileSystemLoader
import os
import json
import csv

import datadb
from urlparams import UrlParams

env = Environment(loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')))


class Frontend(object):

    def __init__(self, features):
        self.features = features

    @cherrypy.expose
    def default(self, *args):
        if len(args) == 0:  # show all dbs
            return self.list_all_dbs()
        elif len(args) == 1:  # show all tables for a db
            return self.list_all_tables(args[0])

        print 'args', args
        up = UrlParams(datadb.object_cache, self.features, *args)
        print 'up', up
        sql = up.to_sql()
        print 'sql', sql
        data = datadb.execute_on_db_uniq(up.db_uniq, sql)
        print 'data'
        print data

        if up.output_format == 'json':
            return json.dumps(data)
        elif up.output_format == 'csv':
            return json.dumps(data)     # TODO
        else:
            tmpl = env.get_template('index.html')
            return tmpl.render(message=None, dbname=up.dbname, table=up.table, sql=sql, data=str(data))

    def list_all_dbs(self, output_format='html'):
        db_uniqs = datadb.object_cache.cache.keys()
        db_info = []
        for u in db_uniqs:
            splits = u.split(':')
            db_info.append({'dbname': splits[0], 'hostname': splits[1], 'port': splits[2]})
        db_info.sort(key=lambda x:x['dbname'])

        if output_format == 'json':
            return json.dumps(db_info)
        elif output_format == 'csv':
            return json.dumps(db_info)     # TODO
        else:
            tmpl = env.get_template('dbs.html')
            return tmpl.render(message=None, db_info=db_info)

    def list_all_tables(self, dbname, output_format='html'):
        db_uniq, table = datadb.object_cache.get_dbuniq_and_table_full_name(dbname)
        tables = datadb.object_cache.get_all_tables_for_dbuniq(db_uniq)
        tables.sort()
        print 'tables', tables

        if output_format == 'json':
            return json.dumps(tables)
        elif output_format == 'csv':
            return json.dumps(tables)     # TODO
        else:
            tmpl = env.get_template('tables.html')
            return tmpl.render(message=None, dbname=dbname, tables=tables)