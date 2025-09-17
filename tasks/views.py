from django.http import HttpRequest, HttpResponse


def test_view(request: HttpRequest) -> HttpResponse:
    return HttpResponse("Hello, world!")
