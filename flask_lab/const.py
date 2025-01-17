

import os

APP_NAME = 'Flask Lab'
APP_VERSION = "1.0.2"
ROOT_PATH, _ = os.path.split(os.path.realpath(__file__))
STATUS = {0: 'new', 1: 'in progress', 2: 'waiting for customer', 3: 'done', 4: 'cenceled'}
PC_KIND = {0: 'PC', 1: 'Laptop', 2: 'Tablet', 3: 'All in One'}
COLORS = {0: 'Black', 1: 'White', 2: 'Red', 3: 'Pink', 4: 'Grey', 100: 'Other'}
PC_MANUFACTURERS = {0: 'Asus', 1: 'Dell', 2: 'HP', 3: 'Lenovo', 4: 'Apple', 5: 'Samsung', 6: 'Fujitsu', 100: 'Other'}
ROLES = {-1: 'public', 0: 'registered', 1: 'user', 2: 'admin'}
PIORITY = {0: 'light', 1: 'info', 2: 'warning', 3: 'danger'}
SETTINGS_DB = 'settings'
USERS_DB = 'user'
CLIENTS_DB = 'client'
TICKETS_DB = 'ticket'
PRODUCTS_DB = 'product'
BRANDS_DB = 'brand'
LANGUAGE = 'il'

POWER_SUPPLIES_FOLDER = f'{ROOT_PATH}/static/img/public/products/power_supplies'

LOGGER_CONFIG = {
    "version": 1,
    "formatters": {
        "default": {
            "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
            "formatter": "default",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "lab.log",
            "maxBytes": 3000000,
            "backupCount": 5,
            "formatter": "default",
        },
    },
    "root": {"level": "DEBUG", "handlers": ["console", "file"]},
}

TICKET_EDIT_FILEDS = [
    'author_id',
    'created',
    'title',
    'body',
    'pc_kind',
    'pc_manufacturer',
    'pc_model',
    'pc_color',
    'pc_screen_inch',
    'with_power_supply',
    'pc_login_password',
    'cpu_diag',
    'ram_diag',
    'disk_diag',
    'video_card_diag',
    'total_diag',
    'diagnostic_end',
    'recived_by_client',
    'spend_time_minutes',
    'spend_parts',
    'price',
    'status',
    'priority',
    ]