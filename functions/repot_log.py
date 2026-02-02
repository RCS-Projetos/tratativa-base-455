import os
from dotenv import load_dotenv
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
env_path = os.path.join(project_root, '.env')
load_dotenv(dotenv_path=env_path)

BASE_URL = os.getenv('BASE_URL')

url_path = lambda x: f'{BASE_URL}{x}'

headers = {
    "Content-Type": "application/json" # Remova se não usar auth
}

def make_report_log(report: str, status: str['STARTED', 'COMPLETED', 'ERROR'], req_type: str['post', 'patch'], id = None):
    
    if req_type == 'post':
        resp = req.post(url_path('/report_type'), json={
        "report_type": report,
        "status": status
    }, headers=headers)
    elif req_type == 'patch':
        resp = req.patch(url_path(f'/report_type/{id}'), json={
        "report_type": report,
        "status": status
    }, headers=headers)

    return resp
    