from .base import *
import environ

root = environ.Path(__file__) - 3
env_file = str(root.path('.env'))
env = environ.Env()
env.read_env(env_file)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG')
SES_ADDRESS = env('SES_ADDRESS')
SES_REGION = env('SES_REGION')
SNS_TOPIC_NAME = env('SNS_TOPIC_NAME')
NOTIFY_TEXT_MESSAGE = env('NOTIFY_TEXT_MESSAGE')
NOTIFY_TEXT_SUBJECT = env('NOTIFY_TEXT_SUBJECT')
EVENT_SNS_TOPIC_ARN = env('EVENT_SNS_TOPIC_ARN')
CORS_ORIGIN_ALLOW_ALL = True

IS_LOCAL = True
# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': env('DB_ENGINE'),
        'NAME': env('DB_NAME'),
        'HOST': env('DB_HOST'),
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD')
    }
}

INTERNAL_IPS = ['127.0.0.1', 'localhost']


def custom_show_toolbar(request):
    return True


INSTALLED_APPS += (
    'corsheaders',
)

MIDDLEWARE += [
    'corsheaders.middleware.CorsMiddleware'
]

# =========================
# log 設定
# =========================
LOGGING["handlers"]['file'] = {
    'level': 'DEBUG',
    'class': 'logging.FileHandler',
    'filename': os.path.join(BASE_DIR, "log", 'naruko-backend.log'),
    'formatter': 'default',
}
LOGGING['loggers'] = {
    'backend': {
        'handlers': ['file', 'console'],
        'level': 'DEBUG',
        'propagate': True,
    }
}
