from datetime import datetime, timezone

#from app import db  # 导入已经创建的 db 实例而不是重新创建 SQLAlchemy


class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    create_on = db.Column(db.DateTime, default=datetime.now(timezone.utc))

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    registed_on = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=True)
    # 反向关系?
    group = db.relationship('Group', backref=db.backref('users', lazy=True))