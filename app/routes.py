import os
import pandas as pd

from datetime import datetime, timedelta, timezone
from flask import Flask
from flask import current_app as app
from flask import request
from flask import render_template, flash, redirect, url_for, jsonify
#from flask import Blueprint
from werkzeug.utils import secure_filename
from sqlalchemy.exc import SQLAlchemyError

from . import db
from .models import User, Group


#main = Blueprint('main', __name__)

@app.route('/')
def index():
    # 获取所有用户和组
    users = User.query.all()
    groups = Group.query.all()

    # 更新每个组的 first_register 和 last_register
    for group in groups:
        group_users = [user for user in users if user.group_id == group.id]
        if group_users:
            #group.first_regist = min(user.registered_on for user in group_users)
            #group.last_regist = max(user.registered_on for user in group_users)
            first_registered_user = min(group_users, key=lambda user: user.registered_on)
            last_registered_user = max(group_users, key=lambda user: user.registered_on)
            group.first_regist = first_registered_user.registered_on
            group.last_regist = last_registered_user.registered_on
            group.last_register_name = last_registered_user.name
        else:
            group.first_register = None
            group.last_register = None
    db.session.commit()

    ###### filter user by id ######
    user_min_id = request.args.get('min_id', default=1, type=int)
    user_max_id = request.args.get('max_id', default=999999, type=int)
    print(f"Selecting user:\n ID between {user_min_id} and {user_max_id}.")
    user_id_query = User.query.filter(User.id.between(user_min_id, user_max_id))

    ###### filter user by group ######
    group_ids = request.args.getlist('group_select', type=int)    # 根据 name 属性选择
    print(f"Selecting user:\n in group {group_ids}")
    if group_ids:
        user_id_query = user_id_query.filter(User.group_id.in_(group_ids))
    # 获取 query 内容
    filtered_users = user_id_query.all()

    ###### filter group by date ######
    group_start_date = request.args.get('start_date', default='2000-01-01', type=str)
    group_end_date = request.args.get('end_date', default=datetime.today().strftime('%Y-%m-%d'), type=str)
    print(f"Selecting group:\n created from {group_start_date} to {group_end_date}.")
    filtered_groups = Group.query.filter(Group.created_on.between(
        datetime.strptime(group_start_date, '%Y-%m-%d').date(), 
        datetime.strptime(group_end_date, '%Y-%m-%d').date() + timedelta(days=1))).all()
    
    return render_template('index.html', 
                           users=filtered_users, 
                           groups=filtered_groups,
                           group_ids=group_ids)

######## 处理 User ########

# 确保日期格式为 <class 'datetime.datetime'>
def date_for_sqlite(meta_date:str) -> datetime:
    if meta_date == '':
        new_date = datetime.now(timezone.utc)
    else:
        new_date = datetime.strptime(meta_date, '%Y-%m-%d')
    return new_date

@app.route('/add_user', methods=['POST'])
def add_user():
    data = request.json
    new_name = data['name']
    new_date = data['registered_on']
    group_id = data['group_id'] if data['group_id'] != 'None' else None
    print(f"Adding new user\n—— named '{new_name}'\n—— registered on {new_date}\n—— in group {group_id}")
    new_user = User(name=new_name, registered_on=date_for_sqlite(new_date), group_id=group_id)
    db.session.add(new_user)
    db.session.commit()
    return jsonify(success=True)

@app.route('/delete_user/<int:id>', methods=['DELETE'])
def delete_user(id):
    user = User.query.get(id)
    #user = session.get(User, id)
    print(f"Deleting user {id}: {user.name}")
    db.session.delete(user)
    db.session.commit()
    return jsonify(success=True)

@app.route('/edit_user/<int:id>', methods=['POST'])
def edit_user(id):
    data = request.json
    new_name = data['name']
    new_date = data['registered_on']
    new_group_id = data['group_id']
    # 
    try:
        new_group_id = int(new_group_id)
    except ValueError:
        return jsonify(success=False, message="Invalid group_id"), 400
    # 正常修改对象实例
    user = User.query.get(id)
    #group = session.get(Group, id)
    if user:
        print(f"Modifying user {id} to\n—— name: '{new_name}'\n—— registered on {new_date}\n—— to group {new_group_id} (type: {type(new_group_id)})")
        user.name = new_name
        user.registered_on = date_for_sqlite(new_date)
        user.group_id = new_group_id
        db.session.commit()
        return jsonify(success=True), 200
    # id错误
    return jsonify(success=False, message=f"User {id} not found"), 404

######## 处理 Group ########

@app.route('/add_group', methods=['POST'])
def add_group():
    data = request.json
    new_name = data['name']
    new_date = data['created_on']
    print(f"Adding new group\n—— named: '{new_name}'\n—— created on {new_date}")
    # 判断group名是否已存在
    existing_group = Group.query.filter_by(name=new_name).first()
    if existing_group:
        return jsonify({'success': False, 'message': 'Group name already exists'}), 400
    new_group = Group(name=new_name, created_on=date_for_sqlite(new_date))
    db.session.add(new_group)
    db.session.commit()
    return jsonify(success=True), 200

@app.route('/delete_group/<int:id>', methods=['DELETE'])
def delete_group(id):
    '''
    group = Group.query.get(id)
    #group = session.get(Group, id)
    print(f"Deleting group {id}: {group.name}")
    db.session.delete(group)
    db.session.commit()
    return jsonify(success=True)
    '''
    try:
        group = Group.query.get(id)
        if not group:
            return jsonify({'message': 'Group not found'}), 404
        print(f"Deleting group {id}: {group.name}")
        # 更新所有关联的 User 实例的 group_id
        users_to_update = User.query.filter(User.group_id == id).all()
        for user in users_to_update:
            user.group_id = 0
        # 提交用户更新
        db.session.commit()
        print(f"Updated all users associated with group_id {id} to 0")
        # 删除 Group 实例
        db.session.delete(group)
        db.session.commit()
        print(f"Deleted group {id}")
        return jsonify(success=True), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Error deleting group: {e}")
        return jsonify({'message': 'An error occurred while deleting the group'}), 500


@app.route('/edit_group/<int:id>', methods=['POST'])
def edit_group(id):
    data = request.json
    new_name = data['name']
    new_date = data['created_on']
    # 判断是否存在其他名称相同的实例
    existing_group = Group.query.filter_by(name=new_name).first()
    if existing_group and existing_group.id != id:
        return jsonify(success=False, message="Group name already exists"), 400
    # 正常修改对象实例
    group = Group.query.get(id)
    #group = session.get(Group, id)
    if group:
        print(f"Modifying group {id} to\n—— name: '{new_name}'\n—— created on {new_date}")
        group.name = new_name
        group.created_on = date_for_sqlite(new_date)
        db.session.commit()
        return jsonify(success=True), 200
    # id错误
    return jsonify(success=False, message=f"Group {id} not found"), 404

######## 处理文件上传 ########

# 验证文件扩展名
def allowed_file(filename:str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'csv', 'xlsx'}

# 根据上传的数据 DataFrame 更新表格
def update_groups_from_dataframe(df:pd.DataFrame) -> None:
    # 逐条遍历 DataFrame
    for _, row in df.iterrows():
        group_id = row['id']
        group_name = row['name']
        created_on = row['created_on']
        #first_register = row.get('first_register')
        #last_register = row.get('last_register')

        # 尝试根据 id 获取数据库中已有实例
        group = Group.query.get(group_id)
        if group is None:
            # 不存在同 id 实例则添加
            group = Group(id=group_id, name=group_name, created_on=created_on)
            print(f"Add new instance: {group}")
            db.session.add(group)
        else:
            # 存在同 id 实例则更新部分属性
            print(f"Update instance: {group}")
            group.name = group_name
            group.created_on = created_on
            #group.first_register = first_register
            #group.last_register = last_register
            pass
        db.session.commit()

@app.route('/upload', methods=['POST'])
def upload_file():
    # 检查请求中是否包含文件，如果不存在，显示错误信息并重定向回上传页面
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    # 如果文件名为空，显示错误信息并重定向回上传页面
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    # 验证文件后缀
    if file and allowed_file(file.filename):
        # 确保上传的文件名是安全的，并移除任何可能导致安全问题的字符
        filename = secure_filename(file.filename)
        # 构建文件路径
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # 处理文件
        if filename.endswith('.csv'):
            df = pd.read_csv(filepath, parse_dates=['created_on'])
        elif filename.endswith('.xlsx'):
            df = pd.read_excel(filepath, parse_dates=['created_on'])
        else:
            flash('Unsupported file format')
            return redirect(request.url)

        # 将文件内容更新到数据库
        update_groups_from_dataframe(df)
        flash('File successfully uploaded and processed')
        return redirect(url_for('index'))

    flash('File type not allowed')
    return redirect(request.url)