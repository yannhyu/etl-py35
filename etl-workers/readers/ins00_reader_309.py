# ins00_reader_309.py

import fileinput
from collections import OrderedDict
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.schema import MetaData
import psycopg2

INPUT_LAYOUT = ('cust_id', 'treatment_code', 'output_id', 'hid', 'acctnum', 'cpi',
                'lname', 'mname', 'fname', 'addr1', 'addr2', 'city', 'state',
                'zip5', 'zip4', 'ssn', 'gender', 'dob', 'g_lname', 'g_mname', 'g_fname',
                'g_addr1', 'g_addr2', 'g_city', 'g_state', 'g_zip5', 'g_zip4', 'g_ssn',
                'g_gender', 'g_dob', 'g_employ_name', 'provider_state',
                'service_date_begin', 'service_date_end', 'pat_proc_type', 'pat_type',
                'fin_class', 'payor_plan1', 'payor_plan2', 'cpt', 'drg', 'diag1', 'diag2',
                'charges', 'balance', 'acct_status', 'client_field1', 'client_field2',
                'client_field3', 'client_date1')

V4_OUTPUT_FIELDS = ('cust_id', 'treatment_code', 'output_id', 'hid', 'acctnum', 'cpi',
                'lname', 'mname', 'fname', 'addr1', 'addr2', 'city', 'state',
                'zip5', 'zip4', 'ssn', 'gender', 'dob', 'g_lname', 'g_mname', 'g_fname',
                'g_addr1', 'g_addr2', 'g_city', 'g_state', 'g_zip5', 'g_zip4', 'g_ssn',
                'g_gender', 'g_dob', 'g_employ_name', 'provider_state',
                'service_date_begin', 'service_date_end', 'pat_proc_type', 'pat_type',
                'fin_class', 'payor_plan1', 'payor_plan2', 'cpt', 'drg', 'diag1', 'diag2',
                'charges', 'balance', 'acct_status', 'client_field1', 'client_field2',
                'client_field3', 'client_date1')

conn_str = 'postgresql://postgres:postgres@db:5432/postgres'
engine = create_engine(conn_str)
meta = MetaData()
meta.reflect(bind=engine)

def project_data(dict_data):
    return OrderedDict(zip(V4_OUTPUT_FIELDS, [ dict_data.get(field, '') for field in V4_OUTPUT_FIELDS ]))

if __name__ == '__main__':
    for line in fileinput.input():
        if not fileinput.isfirstline():    # First line is header in this 309 case
            dic_line = dict(zip(INPUT_LAYOUT, line.strip('\n').strip('\r').split('|')))
            row = project_data(dic_line)
            try:
                engine.execute(
                    meta.tables['ins00'].insert().values(data=row)
                )
            except (psycopg2.DataError, sqlalchemy.exc.DataError):
                pass