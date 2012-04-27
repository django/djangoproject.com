import json
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

class PullRequestsForTicket(View):
    """
    Expose pull requests for a ticket as a minimal web service.
    """
    @method_decorator(csrf_exempt)
    def dispatch(self, request, ticket_id):
        self.ticket = get_object_or_404(Ticket, id=ticket_id)
        return super(PullRequestsForTicket, self).dispatch(request)

    def get(self, request):
        """
        GET pulls/{ticket_id} --> pull requests linked to ticket {ticket_id}

        Returns JSON in the form of::

            {"pulls": [
                {"number": <pull-request-number>, "ticket_id": <ticket-id>, "title": "ticket title"},
                ...
            ]}
        """
        pull_requests = PullRequest.objects.filter(ticket_id=self.ticket.id)
        js = json.dumps({'pulls': [model_to_dict(p) for p in pull_requests]})
        return HttpResponse(js, content_type='application/json')

    def post(self, request):
        """
        POST pulls/{ticket_id} --> link a pull request to ticket {ticket_id}

        Expects form-encoded data (yeah yeah, it's inconsistant. Deal with it.)
        containing a "number" field.
        """
        if not request.user.is_staff:
            return HttpResponse(status=401)
        try:
            number = int(self.request.POST['number'])
        except KeyError:
            return HttpResponse("Missing number field in POST", status=400)
        except (ValueError, TypeError):
            return HttpResponse("Invalid number - must be an int.", status=400)

        # Make sure the PR exists over on the GitHub side.
        response = github.session().get('repos/django/django/pulls/%s' % number)
        if response.status_code != 200:
            return HttpResponse("Bad PR number: GItHub returned HTTP %s." % response.status_code, status=400)

        pr, created = PullRequest.objects.get_or_create(number=number)
        pr.ticket_id = self.ticket.id
        pr.title = response.json['title']
        pr.save()

        return HttpResponse(status=204)
