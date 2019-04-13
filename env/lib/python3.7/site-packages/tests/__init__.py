from io import BytesIO as BaseBytesIO

from requests import Response


class BytesIO(BaseBytesIO):
    def read(self, *args, **kwargs):
        kwargs.pop('decode_content', None)
        return super(BytesIO, self).read(*args, **kwargs)


def response(status_code=200, content='', headers={}):
    response = Response()
    response.status_code = status_code
    response.raw = BytesIO(content.encode('utf-8'))
    response.headers = headers
    return response
