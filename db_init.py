import random
import os

from datetime import datetime, timezone, timedelta

#from app import app, db
from app import create_app, db
from app.models import User, Group


names = ["Peter", "Stewie", "Brian", "Lois", "Meg", "Chris"]
groups = ['Group A', 'Group B', 'Group C']


def generate_random_date(roll_back:int) -> datetime:
    some_day = datetime.now(timezone.utc) - timedelta(days=random.randint(1, roll_back))
    return some_day    


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
            for group in groups:
                group = Group(
                    name=group, 
                    created_on=generate_random_date(60)
                )
                db.session.add(group)
            db.session.commit()

        # 获取当前 Group 模型内所有实例的id
        group_ids = [group.id for group in Group.query.all()]

        # 检查 User 表是否已有数据
        if not User.query.first():
            for name in names:
                user = User(
                    name=name, 
                    registered_on=generate_random_date(7), 
                    # 随机概率0.5不分到任何组
                    group_id=random.choice(group_ids) if random.random() > 0.3 else 0
                )
                db.session.add(user)
            db.session.commit()

if __name__ == '__main__':
    
    init_db()