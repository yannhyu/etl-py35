# tasks.py

from celery_config import app
import time
import logging
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, MetaData

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# create a file handler
handler = logging.FileHandler('tasks.log')
handler.setLevel(logging.INFO)

# create a logging format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# add the handlers to the logger
logger.addHandler(handler)

#CONN_STRING = 'postgresql://test_user:med@10.20.20.12:5432/etl'
CONN_STRING = 'postgresql://postgres:postgres@db:5432/postgres'
ALLOWED_QUERY_KEYS = {'cust_id', 'hid', 'acctnum', 'lname', 'fname'}

@app.task(name='ins00.add')
def add(x, y):
    time.sleep(5) # sleep for a while before the gigantic addition task!
    return x + y

@app.task(name='ins00.load_ins00_data')
def load_ins00_data(*args, **kwargs):
    results = []
    for key, value in kwargs.items():
        results.append('{} = {}<br>\n'.format(key, value))
    if 'reader' in kwargs and 'data' in kwargs:
        myreader = 'readers/{}'.format(kwargs.get('reader', 'ins00_reader_309.py'))
        myfile = 'Data/{}'.format(kwargs.get('data', 'Med_309_fake.txt'))

        import subprocess
        res = subprocess.call(['python3',
                               myreader,
                               myfile],
                               shell=False)
        results.append(str(res))
    return ''.join(results)


@app.task(name='ins00.read_db_data')
def read_db_data(lname_wanted='Washington'):
    Base = automap_base()

    # engine, assume it has a table 'ins00' set up
    engine = create_engine(CONN_STRING)

    # reflect the tables
    Base.prepare(engine, reflect=True)

    # mapped classes are now created with names by default
    # matching that of the table name.
    Insurance = Base.classes.ins00
    session = Session(engine)

    from sqlalchemy import text
    stmt = text("SELECT id, data "
                "FROM ins00 WHERE LOWER(data->>'lname')=LOWER(:lname)")
    stmt = stmt.columns(Insurance.id, Insurance.data)

    LNAME_WANTED = lname_wanted
    logger.info('looking up by last name: {}'.format(LNAME_WANTED))

    insurances = session.query(Insurance).\
                 from_statement(stmt).params(lname=LNAME_WANTED).all()
    results = []
    for ins in insurances:    
        results.append('{} {} {}<br>\n'.format(ins.data['fname'], ins.data['lname'], ins.data['ssn']))
    return ''.join(results)

def generate_flex_find_data_query_text(args, kwargs):
    results = []
    results.append("SELECT id, data FROM ins00 WHERE ")
    for key, value in kwargs.items():
        if key in ALLOWED_QUERY_KEYS:
            OK_LIKE_SQL_FLAG = ('L', 'LI', 'LIK', 'LIKE')
            if args[0] and args[0].upper() in OK_LIKE_SQL_FLAG:
                results.append("LOWER(data->>'{}') LIKE LOWER('%{}%') ".format(key,  value))
            else:
                results.append("LOWER(data->>'{}')=LOWER('{}') ".format(key,  value))
            results.append("AND ")
    return ''.join(results[:-1])

@app.task(name='ins00.flex_find_data')
def flex_find_data(*args, **kwargs):
    Base = automap_base()

    # engine, assume it has a table 'ins00' set up
    engine = create_engine(CONN_STRING)

    # reflect the tables
    Base.prepare(engine, reflect=True)

    # mapped classes are now created with names by default
    # matching that of the table name.
    Insurance = Base.classes.ins00
    session = Session(engine)

    my_sql = generate_flex_find_data_query_text(args, kwargs)
    logger.info('..db looking up with query: {}'.format(my_sql))
    from sqlalchemy import text
    stmt = text(my_sql)
    stmt = stmt.columns(Insurance.id, Insurance.data)
    insurances = session.query(Insurance).from_statement(stmt).all()
    results = []
    #results.append('LIKE is set to {}<br>\n'.format(args[0]))
    results.append('The following keys are allowed in search: {}'.format(','.join(ALLOWED_QUERY_KEYS)))
    results.append('<br>\n<br>\n')
    for ins in insurances:
        results.append('{}={}&'.format('cust_id', ins.data['cust_id']))
        results.append('{}={}&'.format('hid', ins.data['hid']))
        results.append('{}={}<br>\n'.format('acctnum', ins.data['acctnum']))
        results.append('{}/{}/{}<br>\n'.format(ins.data['cust_id'], ins.data['hid'], ins.data['acctnum']))
        results.append('{} {}<br>\n'.format(ins.data['fname'], ins.data['lname']))
        results.append('{}<br>\n'.format(ins.data['addr1']))
        results.append('{}, {} {}<br>\n'.format(ins.data['city'],
                                                ins.data['state'],
                                                ins.data['zip5']))
        fname = ins.data.get('eb_fn')
        append_ssn = ins.data.get('eb_ssn')
        if fname or append_ssn:
            results.append('<h5 style="color:red;">eBureau: (')
            if fname:
                results.append('fname: {}, '.format(fname))
            if append_ssn:
                results.append('append_ssn: {})'.format(append_ssn))
            results.append('</h5>')
        results.append('<br>\n<br>\n')
    return ''.join(results)

def generate_eb_update_query_text(args, kwargs):
    import json
    results = []
    results.append("UPDATE ins00 SET ")
    results.append("  data = data || '{}' ".format(json.dumps(kwargs)))
    results.append("WHERE data->>'cust_id'='{}' AND data->>'hid'='{}' AND data->>'acctnum'='{}'".format(*args))

    return ''.join(results)

@app.task(name='ins00.eb_update')
def eb_update(*args, **kwargs):
    rowcount = 'row(s) affected: ... '
    # engine, assume it has a table 'ins00' set up
    engine = create_engine(CONN_STRING, client_encoding='utf8')
    meta = MetaData(bind=engine, reflect=True)

    from sqlalchemy.sql import text

    my_sql = generate_eb_update_query_text(args, kwargs)
    logger.info('..db upsert with query: {}'.format(my_sql))
    with engine.connect() as con:
        result = con.execute(text("""{}""".format(my_sql)))
        rowcount += str(result.rowcount)
    return rowcount

def generate_eb_delete_query_text(args, kwargs):
    EBUREAU_KEYS = ('eb_fn', 'eb_ln', 'eb_ssn', 'eb_code')
    import json
    results = []
    results.append("UPDATE ins00 SET ")
    results.append("  data = data - '{}' ".format(kwargs.get('target')))
    results.append("WHERE data->>'cust_id'='{}' AND data->>'hid'='{}' AND data->>'acctnum'='{}'".format(*args))

    return ''.join(results)

@app.task(name='ins00.eb_delete')
def eb_delete(*args, **kwargs):
    rowcount = 'row(s) affected: ... '
    # engine, assume it has a table 'ins00' set up
    engine = create_engine(CONN_STRING, client_encoding='utf8')
    meta = MetaData(bind=engine, reflect=True)

    from sqlalchemy.sql import text

    my_sql = generate_eb_delete_query_text(args, kwargs)
    logger.info('..db upsert with query: {}'.format(my_sql))
    with engine.connect() as con:
        result = con.execute(text("""{}""".format(my_sql)))
        rowcount += str(result.rowcount)
    return rowcount