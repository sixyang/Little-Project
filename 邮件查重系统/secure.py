SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:XXX@127.0.0.1:3306/check_homework'
SQLALCHEMY_TRACK_MODIFICATIONS = True

CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/1'