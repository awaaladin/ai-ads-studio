from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from accounts.models import UserProfile
from studio.services.moderation import moderate_text

User = get_user_model()


class HealthTests(TestCase):
    def test_health_ok(self):
        client = APIClient()
        response = client.get("/api/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")
        self.assertEqual(response.json()["database"], "connected")


class LegalTests(TestCase):
    def test_terms_and_privacy(self):
        client = APIClient()
        terms = client.get("/api/legal/terms/")
        privacy = client.get("/api/legal/privacy/")
        self.assertEqual(terms.status_code, 200)
        self.assertEqual(privacy.status_code, 200)
        self.assertIn("title", terms.json())


class ModerationTests(TestCase):
    def test_blocks_policy_violation(self):
        ok, reason = moderate_text("This is a guaranteed cure for everything")
        self.assertFalse(ok)
        self.assertIn("guaranteed cure", reason or "")

    def test_allows_clean_copy(self):
        ok, _ = moderate_text("Launch your summer sale today.")
        self.assertTrue(ok)


@override_settings(REQUIRE_EMAIL_VERIFICATION=False)
class AuthTests(TestCase):
    def test_register_and_me(self):
        client = APIClient()
        payload = {
            "email": "student@example.com",
            "password": "SecurePass123!",
            "password_confirm": "SecurePass123!",
            "first_name": "Test",
            "last_name": "User",
        }
        reg = client.post("/api/auth/register/", payload, format="json")
        self.assertEqual(reg.status_code, 201)

        login = client.post(
            "/api/auth/login/",
            {"email": payload["email"], "password": payload["password"]},
            format="json",
        )
        self.assertEqual(login.status_code, 200)
        token = login.json()["access"]
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        me = client.get("/api/auth/me/")
        self.assertEqual(me.status_code, 200)
        self.assertEqual(me.json()["email"], payload["email"])
        self.assertIn("generations_limit", me.json())

    def test_register_weak_password_returns_400_not_500(self):
        client = APIClient()
        # "stringst" passes validators; "password" fails CommonPasswordValidator → must be 400 not 500
        reg = client.post(
            "/api/auth/register/",
            {
                "email": "weak@example.com",
                "password": "password",
                "password_confirm": "password",
            },
            format="json",
        )
        self.assertEqual(reg.status_code, 400)
        self.assertIn("password", reg.json())


class QuotaTests(TestCase):
    def test_quota_blocks_generation(self):
        user = User.objects.create_user(
            email="quota@example.com",
            username="quota@example.com",
            password="SecurePass123!",
        )
        profile = UserProfile.objects.get(user=user)
        profile.generations_this_month = profile.generation_limit
        profile.save()

        client = APIClient()
        login = client.post(
            "/api/auth/login/",
            {"email": user.email, "password": "SecurePass123!"},
            format="json",
        )
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.json()['access']}")

        brief = client.post(
            "/api/ad-briefs/",
            {
                "product_service": "Coffee",
                "audience": "Students",
                "tone": "friendly",
                "platform": "meta",
                "key_message": "Fresh brew",
            },
            format="json",
        )
        self.assertEqual(brief.status_code, 201)
        brief_id = brief.json()["id"]

        gen = client.post(f"/api/ad-briefs/{brief_id}/generate/")
        self.assertEqual(gen.status_code, 429)
        body = gen.json()
        self.assertIn("error", body)
        self.assertIn("Upgrade", body["error"])


class OutputCleanerTests(TestCase):
    def test_normalizes_primary_text_fields(self):
        from studio.services.output_cleaner import normalize_variant

        result = normalize_variant(
            {
                "headline": "Summer Sale",
                "primary_text": "Save 20% this week only.",
                "call_to_action": "Shop Now",
            }
        )
        self.assertEqual(result["headline"], "Summer Sale")
        self.assertEqual(result["body"], "Save 20% this week only.")
        self.assertEqual(result["cta"], "Shop Now")


class BillingStatusTests(TestCase):
    def test_billing_status_authenticated(self):
        user = User.objects.create_user(
            email="billing@example.com",
            username="billing@example.com",
            password="SecurePass123!",
        )
        client = APIClient()
        login = client.post(
            "/api/auth/login/",
            {"email": user.email, "password": "SecurePass123!"},
            format="json",
        )
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.json()['access']}")
        res = client.get("/api/auth/billing/status/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["plan"], "free")
        self.assertIn("generations_limit", res.json())


class AnalyticsDemoTests(TestCase):
    def test_analytics_marked_as_demo(self):
        user = User.objects.create_user(
            email="demo@example.com",
            username="demo@example.com",
            password="SecurePass123!",
        )
        client = APIClient()
        login = client.post(
            "/api/auth/login/",
            {"email": user.email, "password": "SecurePass123!"},
            format="json",
        )
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.json()['access']}")
        response = client.get("/api/analytics/")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["demo_mode"])
        self.assertEqual(response.json()["metrics_source"], "simulated")
