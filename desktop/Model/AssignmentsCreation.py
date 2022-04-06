from functools import partial

import Model.GraphAPI as API


def generate_assignment(member, task_type, task_format, number_of_exercises):
    json = f'{{mail: {member}, ' \
           f'task_type: {task_type}, ' \
           f'task_format: {task_format}, ' \
           f'number_of_exercises: {number_of_exercises}}}'

    # TODO: create request to web back
    return f'https://www.google.com/{member}'


def create_assignments(members, class_id,
                       task_type, task_format, number_of_exercises,
                       due_date, name):
    urls = list(map(partial(generate_assignment,
                            task_type=task_type,
                            task_format=task_format,
                            number_of_exercises=number_of_exercises),
                    members))

    list(map(partial(API.create_assignment,
                     class_id,
                     due_date,
                     name), members, urls))
