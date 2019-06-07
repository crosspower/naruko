from rest_framework.views import exception_handler
from django.db.models import ObjectDoesNotExist
from rest_framework import status
from rest_framework.response import Response
from backend.logger import NarukoLogging
from backend.exceptions import NarukoException
from botocore.exceptions import ClientError

EXCEPTIONS = {
    status.HTTP_400_BAD_REQUEST: [
        TypeError,
        ValueError,
        KeyError,
        NarukoException,
        ClientError
    ],
    status.HTTP_404_NOT_FOUND: [
        ObjectDoesNotExist
    ]
}


def isinstance_in(o, class_list):
    is_instance = False
    for clazz in class_list:
        is_instance += isinstance(o, clazz)
    return is_instance


def naruko_exception_handler(exc, context):
    response = exception_handler(exc, context)

    logger = NarukoLogging(context['request']).get_logger(context['view'].__module__)
    logger.exception(exc)

    for code in EXCEPTIONS.keys():
        if isinstance_in(exc, EXCEPTIONS[code]):
            return Response(status=code)

    return response
