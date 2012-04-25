import json
from django.views.generic import View
from django.http import HttpResponse

class GithubWebhook(View):
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
