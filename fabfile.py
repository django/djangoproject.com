config.fab_hosts = ['djangoproject.com']

def deploy():
    sudo("cd /home/djangoproject.com && svn up")
    reload()
    
def reload():
    sudo("invoke-rc.d apache2 reload")
    
def flush_cache():
    sudo("invoke-rc.d memcached restart")
    
