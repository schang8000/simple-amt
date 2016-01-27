__author__ = 'shuo chang'

import requests
import json
import pymysql
import random
from random import shuffle
import os
import time
import glob

API_URL = 'https://movielens.org/api/email'
API_POST_HEADERS = {'content-type': 'application/json'}
API_TOKEN = r'6#ST%DecK3vHdps*r8eQ2bTw'
DB_HOST = 'movielens.cs.umn.edu'
DB_PORT = 3306
DB_USER = 'readonly'
DB_PASS = ''
DB_NAME = 'ML3'
MAPPER_N_USERS = 600
BATCH = 100
MAPPER_USR_FILES = '../mapper/batch_*.txt'


def send_mail(n):
    """
    Send emails to a group of movielens users for mapper.
    """
    if not os.path.exists('all_users_ids.txt'):
        con = pymysql.connect(DB_HOST, user=DB_USER, port=DB_PORT, db=DB_NAME, password=DB_PASS)
        with con.cursor() as cur:
            cur.execute('select distinct(userId) from user_login where tstamp > "2014-11-01"')
            recent_users = set([row[0] for row in cur.fetchall()])
            cur.execute('select userId from (select userId, count(*) as cc from user_rating_pairs group by userId) as A where A.cc > 14')
            users_with_enough_ratings = set([row[0] for row in cur.fetchall()])
            candidates = list(recent_users - users_with_enough_ratings)
            shuffle(candidates)
            with open('all_users_ids.txt', 'w') as f:
                for u in candidates:
                    f.write(str(u) + '\n')
    else:
        candidates = []
        with open('all_users_ids.txt', 'r') as f:
            for line in f:
                candidates.append(int(line.strip()))
    start_idx = BATCH * (n-1)
    end_idx = BATCH * n
    # users_to_mail = recent_users[start_idx:end_idx]
    users_to_mail = [221192]
    with open('batch_{}.txt'.format(n), 'w') as f:
        for u in users_to_mail:
            f.write(str(u) + '\n')

    msg = """
    Dear MovieLens user,\n
    \n
    As part of a research project, we are designing a way to explain movie recommendations.
    We'd like your help to take a survey. The survey takes about 10 minutes.\n
    \n
    http://movielens.org/go/expl\n
    \n
    Thanks for your help making MovieLens great!\n
    \n
    Steven Chang\n
    --Ph.D. student with the MovieLens research group
    """
    html_msg = """
    <p>Dear MovieLens user,</p>
    <p>
    As part of a <strong>research project</strong>, we are designing a way to <strong>explain movie recommendations</strong>.
    We'd like your help to take a survey.
    The survey takes about <strong>10 minutes</strong>.
    </p>
    <a href="http://movielens.org/go/expl">http://movielens.org/go/expl</a>
    <p>
    Thanks for your help making MovieLens great!
    </p>
    Steven Chang<br />
    --Ph.D. student with the MovieLens research group
    <div>
    <a href="https://movielens.org/profile/settings/notifications">Unsubscribe</a>
    </div>
    """
    notes = "CrowdLens Eval Email"
    exptId = "explanation"
    with open('batch_{}_log.txt'.format(n), 'a') as f:
        for userId in users_to_mail:
            tmp = "sending to userId %s" % userId
            print tmp
            f.write(tmp+'\n')
            data = {
                'userId': userId,
                'subject': 'MovieLens needs your help',
                'from': 'movielens-info@movielens.umn.edu',
                'emailer': 'mailgun',
                'reply-to': 'schang@cs.umn.edu',
                'textMessage': msg,
                'htmlMessage': html_msg,
                'notes': notes,
                'exptId': exptId,
                'ignoreMinCutoffDate': True,
                'token': API_TOKEN
            }
            r = requests.post(API_URL, data=json.dumps(data), headers=API_POST_HEADERS, verify=True)
            print(r.text)
            f.write(r.text + '\n')
            time.sleep(1)

if __name__ == "__main__":
    send_mail(1)
