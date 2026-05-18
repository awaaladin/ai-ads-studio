from rest_framework import serializers

from .models import AdBrief, AdCreative, AdVariant, Asset, Campaign, GenerationRecord, Notification, Project

PLATFORM_ALIASES = {
    "friendly": "meta",
    "meta": "meta",
    "tiktok": "tiktok",
    "linkedin": "linkedin",
    "youtube": "youtube",
}


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = (
            "id",
            "business_name",
            "industry",
            "audience",
            "tone",
            "colors",
            "goal",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class ProjectCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = (
            "business_name",
            "industry",
            "audience",
            "tone",
            "colors",
            "goal",
        )


class AssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asset
        fields = (
            "id",
            "project_id",
            "file_type",
            "file_url",
            "extracted_text",
            "created_at",
        )
        read_only_fields = fields


class AdCreativeSerializer(serializers.ModelSerializer):
    pdf_brochure_url = serializers.SerializerMethodField()

    class Meta:
        model = AdCreative
        fields = (
            "id",
            "project_id",
            "copy",
            "social_posts",
            "pdf_brochure_url",
            "created_at",
        )
        read_only_fields = fields

    def get_pdf_brochure_url(self, obj):
        if obj.pdf_brochure_url:
            return obj.pdf_brochure_url
        if obj.pdf_file:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.pdf_file.url)
            return obj.pdf_file.url
        return ""


class AdBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdBrief
        fields = (
            "id",
            "product_service",
            "audience",
            "tone",
            "platform",
            "key_message",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class AdBriefCreateSerializer(serializers.ModelSerializer):
    """Accepts frontend2 form field aliases."""

    prod_service = serializers.CharField(required=False, write_only=True)
    key_message = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = AdBrief
        fields = (
            "product_service",
            "prod_service",
            "audience",
            "tone",
            "platform",
            "key_message",
        )

    def validate(self, attrs):
        if not attrs.get("product_service") and attrs.get("prod_service"):
            attrs["product_service"] = attrs.pop("prod_service")
        elif "prod_service" in attrs:
            attrs.pop("prod_service", None)
        if not attrs.get("product_service"):
            raise serializers.ValidationError(
                {"product_service": "Product/service is required."}
            )
        raw_platform = (attrs.get("platform") or "meta").lower()
        attrs["platform"] = PLATFORM_ALIASES.get(raw_platform, raw_platform)
        return attrs


class AdVariantSerializer(serializers.ModelSerializer):
    primary_text = serializers.CharField(source="body", read_only=True)
    call_to_action = serializers.CharField(source="cta", read_only=True)

    class Meta:
        model = AdVariant
        fields = (
            "id",
            "brief_id",
            "headline",
            "body",
            "primary_text",
            "cta",
            "call_to_action",
            "platform",
            "created_at",
        )
        read_only_fields = fields


class GenerationRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = GenerationRecord
        fields = (
            "id",
            "source_type",
            "source_id",
            "input_data",
            "output_data",
            "variant_count",
            "status",
            "created_at",
        )
        read_only_fields = fields


class CampaignSerializer(serializers.ModelSerializer):
    ctr = serializers.FloatField(read_only=True)

    class Meta:
        model = Campaign
        fields = (
            "id",
            "name",
            "platform",
            "status",
            "brief_id",
            "impressions",
            "clicks",
            "spend",
            "ctr",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "ctr", "created_at", "updated_at")


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ("id", "title", "message", "is_read", "created_at")
        read_only_fields = ("id", "created_at")
