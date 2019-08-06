import mysql.connector


def write_to_db(event_info, user_info):
    cntr = mysql.connector.connect(host=user_info['host'],
                                   user=user_info['user'],
                                   password=user_info['password'],
                                   database=user_info['db_name'],
                                   auth_plugin='mysql_native_password')
    cursor = cntr.cursor()
    # 检测活动数据是否已经存在,利用传入活动名称不存在于数据表时，返回list长度为0
    cursor.execute('SELECT event_name FROM event WHERE event_name = %s', (event_info[0],))
    guarantee = cursor.fetchall()
    if len(guarantee):
        pass
    else:
        cursor.execute('INSERT INTO'
                       ' event (event_name, event_type, bonus_type, bonus_members,'
                       ' new_rank_four_members, start_time, end_time) VALUES (%s, %s, %s, %s, %s, %s, %s)',
                       event_info)
        # 提交活动数据
        cntr.commit()
    cntr.close()


