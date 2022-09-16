import functools
from functools import partial
from collections import defaultdict
from multiprocessing.dummy import Pool as ThreadPool

import numpy as np
import pandas as pd
import time

import Model.GraphAPI as API
import Model.EnvironmentVariables as Variables

# table: (Email, Program, TeamsGroup, Status)
table_r = [("vasokolovskiy@ithse.ru", "TestA", "TestAPIClass", 1),
           ("TestUser1@ithse.ru", "TestA", "TestAPIClass", 1),
           ("TestUser2@ithse.ru", "TestA", "TestAPIClass", 1),
           ("TestUser3@ithse.ru", "TestC", "TestAPIClass", 1),
           ("TestUser4@ithse.ru", "TestC", "TestAPIClass", 1),
           ("TestUser5@ithse.ru", "TestB", "TestAPIClass", 1),
           ("TestUser6@ithse.ru", "TestB", "TestAPIClass", 1),
           ("TestUser7@ithse.ru", "TestB", "TestAPIClass", 1),
           ("TestUser8@ithse.ru", "TestA", "TestAPIClass", 1),
           ("TestUser9@ithse.ru", "TestC", "TestAPIClass", 1)]
# ("vasokolovskiy@ithse.ru", "TestB", "TestAPIClassB", 1)]
# ("b", "b", "a", 1),
# ("c", "c", "a", 1),
# ("a", "a", "b", 1),
# ("b", "b", "b", 1),
# ("c", "c", "b", 1),
# ('d', 'd', 'b', 1)]
classes_in_organization = {}


def highlight_bad_rows(x, bad_elems):
    dictionary = x.to_dict()
    if dictionary in bad_elems:
        return ['background-color: yellow'] * len(x)
    else:
        return [''] * len(x)


def get_class_members(class_name):
    members = API.get_class_members(classes_in_organization[class_name])
    teachers = API.get_class_teachers(classes_in_organization[class_name])

    return [x for x in members if x not in teachers]


def add_member_to_class(member_email, class_id):
    API.add_member_to_class(class_id, member_email)


def add_member_to_tag(class_id, tags_dict, members_dict, member_email):
    API.add_member_to_tag(class_id, tags_dict[members_dict[member_email]], member_email)


def populate_program_tags(tags, only_table_members,
                          table_members, class_name):
    uncreated_program_tags = set([table_members[x] for x in only_table_members]).difference(set(tags.keys()))
    members_for_uncreated_tags = [[member for member in only_table_members if table_members[member] == tag]
                                  for tag in uncreated_program_tags]
    members_for_created_tags = [member for member in only_table_members if
                                table_members[member] not in uncreated_program_tags]

    program_tags_ids = list(map(partial(API.create_tag, classes_in_organization[class_name]),
                                uncreated_program_tags, members_for_uncreated_tags))
    list(map(lambda x, y: tags.update({x: y}), uncreated_program_tags, program_tags_ids))

    list(map(partial(add_member_to_tag,
                     classes_in_organization[class_name],
                     tags, table_members),
             members_for_created_tags))


def populate_subgroup_tags(tags, class_name, only_table_members, members_number):
    subgroup_tags = [tag for tag in tags.keys() if "Подгруппа" in tag]

    if len(subgroup_tags) == 0:
        subgroup_tags = [f"Подгруппа_{i}" for i in range(1, Variables.number_of_subgroups + 1)]
        members = np.array(get_class_members(class_name))
        while len(members) != members_number:
            time.sleep(3)
            members = np.array(get_class_members(class_name))
            print('here!')

        np.random.shuffle(members)
        subgroup_members = np.array_split(members, len(subgroup_tags))

        list(map(partial(API.create_tag, classes_in_organization[class_name], has_id=True),
                 subgroup_tags, subgroup_members))
    else:
        subgroup_tags_length = [len(x) for x in list(map(partial(API.get_tag_members,
                                                                 classes_in_organization[class_name]),
                                                         [tags[x] for x in subgroup_tags]))]
        np.random.shuffle(only_table_members)

        for i in range(len(subgroup_tags)):
            while subgroup_tags_length[i] != max(subgroup_tags_length):
                if len(only_table_members) == 0:
                    break
                API.add_member_to_tag(classes_in_organization[class_name],
                                      tags[subgroup_tags[i]],
                                      only_table_members.pop())

        subgroup_members = np.array_split(only_table_members, len(subgroup_tags))
        for i in range(len(subgroup_tags)):
            list(map(partial(API.add_member_to_tag,
                             classes_in_organization[class_name],
                             tags[subgroup_tags[i]]),
                     subgroup_members[i]))


def sync_class(class_element):
    global classes_in_organization

    class_name, table_members = class_element
    table_members_emails = set(table_members.keys())
    table_members_tags = set(table_members.values())

    if class_name not in classes_in_organization:
        classes_in_organization[class_name] = API.create_class(class_name, 'aglushko@ithse.ru')

    class_members = dict(map(lambda x: (x['userPrincipalName'], x['id']),
                             get_class_members(class_name)))
    class_members_emails = set(class_members.keys())

    only_table_members = list(table_members_emails.difference(class_members_emails))
    only_class_members = class_members_emails.difference(table_members_emails)

    pool = ThreadPool()
    pool.map(partial(add_member_to_class,
                     class_id=classes_in_organization[class_name]),
             only_table_members)
    pool.close()
    tags = API.get_tags_in_class(classes_in_organization[class_name])

    pool.join()
    # Updating tags in class
    populate_program_tags(tags, only_table_members,
                          table_members, class_name)
    populate_subgroup_tags(tags, class_name, only_table_members,
                           len(class_members) + len(only_table_members))


def sync_class_to_table(df, only_tabel_members, class_name):
    local_df = df.loc[df['Команда MS Teams'] == class_name]
    emails = set(local_df['Почта'].tolist())
    class_members = dict(map(lambda x: (x['userPrincipalName'], x['id']),
                             get_class_members(class_name)))

    only_tabel_members.extend(emails.difference(set(class_members.keys())))


def add_all_table_members_to_list(df, only_tabel_members, class_name):
    local_df = df.loc[df['Команда MS Teams'] == class_name]
    elems = list(local_df.itertuples(index=False, name=None))

    only_tabel_members.extend(elems)


def add_all_teams_members_to_list(only_teams_members, class_name):
    class_members = list(map(lambda x: x['userPrincipalName'],
                             get_class_members(class_name)))

    for email in class_members:
        only_teams_members.append([email, None, class_name, 0])


def sync_classes_with_table(table_rows):
    global classes_in_organization
    classes_in_organization = dict(map(lambda x: (x['displayName'], x['id']),
                                       API.get_classes_in_organization()))

    teams_map = defaultdict(dict)
    for Email, Program, TeamsGroup, Status in [i for i in table_rows if i[3]]:
        teams_map[TeamsGroup][Email] = Program

    pool = ThreadPool()
    res = pool.map(sync_class, teams_map.items())

    pool.close()
    pool.join()


def sync_table_with_classes(excel_table):
    global classes_in_organization
    if Variables.syncs[Variables.selected_sync_ind] == 'Hard':
        excel_table = excel_table[0:0]
    classes_in_organization = dict(map(lambda x: (x['displayName'], x['id']),
                                       API.get_classes_in_organization()))
    classes_in_table = set(excel_table['Команда MS Teams'].unique())

    only_table_classes = classes_in_table.difference(set(classes_in_organization.keys()))
    only_teams_classes = set(classes_in_organization.keys()).difference(classes_in_table)

    only_table_members = []
    only_teams_members = []

    pool_only_table_classes = ThreadPool()
    res = pool_only_table_classes.map(functools.partial(add_all_table_members_to_list,
                                                        excel_table,
                                                        only_table_members),
                                      only_table_classes)
    pool_only_table_classes.close()
    pool_only_table_classes.join()

    arr = []
    for i in only_table_members:
        for j in excel_table.loc[(excel_table['Почта'] == i[0]) &
                                 (excel_table['Команда MS Teams'] == i[2])].iterrows():
            arr.append(j[1].to_dict())

    pool_only_teams_classes = ThreadPool()
    res = pool_only_teams_classes.map(functools.partial(add_all_teams_members_to_list,
                                                        only_teams_members),
                                      only_teams_classes)

    pool = ThreadPool()
    res = pool.map(functools.partial(sync_class_to_table,
                                     excel_table,
                                     only_table_members),
                   classes_in_organization)

    pool.close()
    pool_only_teams_classes.close()

    pool.join()
    pool_only_teams_classes.join()

    for i in only_teams_members:
        excel_table = excel_table.append(pd.Series(i,
                                                   index=['Почта', 'ОП', 'Команда MS Teams', 'Статус']),
                                         ignore_index=True)
    excel_table = excel_table.style.apply(highlight_bad_rows, bad_elems=arr, axis=1)
    return only_table_members, excel_table
