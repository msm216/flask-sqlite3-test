import os
import random

from datetime import datetime, timezone, timedelta
from sqlalchemy.exc import IntegrityError

#from app import app, db
from app import create_app, db
from app.models import User, Group
from app.utilities import date_to_id, generate_random_date


# 用户和组名称列表
users = ["Peter", "Stewie", "Brian", "Lois", "Meg", "Chris"]
groups = ['Group A', 'Group B', 'Group C']

def init_db():
    #
    app = create_app()

    with app.app_context():

        # 关闭会话
        db.session.remove()
        
        #db_path = 'instance\\app.db'
        db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')

        if os.path.exists(db_path):
            os.remove(db_path)
            print(f'Database file removed: {db_path}')
        else:
            print(f'Database file {db_path} not found.')

        db.drop_all()
        print("Tables dropped.")
        db.create_all()
        print("Tables created.")
        
        # 检查 Group 表是否已有数据
        if not Group.query.first():
            for group_name in groups:
                new_date = generate_random_date(60)
                group = Group(
                    name=group_name, 
                    created_on=new_date,
                )
                db.session.add(group)
            db.session.commit()

        # 获取当前 Group 模型内所有实例的id
        group_ids = [group.id for group in Group.query.all()]

        # 检查 User 表是否已有数据
        if not User.query.first():
            for user_name in users:
                user = User(
                    name=user_name, 
                    registered_on=generate_random_date(7), 
                    # 随机概率0.5不分到任何组
                    group_id=random.choice(group_ids) if random.random() > 0.3 else 0
                )
                db.session.add(user)
            db.session.commit()


if __name__ == '__main__':
    
    #init_db()
    app = create_app()

    with app.app_context():

        # 关闭会话
        db.session.remove()
        
        #db_path = 'instance\\app.db'
        db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')

        if os.path.exists(db_path):
            os.remove(db_path)
            print(f'Database file removed: {db_path}')
        else:
            print(f'Database file {db_path} not found.')

        db.drop_all()
        print("Tables dropped.")
        db.create_all()
        print("Tables created.")

        # 创建组实例
        group_instances = []
        for group_name in groups:
            created_date = generate_random_date(60)  # 在过去30天内生成随机日期
            group_sequence_number = Group.query.filter(db.func.date(Group.created_on) == created_date.date()).count() + 1
            group_id = date_to_id("Group", created_date, group_sequence_number)
            new_group = Group(id=group_id, name=group_name, created_on=created_date)
            print(f"Group {group_id} named {group_name} created on {created_date} added.")
            group_instances.append(new_group)
            db.session.add(new_group)
        try:
            # 提交组实例到数据库
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            print(f"Error occurred while committing groups: {e}")

        # 创建用户实例并随机分配组
        for user_name in users:
            registered_date = generate_random_date(30)  # 在过去30天内生成随机日期
            user_sequence_number = User.query.filter(db.func.date(User.registered_on) == registered_date.date()).count() + 1
            user_id = date_to_id("User", registered_date, user_sequence_number)
            new_user = User(id=user_id, name=user_name, registered_on=registered_date)
            # 为66%的用户随机分配一个组
            if random.random() < 0.66:
                new_user.group_id = random.choice(group_instances).id
            print(f"User {user_id} named {user_name} registered to group {new_user.group_id} on {registered_date} added.")
            db.session.add(new_user)
        try:
            # 提交用户实例到数据库
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            print(f"Error occurred while committing users: {e}")