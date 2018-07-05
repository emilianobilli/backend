RETURN_ERROR = -1
RETURN_OK = 0
STATUS_QUEUE = 'Q'
STATUS_PUBLISH= 'P'
FLAG_SUCCESS = 'success'
FLAG_ALERT = 'alert'


BLOCK_TYPE = (
    ('S', 'Static'),
    ('D', 'Dynamic')
)

PACKAGE_DURATION = (
        ('1', '1 Mes'),
        ('6', '6 Meses'),
    )

PACKAGE_DURATION_VIEW = {
        '1': '1 Mes',
        '6': '6 Meses',
}

RULES = {'H': 'HotGo Registration Page',
         'P': 'Provider Registration Page',
         'D': 'Default Page'}