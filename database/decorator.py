from functools import wraps
from .engine import async_session, engine
from .schema import DataSchema

def async_update_to_db(table_class: DataSchema, db_session = async_session, always_new = True, always_sql = False):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):

            ####### if always_new = False ##########
            if always_new == False:
                result = load_from_saved(table_class, db_session, args, kwargs)
                if len(result) == 0:
                    pass
                elif len(result) == 1:
                    return result[0]
                else:
                    return result
                    
            # 如果 alway_new == True 或者 数据库无对应查询
            datas = await func(*args, **kwargs)
            if type(datas) == dict:
                records_and_update(table_class, db_session, datas)
            elif type(datas) == list and len(datas) > 0:
                for data_row in datas:
                    records_and_update(table_class, db_session, data_row)
            elif type(datas) == list and len(datas) == 0:
                pass
            else:
                print('API 异常, 无法保存到DB')


            ####### if always_sql = True #########
            if always_sql == True:
                result = load_from_saved(table_class, db_session, args, kwargs)
                if len(result) == 0:
                    pass
                elif len(result) == 1:
                    return result[0]
                else:
                    return result


            return datas

        return wrapper
    return decorator



