import os
from flask import Flask, request
from flask import url_for
from worker import celery
from celery.result import AsyncResult
import celery.states as states

env=os.environ
app = Flask(__name__)

@app.route('/add/<int:param1>/<int:param2>')
def add(param1,param2):
    task = celery.send_task('ins00.add', args=[param1, param2], kwargs={})
    return "<a href='{url}'>check status of {id} </a>".format(id=task.id,
                url=url_for('check_task',id=task.id,_external=True))

@app.route('/load_ins00_data/')
def load_ins00_data():
    all_args = request.args.to_dict()
    task = celery.send_task('ins00.load_ins00_data', args=[], kwargs=all_args)
    return "<a href='{url}'>check status of {id} </a>".format(id=task.id,
                url=url_for('check_task',id=task.id,_external=True))

@app.route('/read_db_data/<string:param>')
def read_db_data(param):
    task = celery.send_task('ins00.read_db_data', args=[], kwargs={'lname_wanted':param})
    return "<a href='{url}'>check status of {id} </a>".format(id=task.id,
                url=url_for('check_task',id=task.id,_external=True))

@app.route('/flex_find_data/', defaults={'param': 'eq'})
@app.route('/flex_find_data/<string:param>')
def flex_find_data(param):
    all_args = request.args.to_dict()
    task = celery.send_task('ins00.flex_find_data', args=[param], kwargs=all_args)
    return "<a href='{url}'>check status of {id} </a>".format(id=task.id,
                url=url_for('check_task',id=task.id,_external=True))

@app.route('/eb_update/<string:param1>/<string:param2>/<string:param3>/')
def eb_update(param1,param2,param3):
    all_args = request.args.to_dict()
    task = celery.send_task('ins00.eb_update', args=[param1,param2,param3], kwargs=all_args)
    return "<a href='{url}'>check status of {id} </a>".format(id=task.id,
                url=url_for('check_task',id=task.id,_external=True))

@app.route('/eb_delete/<string:param1>/<string:param2>/<string:param3>/')
def eb_delete(param1,param2,param3):
    all_args = request.args.to_dict()
    task = celery.send_task('ins00.eb_delete', args=[param1,param2,param3], kwargs=all_args)
    return "<a href='{url}'>check status of {id} </a>".format(id=task.id,
                url=url_for('check_task',id=task.id,_external=True))

@app.route('/check/<string:id>')
def check_task(id):
    res = celery.AsyncResult(id)
    if res.state==states.PENDING:
        return res.state
    else:
        return str(res.result)


if __name__ == '__main__':
    app.run(debug=env.get('DEBUG',True),
            port=int(env.get('PORT',5000)),
            host=env.get('HOST','0.0.0.0')
    )
