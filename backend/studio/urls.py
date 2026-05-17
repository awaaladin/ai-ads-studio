from django.urls import path

from .legal_views import PrivacyView, TermsView
from .views import (
    AdBriefDetailView,
    AdBriefGenerateView,
    AdBriefListCreateView,
    AdBriefVariantsListView,
    AnalyticsView,
    CampaignDetailView,
    CampaignListCreateView,
    CampaignSimulateMetricsView,
    DashboardView,
    HealthView,
    NotificationListView,
    NotificationMarkReadView,
    ProjectCreativesListView,
    ProjectDetailView,
    ProjectGenerateView,
    ProjectListCreateView,
)

urlpatterns = [
    path("", HealthView.as_view(), name="health"),
    path("legal/terms/", TermsView.as_view(), name="api-legal-terms"),
    path("legal/privacy/", PrivacyView.as_view(), name="api-legal-privacy"),
    path("dashboard/", DashboardView.as_view(), name="api-dashboard"),
    path("analytics/", AnalyticsView.as_view(), name="api-analytics"),
    path("ad-briefs/", AdBriefListCreateView.as_view(), name="api-ad-briefs"),
    path("ad-briefs/<uuid:brief_id>/", AdBriefDetailView.as_view(), name="api-ad-brief-detail"),
    path(
        "ad-briefs/<uuid:brief_id>/generate/",
        AdBriefGenerateView.as_view(),
        name="api-ad-brief-generate",
    ),
    path(
        "ad-briefs/<uuid:brief_id>/variants/",
        AdBriefVariantsListView.as_view(),
        name="api-ad-brief-variants",
    ),
    path("campaigns/", CampaignListCreateView.as_view(), name="api-campaigns"),
    path("campaigns/<uuid:campaign_id>/", CampaignDetailView.as_view(), name="api-campaign-detail"),
    path(
        "campaigns/<uuid:campaign_id>/simulate/",
        CampaignSimulateMetricsView.as_view(),
        name="api-campaign-simulate",
    ),
    path("notifications/", NotificationListView.as_view(), name="api-notifications"),
    path(
        "notifications/<uuid:notification_id>/read/",
        NotificationMarkReadView.as_view(),
        name="api-notification-read",
    ),
    path("projects/", ProjectListCreateView.as_view(), name="api-projects-list"),
    path("projects/<uuid:project_id>/", ProjectDetailView.as_view(), name="api-project-detail"),
    path(
        "projects/<uuid:project_id>/generate/",
        ProjectGenerateView.as_view(),
        name="api-project-generate",
    ),
    path(
        "projects/<uuid:project_id>/creatives/",
        ProjectCreativesListView.as_view(),
        name="api-project-creatives",
    ),
]
