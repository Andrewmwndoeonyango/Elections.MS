# =====================================================
# DISTINCTION-LEVEL ELECTION MANAGEMENT SYSTEM URLS
# =====================================================

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from rest_framework.routers import DefaultRouter

# Import API views
from .api_views import (
    ResultViewSet, get_aggregated_results, get_results_dashboard,
    get_winners, get_all_winners, export_results
)

# Import regular views
from .views import (
    dashboard_view, login_view, logout_view, results_view,
    candidates_view, counties_view, constituencies_view
)

# Create REST API router
router = DefaultRouter()
router.register(r'api/results', ResultViewSet, basename='result')

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Authentication
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    
    # Main Dashboard
    path('', dashboard_view, name='dashboard'),
    path('dashboard/', dashboard_view, name='dashboard'),
    
    # Results Pages
    path('results/', results_view, name='results'),
    path('results/dashboard/', TemplateView.as_view(template_name='results_dashboard.html'), name='results_dashboard'),
    
    # Data Management Pages
    path('candidates/', candidates_view, name='candidates'),
    path('counties/', counties_view, name='counties'),
    path('constituencies/', constituencies_view, name='constituencies'),
    
    # REST API URLs
    path('api/', include(router.urls)),
    
    # Results Aggregation API
    path('api/results/ward/<int:ward_id>/mca/', get_aggregated_results, name='ward_mca_results'),
    path('api/results/constituency/<int:constituency_id>/mp/', get_aggregated_results, name='constituency_mp_results'),
    path('api/results/county/<int:county_id>/governor/', get_aggregated_results, name='county_governor_results'),
    path('api/results/county/<int:county_id>/senator/', get_aggregated_results, name='county_senator_results'),
    path('api/results/county/<int:county_id>/women_rep/', get_aggregated_results, name='county_women_rep_results'),
    
    # Dashboard API
    path('api/results/dashboard/', get_results_dashboard, name='results_dashboard_api'),
    
    # Winners API
    path('api/winners/', get_winners, name='get_winners'),
    path('api/winners/all/', get_all_winners, name='get_all_winners'),
    
    # Export API
    path('api/export/', export_results, name='export_results'),
    
    # Static files
    path('static/', TemplateView.as_view(template_name='static/index.html'), name='static'),
]

# Serve static and media files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Custom error handlers
handler404 = 'elections.views.custom_404'
handler500 = 'elections.views.custom_500'
