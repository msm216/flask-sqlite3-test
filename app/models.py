from datetime import datetime, timezone
from sqlalchemy import event
from sqlalchemy.exc import SQLAlchemyError

from . import db


class Group(db.Model):

    __tablename__ = 'group_table'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False, unique=True)
    # 可调用对象 lambda 确保每次实例化时都会重新获得当前日期时间，而不是服务器启动时的日期时间
    created_on = db.Column(db.Date, default=lambda: datetime.now(timezone.utc).date())
    first_regist = db.Column(db.Date, nullable=True)
    last_regist = db.Column(db.Date, nullable=True)
    last_register_name = db.Column(db.String(80), nullable=True)
    # 反向关联，lazy='dynamic' 使得反向关系被访问时返回一个对象而不是列表
    users = db.relationship('User', backref='user_group', lazy=True)

    def __repr__(self):
        return f'<Group: {self.name}>'

class User(db.Model):

    __tablename__ = 'user_table'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    registered_on = db.Column(db.Date, default=lambda: datetime.now(timezone.utc).date())
    group_id = db.Column(db.Integer, db.ForeignKey('group_table.id'), default=0)
    #group = db.relationship('Group', backref=db.backref('users', lazy=True))

    def __repr__(self):
        return f'<User: {self.name}>'
    

@event.listens_for(Group, 'before_delete')
def update_user_group_ids(mapper, connection, target):
    try:
        print(f"About to delete group with id: {target.id}, name: {target.name}")

        # 使用 connection 执行更新操作，而不是使用 session 提交事务
        connection.execute(
            User.__table__.update().
            where(User.group_id == target.id).
            values(group_id=0)
        )
        print(f"Updated all users associated with group_id {target.id} to 0")

    except SQLAlchemyError as e:
        print(f"Error in update_user_group_ids: {e}")