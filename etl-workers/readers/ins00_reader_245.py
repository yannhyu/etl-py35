# ins00_reader_245.py

import fileinput
from collections import OrderedDict
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.schema import MetaData
import psycopg2

INPUT_LAYOUT = ('cust_id', 'treatment_code', 'output_id', 'hid', 'acctnum', 'cpi',
                'patient_name', 'mname', 'fname', 'addr1', 'addr2', 'city', 'state',
                'zip5', 'temp_zip4', 'ssn', 'gender', 'dob', 'g_name', 'g_mname', 'g_fname',
                'g_addr1', 'g_addr2', 'g_city', 'g_state', 'g_zip5', 'temp_g_zip4', 'g_ssn',
                'g_gender', 'g_dob', 'g_employ_name', 'provider_state',
                'service_date_begin', 'service_date_end', 'pat_proc_type', 'pat_type',
                'fin_class', 'payor_plan1', 'payor_plan2', 'cpt', 'drg', 'diag1', 'diag2',
                'charges', 'balance', 'acct_status', 'client_field1', 'client_field2',
                'client_field3', 'client_field4',
                'hospital_state2', 'hospital_city', 'hospital_county', 'hospital_zip')

V4_OUTPUT_FIELDS = ('cust_id', 'treatment_code', 'output_id', 'hid', 'acctnum', 'cpi',
                'lname', 'mname', 'fname', 'addr1', 'addr2', 'city', 'state',
                'zip5', 'zip4', 'ssn', 'gender', 'dob', 'g_lname', 'g_mname', 'g_fname',
                'g_addr1', 'g_addr2', 'g_city', 'g_state', 'g_zip5', 'g_zip4', 'g_ssn',
                'g_gender', 'g_dob', 'g_employ_name', 'provider_state',
                'service_date_begin', 'service_date_end', 'pat_proc_type', 'pat_type',
                'fin_class', 'payor_plan1', 'payor_plan2', 'cpt', 'drg', 'diag1', 'diag2',
                'charges', 'balance', 'acct_status', 'client_field1', 'client_field2',
                'client_field3', 'client_date1')

#conn_str = 'postgresql://test_user:med@10.20.20.12:5432/etl'
conn_str = 'postgresql://postgres:postgres@db:5432/postgres'
engine = create_engine(conn_str)
meta = MetaData()
meta.reflect(bind=engine)

def hack_names(last, first, *middle):
        return last, first, middle

def project_data(dict_data):
    dict_out = OrderedDict(zip(V4_OUTPUT_FIELDS, [ dict_data.get(field, '') for field in V4_OUTPUT_FIELDS ]))
    if not dict_out['cust_id']:    # Curating
        dict_out['cust_id'] = '245'

    # patient_name is in the form 'last first [middle]'
    # examples: 'CARSWELL JARVIS', 'DAWLEY BARBARA A', 'BROWN MICHAEL DAVID', or 'BRUMFIELD KRISTY GAYLE'
    #last, first, *middle = dict_data['patient_name'].split()
    patient_names = dict_data['patient_name'].split()
    last, first, middle = hack_names(*patient_names)
    if not dict_out['lname']:
        dict_out['lname'] = last
    if not dict_out['fname']:
        dict_out['fname'] = first
    if middle and not dict_out['mname']:    # If middle name list is non-empty and ..
        dict_out['mname'] = middle[0]

    g_names = dict_data['g_name'].split()
    if g_names and len(g_names) > 1:
        g_last, g_first, g_middle = hack_names(*g_names)
        if not dict_out['g_lname']:
            dict_out['g_lname'] = g_last
        if not dict_out['g_fname']:
            dict_out['g_fname'] = g_first
        if g_middle and not dict_out['g_mname']:    # If middle name list is non-empty and ..
            dict_out['g_mname'] = g_middle[0]
    elif g_names and len(g_names) == 1:
        dict_out['g_lname'] = g_names[0]

    return dict_out

if __name__ == '__main__':
    import sys
    sys.setdefaultencoding('utf8')
    reload(sys)
    for line in fileinput.input():
        if not fileinput.isfirstline():    # First line is header in the case of 245
            dic_line = dict(zip(INPUT_LAYOUT, line.strip('\n').strip('\r').split('|')))
            row = project_data(dic_line)
            try:
                engine.execute(
                    meta.tables['ins00'].insert().values(data=row)
                )
            except (psycopg2.DataError, sqlalchemy.exc.DataError, sqlalchemy.exc.StatementError):
                print('Unable to insert data:')
                print(row)
                pass