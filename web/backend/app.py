from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin

import random
import hashlib

import GraphAPILib as API
import variables as Variables

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
tasks_map = {}


def create_string_id(number):
    string_id = ""

    for i in range(7):
        if number % 10 > 0:
            string_id = str(number % 10) + string_id
            number //= 10
        else:
            string_id = str(0) + string_id

    return string_id


def create_task_redirect_url(params_tuple):
    if params_tuple is None:
        return 'null'

    # TODO: create HTTP request to generator service
    return '"https://www.google.com"'


@app.route('/tasks', methods=['GET', 'OPTIONS'])
@cross_origin()
def get_task():  # put application's code here
    task_id = request.args.get('id')

    if task_id is None:
        return "No id parameters in request", 400

    redirect_url = create_task_redirect_url(tasks_map.get(task_id))
    json_response_string = '{{"redirect": {}}}'.format(redirect_url)

    print(jsonify(json_response_string))
    return jsonify(json_response_string), 200


'''
Handling creating of new task

Request example:
{
    "mail": "student@example.com",
    "task_type": "type_example",
    "task_format": "format_example",
    "number_of_exercises": 10,
    "assignment_link": "graph_link"
}
'''
@app.route('/createTask', methods=['POST', 'OPTIONS'])
@cross_origin()
def create_task():  # put application's code here
    request_data = request.get_json()

    if not request_data:
        return "No JSON in request", 400

    if not ('mail' in request_data and 'task_type' in request_data and
            'task_format' in request_data and 'number_of_exercises' in request_data and
            'assignment_link' in request_data):
        return "Not all required keys are provided in JSON", 400

    external_task_id = create_string_id(random.randint(0, 9999999))
    internal_task_id = hashlib.md5(external_task_id.encode('utf-8'))
    tasks_map[external_task_id] = (internal_task_id.hexdigest(), request_data['mail'],
                                   request_data['task_type'],
                                   request_data['task_format'],
                                   request_data['number_of_exercises'],
                                   request_data['assignment_link'])
    print("Created task with ID: ", external_task_id)
    print("hash: ", internal_task_id.hexdigest())
    json_response_string = '{{"task_url": {}}}'\
        .format(create_task_redirect_url(tasks_map[external_task_id]))

    return jsonify(json_response_string), 200


'''
Handling task grading

Request example:
{
    "token": "128_symbols_trash",
    "grade": 10,
    "comment": "Big text example"
}
'''
@app.route('/gradeTask', methods=['POST', 'OPTIONS'])
@cross_origin()
def grade_task():
    request_data = request.get_json()
    passed = False
    assignment_link = None

    if not request_data:
        return "No JSON in request", 400

    if not ('token' in request_data and 'grade' in request_data):
        return "Not all required keys are provided in JSON", 400
    token = request_data['token']
    grade = int(request_data['grade'])
    comment = request_data['comment']

    for val in tasks_map.values():
        if val[0] == token:
            passed = True
            assignment_link = val[-1]

    if not passed:
        return 'OK!', 200

    if not Variables.user_token:
        Variables.user_token, _ = API.get_token(Variables.secret_login,
                                                Variables.secret_password)

    submission_id = API.get_submissions(assignment_link)
    submission_link = f'{assignment_link}/submissions/{submission_id}'
    API.submit_task(submission_link)
    API.grade_task(submission_link, grade, comment)

    return 'Graded!', 200


if __name__ == '__main__':
    app.run()
