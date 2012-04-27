import json
from django.contrib.auth.decorators import user_passes_test
from django.forms import model_to_dict
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from ..trac.models import Ticket
from . import github
from .models import PullRequest

class GithubWebhook(View):
    """
    Handle the Github webhooks.
    """
    def dispatch(self, request):
        self.request = request
        self.event = request.META['HTTP_X_GITHUB_EVENT']
        self.payload = json.load(request)
        # FIXME: should validate X-Hub-Signature here.
        return getattr(self, 'handle_%s_webhook' % self.event)()

    def handle_pull_request_webhook(self):
        print "Pull request!"
        return HttpResponse(status=204)

    def handle_push_webhook(self):
        print "Push!"
        return HttpResponse(status=204)

    def handle_issue_comment_webhook(self):
        print "Issue comment!"
        return HttpResponse(status=204)
