"""
Mark people with 404'ing feeds as defunct.
"""

for f in Feed.objects.all():
    try:
        r = urllib2.urlopen(f.feed_url)
    except urllib2.HTTPError, e:
        if e.code == 404 or e.code == 500:
            print "%s on %s; marking defunct" % (e.code, f)
            f.is_defunct = True
            f.save()
        else:
            raise