import os
import random
from datetime import datetime, timezone, timedelta


def generate_random_date(roll_back:int) -> datetime:
    some_day = datetime.now(timezone.utc) - timedelta(days=random.randint(1, roll_back))
    return some_day

# 确保日期格式为 <class 'datetime.datetime'>
def date_for_sqlite(meta_date:str) -> datetime:
    if meta_date == '':
        new_date = datetime.now(timezone.utc)
    else:
        new_date = datetime.strptime(meta_date, '%Y-%m-%d')
    return new_date

# 根据类名和实例日期生成id
def date_to_id(model_name, date, sequence_number):
    date_str = date.strftime("%Y%m%d")
    return f"{model_name}-{date_str}-{sequence_number:03d}"

# 验证文件扩展名
def allowed_file(filename:str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'csv', 'xlsx'}