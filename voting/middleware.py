
import time
from django.utils.deprecation import MiddlewareMixin

class PerformanceMonitoringMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.start_time = time.time()
        
    def process_response(self, request, response):
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            response['X-Page-Generation-Time'] = str(round(duration, 3))
            
            # Log slow requests
            if duration > 1.0:
                import logging
                logger = logging.getLogger('performance')
                logger.warning(f'Slow request: {request.path} took {duration:.3f}s')
        
        return response
