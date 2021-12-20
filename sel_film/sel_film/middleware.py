from django.http import HttpResponse
from django.shortcuts import render
from loguru import logger


class ErrorLogMiddleware:
    def __init__(self, get_response):
        self._get_response = get_response

    def __call__(self, request):
        response = self._get_response(request)
        return response

    # TO DO: page for exceptions
    def process_exception(self, request, exception):
        logger.error(f'Error middleware: {exception}')
<<<<<<< HEAD
        return HttpResponse('Что-то пошло не так')

=======
        return render(request, 'error_page/index.html')
>>>>>>> 693321860bf81158170e8bcc27abacfeb302c396

