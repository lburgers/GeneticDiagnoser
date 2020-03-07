import os
import logging
from django.http import HttpResponse
from django.views.generic import View
from django.conf import settings

class FrontendAppView(View):
    """
    Serves frontend app (neeed to run 'yarn build')
    """
    index_file_path = os.path.join(settings.REACT_APP_DIR, 'build', 'index.html')

    def get(self, request):
        try:
            with open(self.index_file_path) as f:
                return HttpResponse(f.read())
        except FileNotFoundError:
            logging.exception('Production build of app not found')
            return HttpResponse(
                """
                This url only works with production build of app
                """,
                status=501,
            )