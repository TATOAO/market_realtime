from ast import main
import subprocess
import os
import sys
from time import sleep
import re
import dotenv

if os.path.exists('docker/.env'):
    dotenv.load_dotenv('docker/.env')
else:
    dotenv.load_dotenv()


def edit_xml_fields(
    file_path: str = './futu/Futu_OpenD_9.3.5308_Mac/Futu_OpenD_9.3.5308_Mac/FutuOpenD.xml',
    user_id: str = None,
    port: str = None,
    md5_password: str = None
):
    """
    Edit the XML file to update user_id, port, and/or md5_password fields.
    Only fields provided (not None) will be updated.
    """
    with open(file_path, 'r') as file:
        content = file.read()

    if user_id is not None:
        content = re.sub(r'<login_account>.*</login_account>', f'<login_account>{user_id}</login_account>', content)
    if port is not None:
        content = re.sub(r'<api_port>.*</api_port>', f'<api_port>{port}</api_port>', content)
    if md5_password is not None:
        content = re.sub(r'<login_pwd_md5>.*</login_pwd_md5>', f'<login_pwd_md5>{md5_password}</login_pwd_md5>', content)

    with open(file_path, 'w') as file:
        file.write(content)


def open_futu_client():
    # ./futu/Futu_OpenD_9.3.5308_Mac/Futu_OpenD_9.3.5308_Mac/FutuOpenD.xml
    # ./futu/Futu_OpenD_9.3.5308_Mac/Futu_OpenD_9.3.5308_Mac/FutuOPenD.app/Contents/MacOS/FutuOpenD
    # run the app in the background
    subprocess.Popen(['./futu/Futu_OpenD_9.3.5308_Mac/Futu_OpenD_9.3.5308_Mac/FutuOPenD.app/Contents/MacOS/FutuOpenD'])



def init_futu_client():
    user_id_list = os.getenv('futu_user_id_list').split(',')
    port_list = os.getenv('futu_user_port_list').split(',')
    password_list = os.getenv('futu_user_password_list').split(',')
    # 1. edit the xml file with the user id
    for user_id, port, password in zip(user_id_list, port_list, password_list):
        edit_xml_fields(user_id=user_id, port=port, md5_password=password)
        open_futu_client()
        sleep(5)


# python -m apps.stock_monitor_backend.app.utils.open_futu_client
if __name__ == '__main__':
    init_futu_client()