from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin

import random
import hashlib
import requests

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

    headers = {
        'Content-Type': 'application/json'
    }

    payload = '{\n' \
              f'\"gradeToken\": \"{params_tuple[0]}\", \n' \
              f'\"gradeUrl\": \"https://management-system-api.azurewebsites.net/gradeTask\", \n' \
              f'\"userEmail\": \"{params_tuple[1]}\",\n' \
              f'\"firstname\": \"{params_tuple[2]}\", \n' \
              f'\"lastname\": \"{params_tuple[3]}\", \n' \
              f'\"taskType\": \"{params_tuple[4]}\", \n' \
              f'\"taskFormat\": \"{params_tuple[5]}\", \n' \
              f'\"taskClass\": \"SomeClass\", \n' \
              f'\"taskNumber\": {params_tuple[6]}, \n' \
              f'\"isGenerated\": false, \n' \
              f'\"timeFinish\": \"{params_tuple[7]}\", \n' \
              f'\"assignmentName\": \"{params_tuple[8]}\" \n' \
              '}'
    print("Sending request with payload: ", payload)
    response = requests.request("POST", "https://ed-machine-deployment-test.vercel.app/api/tasks/create",
                                headers=headers, data=payload.encode('utf-8')).json()
    print('Response: ', response)

    return response['assessmentUrl']


@app.route('/')
def index():
    return "Home"


@app.route('/tasks', methods=['GET', 'OPTIONS'])
@cross_origin()
def get_task():  # put application's code here
    task_id = request.args.get('id')

    if task_id is None:
        return "No id parameters in request", 400
    if task_id not in tasks_map:
        return "Unknown task", 400

    redirect_url = create_task_redirect_url(tasks_map.get(task_id))
    json_response_string = '{{"redirect": "https://{}"}}'.format(redirect_url)

    print(json_response_string)
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

    if not ('student_email' in request_data and 'task_type' in request_data and
            'task_format' in request_data and 'number_of_exercises' in request_data and
            'assignment_link' in request_data and
            'student_name' in request_data and 'student_surname' in request_data and
            'assignment_end_time' in request_data and 'task_title' in request_data):
        return "Not all required keys are provided in JSON", 400

    external_task_id = create_string_id(random.randint(0, 9999999))
    while external_task_id in tasks_map:
        external_task_id = create_string_id(random.randint(0, 9999999))

    internal_task_id = hashlib.md5(external_task_id.encode('utf-8'))
    tasks_map[external_task_id] = (internal_task_id.hexdigest(), request_data['student_email'],
                                   request_data['student_name'],
                                   request_data['student_surname'],
                                   request_data['task_type'],
                                   request_data['task_format'],
                                   request_data['number_of_exercises'],
                                   request_data['assignment_end_time'],
                                   request_data['task_title'],
                                   request_data['assignment_link'])
    print("Created task with ID: ", external_task_id)
    print("hash: ", internal_task_id.hexdigest())
    json_response_string = '{{"task_url": "{}"}}'\
        .format(f'https://management-system-web.azurewebsites.net/{external_task_id}')

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
    key_to_delete = None

    if not request_data:
        return "No JSON in request", 400

    if not ('token' in request_data and 'grade' in request_data):
        return "Not all required keys are provided in JSON", 400
    token = request_data['token']
    grade = int(request_data['grade'])
    comment = request_data['comment']
    # get dict key to delete task after grading
    for key, val in tasks_map.items():
        if val[0] == token:
            passed = True
            assignment_link = val[-1]
            key_to_delete = key

    if not passed:
        return 'OK!', 200

    if not Variables.user_token:
        Variables.user_token, _ = API.get_token(Variables.secret_login,
                                                Variables.secret_password)

    submission_id = API.get_submissions(assignment_link)
    submission_link = f'{assignment_link}/submissions/{submission_id}'
    API.submit_task(submission_link)
    API.grade_task(submission_link, grade, comment)
    tasks_map.pop(key_to_delete)

    return 'Graded!', 200


if __name__ == '__main__':
    app.run()
