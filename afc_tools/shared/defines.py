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

PATCH_OP_ADD = 'add'
PATCH_OP_REMOVE = 'remove'
PATCH_OP_REPLACE = 'replace'

NEIGHBOR_TYPE_LLDP = 'lldp'
NEIGHBOR_TYPE_CDP = 'cdp'
NEIGHBOR_TYPE = (NEIGHBOR_TYPE_CDP, NEIGHBOR_TYPE_LLDP)

PATCH_OPS = (PATCH_OP_ADD, PATCH_OP_REMOVE, PATCH_OP_REPLACE)
