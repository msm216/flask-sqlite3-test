import os
import random

from flask import Flask
from flask import request
from flask import render_template, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.inspection import inspect
from datetime import datetime, timezone, timedelta


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Ticket(db.Model):
    __tablename__ = 'ticket_table'
    id = db.Column(db.String(32), primary_key=True)
    title = db.Column(db.String(64), unique=True)
    # lazy='dynamic' 使得 ticket_1.tasks 和 ticket_2.tasks 返回一个查询对象（而不是一个列表），可以在这个查询对象上调用额外的过滤和排序方法
    # SELECT tasks.id AS tasks_id, tasks.description AS tasks_description, tasks.ticket_id AS tasks_ticket_id FROM tasks WHERE ? = tasks.ticket_id
    #tasks = db.relationship('Task', backref='related_ticket', lazy='dynamic')
    tasks = db.relationship('Task', backref='related_ticket', lazy=True)

    def __repr__(self):
        return f'<Ticket Instance: {self.title}>'

class Task(db.Model):
    __tablename__ = 'task_table'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(64), unique=True, index=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('ticket_table.id'))

    def __repr__(self):
        return f'<Task Instance: {self.description}>'


# 创建数据库和表
with app.app_context():
    db.drop_all()
    db.create_all()

ticket_columns = inspect(Ticket).columns
task_columns = inspect(Task).columns

# 创建示例数据
with app.app_context():
    ticket_1 = Ticket(id='RW2401050298', title='The1stTicket')
    ticket_2 = Ticket(id='UP2405270806', title='The2ndTicket')
    db.session.add_all([ticket_1, ticket_2])
    db.session.commit()

    # related_ticket 参数来自于 Ticket.tasks 的反向关联，可以直接用于访问 Ticket 对象
    task_1 = Task(description='TheTask1', related_ticket=ticket_1)
    task_2 = Task(description='TheTask2', related_ticket=ticket_2)
    task_3 = Task(description='TheTask3', related_ticket=ticket_2)
    db.session.add_all([task_1, task_2, task_3])
    db.session.commit()

    print("读取全部 Ticket")
    ticket_list = Ticket.query.all()
    print(f"{ticket_columns.id.key}|{ticket_columns.title.key}")
    for ticket in ticket_list:
        print(f"{ticket.id}|{ticket.title}")
        print(f"{ticket.tasks}")

    print("读取全部 Task")
    task_list = Task.query.all()
    print(f"{task_columns.id.key}|{task_columns.description.key}|{task_columns.ticket_id.key}")
    for task in task_list:
        print(f"{task.id}|{task.description}|{task.ticket_id}")

    print("通过 Ticket 访问 Task")
    try:
        # lazy='dynamic'
        print(ticket_1.tasks.all())  # 输出: [<Task Instance: The task 1>]
        print(ticket_2.tasks.all())   # 输出: [<Task Instance: The task 2>, <Task Instance: The task 3>]
    except AttributeError as e:
        # lazy=True
        print(ticket_1.tasks)  # 输出: [<Task Instance: The task 1>]
        print(ticket_2.tasks)   # 输出: [<Task Instance: The task 2>, <Task Instance: The task 3>]

    print("通过 Task 访问 Ticket")
    print(task_1.related_ticket)  # 输出: <Ticket Instance: The 1st ticket>
    print(task_2.related_ticket)  # 输出: <Ticket Instance: The 2nd ticket>
    print(task_3.related_ticket)  # 输出: <Ticket Instance: The 2nd ticket>


