from django.utils.httpwrappers import HttpResponse

def aggregator(request):
    return HttpResponse("Hello, world. You're at the poll index.")
