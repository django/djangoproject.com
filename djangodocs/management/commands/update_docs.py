"""
Update and build the documentation into files for display with the djangodocs
app.
"""

import os
import sys
import pysvn
import sphinx

SVN_DOCS_TRUNK = 'http://code.djangoproject.com/svn/django/trunk/docs/'
SVN_DOCS_RELEASES = 'http://code.djangoproject.com/svn/django/branches/releases/'

svn = pysvn.Client()

def get_doc_versions():
    """
    Get a list of (lang, version, svnurl) tuples of docs to build.
    """
    yield ('en', 'dev', SVN_DOCS_TRUNK)
    for release in svn.ls(SVN_DOCS_RELEASES):
        version = release.name.split('/')[-1].replace('.X', '')
        yield ('en', version, "%s/docs/" % release.name)
    
def update_docs(basedir):
    """
    Update all versions of the docs into the given base directory.
    """
    for (lang, version, svnurl) in get_doc_versions():
        
        # Make an SVN checkout (or update) in the destination directory,
        # creating it if it doesn't exist
        destdir = os.path.join(basedir, lang, version)
        if not os.path.exists(destdir):
            os.makedirs(destdir)
        svn.checkout(svnurl, destdir)
                
        # Run Sphinx by faking a commandline. Better than shelling out, I s'pose.
        sphinx.main([
            'sphinx-build',                          # Fake argv[0]
            '-b', 'json',                            # Use the JSON builder
            '-q',                                    # Be vewy qwiet
            destdir,                                 # Source file directory
            os.path.join(destdir, '_build', 'json'), # Destination directory
        ])

if __name__ == '__main__':
    update_docs(sys.argv[1])