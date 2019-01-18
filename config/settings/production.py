from .base import *
import os
import boto3

IS_LOCAL = False

# 設定値リスト
keys = [
    "DEBUG",
    "SES_ADDRESS",
    "SES_REGION",
    "LOG_GROUP",
    "SNS_TOPIC_NAME",
    "NOTIFY_TEXT_MESSAGE",
    "NOTIFY_TEXT_SUBJECT",
    "EVENT_SNS_TOPIC_ARN",
    "CONNECT_REGION",
    "CONNECT_NOTIFY_FLOW_ID",
    "CONNECT_NOTIFY_INSTANCE_ID",
    "CONNECT_PHONE_NUMBER"
]

# 辞書構造の設置値リスト
dict_keys = [
    "DB_ENGINE",
    "DB_NAME",
    "DB_HOST",
    "DB_USER",
    "DB_PASSWORD"
]

# 検証環境か
is_dev = os.environ.get("environment", "dev") == "dev"

# 検証環境であれば検証環境の値を使用する
if is_dev:
    keys = ["DEV_" + key for key in keys]
    dict_keys = ["DEV_" + dict_key for dict_key in dict_keys]


# AWS System Manager パラメータストアから本番環境用設定値を取得する
def get_params():
    keys_list = keys+dict_keys
    names_list = [keys_list[idx:idx + 10] for idx in range(0, len(keys_list), 10)]
    client = boto3.client("ssm", region_name=NARUKO_REGION)

    res = dict()
    for names in names_list:
        response = client.get_parameters(
            Names=names,
            WithDecryption=True
        )
        res.update({param["Name"]: param["Value"] for param in response["Parameters"]})

    return res


# パラメータストアから取得した値をグローバル変数に代入しSettingsから参照できるようにする
parameters = get_params()
for key in keys:
    actual_key = key.replace("DEV_", "") if is_dev else key
    exec("{0}='{1}'".format(actual_key, parameters[key]))


# 検証環境であれば検証環境の値を使用する
def convert_key(key, is_develop):
    return "DEV_" + key if is_develop else key


DATABASES = {
    'default': {
        'ENGINE': parameters[convert_key("DB_ENGINE", is_dev)],
        'NAME': parameters[convert_key("DB_NAME", is_dev)],
        'HOST': parameters[convert_key("DB_HOST", is_dev)],
        'USER': parameters[convert_key("DB_USER", is_dev)],
        'PASSWORD': parameters[convert_key("DB_PASSWORD", is_dev)]
    }
}

# =========================
# log 設定
# =========================
LOGGING["handlers"]['watchtower'] = {
    'level': 'DEBUG',
    'class': 'watchtower.CloudWatchLogHandler',
    'boto3_session': boto3.Session(region_name=NARUKO_REGION),
    'log_group': parameters[convert_key("LOG_GROUP", is_dev)],
    "stream_name": "NARUKO_APP_LOG",
    'formatter': 'default',
}
LOGGING['loggers'] = {
    'backend': {
        'handlers': ['console', 'watchtower'],
        'level': 'DEBUG' if is_dev else 'INFO',
        'propagate': True,
    }
}
