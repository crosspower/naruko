from backend.serializers.user_model_serializer import UserModelDetailSerializer


def jwt_response_payload_handler(token, user=None, request=None):
    return {
        'token': token,
        'user': UserModelDetailSerializer(user, context={'request':request}).data
    }