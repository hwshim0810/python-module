from django.db import models
from django.utils import timezone
# Import Util module
from operator import eq
from sms_module.util import get_secret
from sms_module.crypto import AESCipher

key = get_secret("crypto_key")


class AuthInfo(models.Model):
    phone = models.CharField(max_length=50)
    msg = models.CharField(max_length=20)
    counter = models.IntegerField(default=0)
    date = models.DateField(default=timezone.now)

    @classmethod
    def get_info_by_id(cls, msg_id):
        return AuthInfo.objects.get(id=msg_id)

    @classmethod
    def get_info_by_num(cls, phone):
        return AuthInfo.objects.get(phone=phone)

    def validate_count(self):
        # 인증은 3회까지
        if self.counter > 1:
            self.delete()
            return True
        else:
            return False

    def validate_info(self, msg):
        # DB정보와 입력정보 대조하여 인증여부 결정
        if eq(msg, AESCipher(key).decrypt(str(self.msg))):
            self.delete()
            return {'res': True}
        # 틀렸을 경우 기회차감
        else:
            self.counter = self.counter + 1
            self.publish()
            return {'res': False, 'id': self.id}

    def update_count(self):
        self.counter = self.counter + 1
        self.publish()

    def publish(self):
        self.save()

    def __str__(self):
        return self.phone
