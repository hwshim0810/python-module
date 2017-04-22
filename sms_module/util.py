import json
import random
from django.core.exceptions import ImproperlyConfigured

with open("key.json") as f:
    key = json.loads(f.read())


# Keep secret keys in secrets.json
def get_secret(setting, key=key):
    try:
        return key[setting]
    except KeyError:
        error_msg = "Set the {0} environment variable".format(setting)
        raise ImproperlyConfigured(error_msg)


def gen_num(n):
    return str(int(random.random() * pow(10, n)))
