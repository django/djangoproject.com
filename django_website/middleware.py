class SetRemoteAddr(object):
    """
    Set the remote addr to the actual real IP, not the IP of the load
    balancer. This assumes running behind Nginx with something like::
    
        location / {
            proxy_pass        http://localhost:8000;
            proxy_set_header  X-Real-IP  $remote_addr;
        }
    """
    
    def process_request(self, request):
        try:
            request.META['REMOTE_ADDR'] = request.META['HTTP_X_REAL_IP']
        except KeyError:
            pass    