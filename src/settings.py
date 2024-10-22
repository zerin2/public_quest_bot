import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

TELEGRAM_TOKEN: Optional[str] = os.getenv('TELEGRAM_TOKEN')

DATABASES = {
    'APP': {
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
        'URL': os.getenv('DATABASE_URL')
    }
}

ACT_CODE = {
    'default': '000',
    '1': '100',
    '2': '110',
    '3': '111',
    'final': 'final',
    'present': 'present'
}
ACT_STATE = {
    'pre_check': 'pre_check',
    'start': 'start',
    'default': 'default_scene',
    '1': 'first_act',
    '2': 'second_act',
    '3': 'third_act',
    'final': 'final',
    'present': 'present',
}
