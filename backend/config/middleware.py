from django.http import HttpResponse

class IgnoreWellKnownRequestsMiddleware:
    """
    Middleware pour ignorer les requêtes vers les fichiers .well-known
    qui génèrent des erreurs 404 inutiles dans les logs.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Ignorer les requêtes .well-known et similaires
        if request.path.startswith('/.well-known/'):
            return HttpResponse(status=204)  # No Content
        
        response = self.get_response(request)
        return response
