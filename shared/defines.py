import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TOKEN = 'auth/token'
vURL = 'https://{host}/api/{version}/{path}'
URL = 'https://{host}/api/{path}'

LAG_TYPE_PROVISIONED = 'provisioned'
LAG_TYPE_INTERNAL = 'internal'

SWITCH_ROLE_SPINE = 'spine'
SWITCH_ROLE_LEAF = 'leaf'
SWITCH_ROLE_BORDER_LEAF = 'border_leaf'