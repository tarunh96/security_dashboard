"""findings_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.views.generic import RedirectView

from findings_platform import views
from findings_platform import service_layer_controller_logic as controller_logic
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('findings_platform/pages/<str:input_to_organisation>/home/', views.HomeView.as_view(), name='home'),

    path('findings_platform/pages/<str:input_to_organisation>/assets/<str:input_assettype>/',
        views.AssetListView.as_view(), name='asset-list'),
    path('findings_platform/pages/<str:input_to_organisation>/assets/<str:input_assettype>/create/',
        views.AssetCreateView.as_view(), name='asset-create'),
    path('findings_platform/pages/<str:input_to_organisation>/assets/<str:input_assettype>/<int:input_assetid>/update/',
        views.AssetUpdateView.as_view(), name='asset-update'),
    path('findings_platform/pages/<str:input_to_organisation>/assets/<str:input_assettype>/<int:input_assetid>/delete/',
        views.AssetDeleteView.as_view(), name='asset-delete'),


    path('findings_platform/pages/<str:input_to_organisation>/findings/<str:input_findingtype>/',
         views.FindingListView.as_view(), name='finding-list'),
    path('findings_platform/pages/<str:input_to_organisation>/finding/<str:input_findingtype>/<int:input_findingid>/update/',
        views.FindingUpdateView.as_view(), name='finding-update'),
    path('findings_platform/pages/<str:input_to_organisation>/findings/<str:input_findingtype>/create/',
        views.FindingCreateView.as_view(), name='finding-create'),
    path('findings_platform/pages/<str:input_to_organisation>/finding/<str:input_findingtype>/<int:input_findingid>/delete/',
        views.FindingDeleteView.as_view(), name='finding-delete'),


    path('findings_platform/pages/<str:input_to_organisation>/csv_upload/<str:input_model>/upload/',
         views.CSVUpload.as_view(), name='csv-upload'),

    path('findings_platform/pages/<str:input_to_organisation>/findings/<str:input_assettype>/<int:input_assetid>/',
         views.AssetFindingListView.as_view(), name='finding-asset-list'),


    path('findings_platform/api/findings/<str:input_to_organisation>/', views.AllFindingsAPI.as_view(), name='findings-api'),
    path('findings_platform/api/findingsHistory/<str:input_to_organisation>/', views.AllFindingsHistoryAPI.as_view(), name='findings-history-api'),
    path('findings_platform/api/csv/settings/<str:input_model>/<str:input_action>/', views.CSVSettingsUpdateAPI.as_view(), name='csv-settings-api'),
    path('findings_platform/api/csv/upload/<str:input_model>/', views.CSVUploadAPI.as_view(), name='csv-upload-api')
    # # path('findings_platform/login', views.get_login),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
