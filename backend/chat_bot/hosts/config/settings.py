# config/settings.py
REMOTE_AGENTS = {
    'auto_recommend': {
        'port': 10010,
        'description': 'automobile recommendation agent',
        'module': 'remotes.auto_recommend'
    },
    'loan_suggest': {
        'port': 10020,
        'description': 'loan suggestion agent',
        'module': 'remotes.loan_suggest'
    },
    'loan_pre-examination': {
        'port': 10030,
        'description': 'loan pre-examination agent',
        'module': 'remotes.loan_pre-examination'
    },
}

API_CONFIG = {
    'host': '0.0.0.0',
    'port': 9001,
    'timeout': 30
}