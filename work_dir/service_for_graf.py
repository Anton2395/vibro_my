def generate_column(table_name: str):
    if table_name in ['datchik_3_axel', 'datchik_4_axel', 'datchik_5_axel']:
        return ('axel_time, axel', 'axel_time')
    elif table_name in ['datchik_3_temp', 'datchik_4_temp', 'datchik_5_temp']:
        return ('temp_time, temp', 'temp_time')
    else:
        return ("trunc(date_part('epoch',now_time)*1000), value", 'now_time')


def get_table_name(marker: str):
    if marker == 'vibr3':
        return 'datchik_3_axel'
    elif marker == 'vibr4':
        return 'datchik_4_axel'
    elif marker == 'vibr5':
        return 'datchik_5_axel'
    elif marker == 'temp3':
        return 'datchik_3_temp'
    elif marker == 'temp4':
        return 'datchik_4_temp'
    elif marker == 'temp5':
        return 'datchik_5_temp'
    elif marker == 'vibr44':
        return 'datchik_44_axel'
    elif marker == 'temp44':
        return 'datchik_44_temp'
    else:
        return None