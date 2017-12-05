class CORSMiddleware(object):
    """
    Set the CORS 'Access-Control-Allow-Origin' header to allow the debug
    toolbar to work on the docs domain.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response['Access-Control-Allow-Origin'] = '*'
        return response
