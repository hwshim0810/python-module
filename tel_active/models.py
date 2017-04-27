from django.db import models
from django.utils import timezone
# Import regex module
import re
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

    @classmethod
    def validate_phone(cls, phone):
        return not bool(re.search(r"^[0-9]*$", phone)) or len(phone) <= 10

    @classmethod
    def insert_info(cls, res, r_num, phone):
        if int(res["success_count"]) > 0:
            # 인증번호 암호화 후 DB저장
            r_num = AESCipher(key).encrypt(r_num)
            AuthInfo(phone=phone, msg=r_num).publish()
            return True
        else:
            return False

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
