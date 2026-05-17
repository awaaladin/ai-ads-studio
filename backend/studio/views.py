import os
import random
import uuid
from decimal import Decimal

from django.conf import settings
from django.db.models import Q
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics, permissions, status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from django.db.models import Sum

from .models import AdBrief, AdCreative, AdVariant, Asset, Campaign, Notification, Project
from .serializers import (
    AdBriefCreateSerializer,
    AdBriefSerializer,
    AdCreativeSerializer,
    AdVariantSerializer,
    CampaignSerializer,
    NotificationSerializer,
    ProjectCreateSerializer,
    ProjectSerializer,
)
from .services.assets import detect_file_type, extract_text_from_upload
from django.db import connection

from .services.audit import audit
from .services.llm import LLMServiceError, generate_ad_copy, generate_ad_variants
from .services.moderation import apply_disclaimer, moderate_text, moderate_variant
from .services.pdf import generate_pdf
from .services.storage import upload_file_to_storage
from .services.usage import check_generation_quota, record_generation


class HealthView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        payload = {
            "status": "ok",
            "message": "AI Ads Studio API is running",
            "database": "unknown",
            "ai": "configured" if settings.GROQ_API_KEY else "fallback_templates",
        }
        try:
            connection.ensure_connection()
            payload["database"] = "connected"
        except Exception as exc:
            payload["status"] = "degraded"
            payload["database"] = str(exc)
        code = status.HTTP_200_OK if payload["status"] == "ok" else status.HTTP_503_SERVICE_UNAVAILABLE
        return Response(payload, status=code)


class GenerateThrottle(ScopedRateThrottle):
    scope = "generate"


@extend_schema_view(
    get=extend_schema(summary="List projects", responses=ProjectSerializer(many=True)),
    post=extend_schema(summary="Create project (onboarding)", request=ProjectCreateSerializer),
)
class ProjectListCreateView(generics.ListCreateAPIView):
    serializer_class = ProjectSerializer

    def get_queryset(self):
        qs = Project.objects.all()
        if self.request.user.is_authenticated:
            return qs.filter(Q(owner=self.request.user) | Q(owner__isnull=True))
        return qs

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ProjectCreateSerializer
        return ProjectSerializer

    def perform_create(self, serializer):
        owner = self.request.user if self.request.user.is_authenticated else None
        serializer.save(owner=owner)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        output = ProjectSerializer(serializer.instance, context={"request": request})
        headers = self.get_success_headers(output.data)
        return Response(output.data, status=status.HTTP_201_CREATED, headers=headers)


class ProjectDetailView(generics.RetrieveAPIView):
    serializer_class = ProjectSerializer
    lookup_field = "id"
    lookup_url_kwarg = "project_id"

    def get_queryset(self):
        qs = Project.objects.all()
        if self.request.user.is_authenticated:
            return qs.filter(Q(owner=self.request.user) | Q(owner__isnull=True))
        return qs


class ProjectGenerateView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [permissions.AllowAny]
    throttle_classes = [GenerateThrottle]

    @extend_schema(
        summary="Generate ad creatives for a project",
        request={"multipart/form-data": {"type": "object", "properties": {"file": {"type": "string", "format": "binary"}}}},
        responses=AdCreativeSerializer,
    )
    def post(self, request, project_id):
        if request.user.is_authenticated:
            check_generation_quota(request.user)
        project = get_object_or_404(Project, id=project_id)
        if (
            request.user.is_authenticated
            and project.owner_id
            and project.owner_id != request.user.id
        ):
            return Response({"detail": "Not allowed."}, status=status.HTTP_403_FORBIDDEN)

        extracted_text = ""
        uploaded = request.FILES.get("file")
        if uploaded:
            extracted_text = extract_text_from_upload(uploaded)
            asset = Asset(
                project=project,
                file_type=detect_file_type(uploaded.name),
                extracted_text=extracted_text,
            )
            asset.file.save(uploaded.name, uploaded, save=False)
            asset.file_url = request.build_absolute_uri(asset.file.url)
            asset.save()

        context = {
            "business_name": project.business_name,
            "industry": project.industry,
            "audience": project.audience,
            "tone": project.tone,
            "goal": project.goal,
        }

        try:
            gen_result = generate_ad_copy(context, extracted_text)
        except LLMServiceError as exc:
            return Response(
                {"detail": f"Creative generation unavailable: {exc}"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        ad_copy = gen_result.get("ad_copy", "")
        ok, reason = moderate_text(ad_copy)
        if not ok:
            return Response({"detail": reason}, status=status.HTTP_400_BAD_REQUEST)
        for post in gen_result.get("social_posts", []) or []:
            ok, reason = moderate_text(str(post))
            if not ok:
                return Response({"detail": reason}, status=status.HTTP_400_BAD_REQUEST)

        pdf_path = generate_pdf(
            project.business_name,
            project.colors,
            gen_result.get("brochure_content", ""),
        )
        pdf_url = ""
        try:
            pdf_url = upload_file_to_storage(pdf_path, f"{project_id}_{uuid.uuid4()}.pdf")
        finally:
            if os.path.exists(pdf_path):
                os.remove(pdf_path)

        creative = AdCreative.objects.create(
            project=project,
            copy=ad_copy,
            social_posts=gen_result.get("social_posts", []),
            pdf_brochure_url=pdf_url,
        )

        if request.user.is_authenticated:
            record_generation(request.user)
            audit(request.user, "project.generate", "project", project_id)

        serializer = AdCreativeSerializer(creative, context={"request": request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ProjectCreativesListView(generics.ListAPIView):
    serializer_class = AdCreativeSerializer

    def get_queryset(self):
        project = get_object_or_404(Project, id=self.kwargs["project_id"])
        if self.request.user.is_authenticated and project.owner_id and project.owner_id != self.request.user.id:
            return AdCreative.objects.none()
        return AdCreative.objects.filter(project=project)


@extend_schema_view(
    get=extend_schema(summary="List ad briefs"),
    post=extend_schema(summary="Create ad brief", request=AdBriefCreateSerializer),
)
class AdBriefListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return AdBrief.objects.filter(
            Q(owner=self.request.user) | Q(owner__isnull=True)
        )

    def get_serializer_class(self):
        if self.request.method == "POST":
            return AdBriefCreateSerializer
        return AdBriefSerializer

    def perform_create(self, serializer):
        owner = self.request.user if self.request.user.is_authenticated else None
        serializer.save(owner=owner)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        output = AdBriefSerializer(serializer.instance, context={"request": request})
        return Response(output.data, status=status.HTTP_201_CREATED)


class AdBriefDetailView(generics.RetrieveAPIView):
    serializer_class = AdBriefSerializer
    lookup_field = "id"
    lookup_url_kwarg = "brief_id"
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return AdBrief.objects.filter(
            Q(owner=self.request.user) | Q(owner__isnull=True)
        )


class AdBriefGenerateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [GenerateThrottle]

    @extend_schema(summary="Generate ad variants from brief", responses=AdVariantSerializer(many=True))
    def post(self, request, brief_id):
        check_generation_quota(request.user)
        brief = get_object_or_404(AdBrief, id=brief_id)
        context = {
            "product_service": brief.product_service,
            "audience": brief.audience,
            "tone": brief.tone,
            "platform": brief.platform,
            "key_message": brief.key_message,
        }

        try:
            variants_data = generate_ad_variants(context)
        except LLMServiceError as exc:
            return Response(
                {"detail": f"Variant generation unavailable: {exc}"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        variants_data = apply_disclaimer(variants_data)
        created = []
        for item in variants_data:
            ok, reason = moderate_variant(item)
            if not ok:
                return Response({"detail": reason}, status=status.HTTP_400_BAD_REQUEST)
            variant = AdVariant.objects.create(
                brief=brief,
                headline=item.get("headline", ""),
                body=item.get("body", ""),
                cta=item.get("cta", ""),
                platform=brief.platform,
            )
            created.append(variant)

        record_generation(request.user, count=len(created))
        audit(request.user, "ad.generate", "ad_brief", brief_id, {"variants": len(created)})
        serializer = AdVariantSerializer(created, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AdBriefVariantsListView(generics.ListAPIView):
    serializer_class = AdVariantSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        brief = get_object_or_404(AdBrief, id=self.kwargs["brief_id"])
        return AdVariant.objects.filter(brief=brief)


class DashboardView(APIView):
    """Dashboard page: summary stats + recent items."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        campaigns_qs = Campaign.objects.filter(owner=request.user)
        briefs_qs = AdBrief.objects.filter(Q(owner=request.user) | Q(owner__isnull=True))
        notifications_qs = Notification.objects.filter(user=request.user)

        totals = campaigns_qs.aggregate(
            impressions=Sum("impressions"),
            clicks=Sum("clicks"),
            spend=Sum("spend"),
        )
        impressions = totals["impressions"] or 0
        clicks = totals["clicks"] or 0
        ctr = round((clicks / impressions) * 100, 2) if impressions else 0.0

        return Response(
            {
                "total_campaigns": campaigns_qs.count(),
                "active_campaigns": campaigns_qs.filter(status=Campaign.STATUS_ACTIVE).count(),
                "total_briefs": briefs_qs.count(),
                "total_variants": AdVariant.objects.filter(brief__in=briefs_qs).count(),
                "analytics": {
                    "impressions": impressions,
                    "clicks": clicks,
                    "ctr": ctr,
                    "spend": str(totals["spend"] or 0),
                },
                "recent_campaigns": CampaignSerializer(
                    campaigns_qs[:5], many=True, context={"request": request}
                ).data,
                "recent_briefs": AdBriefSerializer(
                    briefs_qs[:5], many=True, context={"request": request}
                ).data,
                "unread_notifications": NotificationSerializer(
                    notifications_qs.filter(is_read=False)[:5],
                    many=True,
                    context={"request": request},
                ).data,
            }
        )


class AnalyticsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        qs = Campaign.objects.filter(owner=request.user)
        totals = qs.aggregate(
            impressions=Sum("impressions"),
            clicks=Sum("clicks"),
            spend=Sum("spend"),
        )
        impressions = totals["impressions"] or 0
        clicks = totals["clicks"] or 0
        return Response(
            {
                "impressions": impressions,
                "clicks": clicks,
                "ctr": round((clicks / impressions) * 100, 2) if impressions else 0.0,
                "spend": str(totals["spend"] or 0),
                "campaigns": CampaignSerializer(qs, many=True, context={"request": request}).data,
            }
        )


class CampaignListCreateView(generics.ListCreateAPIView):
    serializer_class = CampaignSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Campaign.objects.filter(owner=self.request.user)
        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(name__icontains=search)
        return qs

    def perform_create(self, serializer):
        campaign = serializer.save(owner=self.request.user)
        Notification.objects.create(
            user=self.request.user,
            title="Campaign created",
            message=f'Campaign "{campaign.name}" was created.',
        )


class CampaignDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CampaignSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"
    lookup_url_kwarg = "campaign_id"

    def get_queryset(self):
        return Campaign.objects.filter(owner=self.request.user)


class CampaignSimulateMetricsView(APIView):
    """Demo: increase impressions/clicks/spend when a campaign runs (for analytics charts)."""

    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(summary="Simulate live ad metrics (demo)")
    def post(self, request, campaign_id):
        campaign = get_object_or_404(
            Campaign, id=campaign_id, owner=request.user
        )
        if campaign.status == Campaign.STATUS_DRAFT:
            campaign.status = Campaign.STATUS_ACTIVE

        imp_delta = request.data.get("impressions_delta")
        click_delta = request.data.get("clicks_delta")
        spend_delta = request.data.get("spend_delta")

        campaign.impressions += int(imp_delta if imp_delta is not None else random.randint(200, 900))
        campaign.clicks += int(click_delta if click_delta is not None else random.randint(8, 45))
        campaign.spend += Decimal(str(spend_delta if spend_delta is not None else "5.00"))
        campaign.save()

        Notification.objects.create(
            user=request.user,
            title="Campaign running",
            message=f'"{campaign.name}" — {campaign.impressions:,} impressions, {campaign.clicks:,} clicks.',
        )
        return Response(
            CampaignSerializer(campaign, context={"request": request}).data
        )


class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Notification.objects.filter(user=self.request.user)
        unread = self.request.query_params.get("unread")
        if unread in ("1", "true", "yes"):
            qs = qs.filter(is_read=False)
        return qs


class NotificationMarkReadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, notification_id):
        notification = get_object_or_404(
            Notification, id=notification_id, user=request.user
        )
        notification.is_read = True
        notification.save(update_fields=["is_read"])
        return Response(NotificationSerializer(notification).data)
