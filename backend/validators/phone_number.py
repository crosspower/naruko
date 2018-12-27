import phonenumbers
from rest_framework import serializers


class PhoneNumber(object):
    def __call__(self, value):
        try:
            phonenumber = phonenumbers.parse(value, 'JP')
        except phonenumbers.phonenumberutil.NumberParseException:
            raise serializers.ValidationError("有効な電話番号を入力してください。")

        if phonenumbers.is_possible_number(phonenumber):
            if phonenumbers.format_number(phonenumber, phonenumbers.PhoneNumberFormat.NATIONAL) == value:
                return value

        raise serializers.ValidationError("有効な電話番号を入力してください。")
