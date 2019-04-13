pykismet3
=========

A Python 3 Akismet client library.

## Supported API

The Following Akismet API Calls are currently supported:
* Comment Check
* Submit Ham
* Submit Spam

## Unsupported API

The following Akismet API Calls are not yet supported:
* Key Verification

## Installation

1. Signup for Akismet and get yourself an API key at http://akismet.com/plans/

2. Install this library:

    pip install pykismet3

3. Make some calls to Akismet (see example below to get started)

## Example

Import and instantiate Pykismet.

    from pykismet3 import Akismet
    import os

    a = Akismet(blog_url="http://your.blog/url",
                user_agent="My Awesome Web App/0.0.1")

    a.api_key="YOUR_AKISMET_API_KEY"

### Comment Check

    a.check({'user_ip': os.environ['REMOTE_ADDR'],
             'user_agent': os.environ['HTTP_USER_AGENT'],
             'referrer': os.environ.get('HTTP_REFERER', 'unknown'),
             'comment_content': 'I LIEK YOUR WEB SITE',
             'comment_author': 'Comment Author',
             'is_test': 1,
    })

### Submit Ham

    a.submit_ham({'user_ip': os.environ['REMOTE_ADDR'],
                  'user_agent': os.environ['HTTP_USER_AGENT'],
                  'referrer': os.environ.get('HTTP_REFERER', 'unknown'),
                  'comment_content': 'I LIEK YOUR WEB SITE',
                  'comment_author': 'Comment Author',
                  'is_test': 1,
    })

### Submit Spam

    a.submit_spam({'user_ip': os.environ['REMOTE_ADDR'],
                   'user_agent': os.environ['HTTP_USER_AGENT'],
                   'referrer': os.environ.get('HTTP_REFERER', 'unknown'),
                   'comment_content': 'I LIEK YOUR WEB SITE',
                   'comment_author': 'Comment Author',
                   'is_test': 1,
    })

## Documentation

The examples above show you pretty much everything you need to know.

For a full list of supported parameters for each API call, see http://akismet.com/development/api/

The code is only ~150 lines long anyway, so just look at '''pykismet.py''' if you aren't sure about something.

## Bugs

Patches to fix bugs and implement missing features welcome! Please make a pull request.




