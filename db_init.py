import random
from datetime import datetime, timezone, timedelta

from app import app, db
from app import User, Group


names = ["Peter", "Stewie", "Brian", "Lois", "Meg", "Chris"]
groups = ['Group A', 'Group B', 'Group C']


def generate_random_date(roll_back:int) -> datetime:
    some_day = datetime.now(timezone.utc) - timedelta(days=random.randint(1, roll_back))
    return some_day    


def init_db():

    with app.app_context():

        print("Dropping all tables...")
        db.drop_all()
        print("Tables dropped.")
        print("Creating all tables...")
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
                    registed_on=generate_random_date(7), 
                    group_id=random.choice(group_ids) if random.random() > 0.5 else None
                )
                db.session.add(user)
            db.session.commit()

if __name__ == '__main__':
    
    init_db()