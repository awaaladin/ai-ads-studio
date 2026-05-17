from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

TERMS = {
    "title": "Terms of Service",
    "version": "2026-05-15",
    "summary": (
        "AI Ads Studio is an educational MVP. Generated copy is AI-assisted and must be "
        "reviewed before use. You are responsible for compliance with ad platforms and laws."
    ),
}

PRIVACY = {
    "title": "Privacy Policy",
    "version": "2026-05-15",
    "summary": (
        "We store account email, usage metrics, and content you submit for generation. "
        "Do not submit sensitive personal data. Contact your instructor for data requests."
    ),
}


class TermsView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response(TERMS)


class PrivacyView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response(PRIVACY)
