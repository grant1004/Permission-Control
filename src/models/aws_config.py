import base64

class AWSConfig:
    def __init__(self):
        # 這些值是用 base64 編碼的認證資訊
        self._access_key = base64.b64decode('QUtJQVpTWUxVMjc1NFdDUVBENVM=').decode()
        self._secret_key = base64.b64decode('K1NRcWRibjVkTHZGb3Ivc1FlbHF0VzMzcmw1K08ybUM4T3dIUjl0Vw==').decode()
        self._region = 'ap-northeast-1'
        self._bucket = 'hy-si-upload'

    @property
    def credentials(self):
        return {
            'aws_access_key_id': self._access_key,
            'aws_secret_access_key': self._secret_key,
            'region_name': self._region
        }

    @property
    def bucket(self):
        return self._bucket