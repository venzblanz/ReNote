from unittest.mock import patch
from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core import mail

User = get_user_model()


class PasswordResetTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="oldpassword123",
        )
        self.reset_url = reverse("login:password_reset")
        self.reset_done_url = reverse("login:password_reset_done")

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_password_reset_success_sends_email(self):
        """Test submitting valid user email generates and sends reset email."""
        response = self.client.post(self.reset_url, {"email": "testuser@example.com"})
        self.assertRedirects(response, self.reset_done_url)
        self.assertEqual(len(mail.outbox), 1)
        sent_email = mail.outbox[0]
        self.assertEqual(sent_email.to, ["testuser@example.com"])
        self.assertIn("Reset your password", sent_email.subject)
        self.assertIn("reset/", sent_email.body)

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_password_reset_nonexistent_email(self):
        """Nonexistent email redirects to done without sending email or leaking user existence."""
        response = self.client.post(self.reset_url, {"email": "nobody@example.com"})
        self.assertRedirects(response, self.reset_done_url)
        self.assertEqual(len(mail.outbox), 0)

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    @patch("django.core.mail.message.EmailMultiAlternatives.send")
    def test_password_reset_handles_mail_exception_gracefully(self, mock_send):
        """
        When email delivery fails (e.g. SMTP connection timeout / blocked port),
        the view must NOT crash with 500. CustomPasswordResetForm catches it,
        logs the error, and redirects gracefully to password_reset_done.
        """
        mock_send.side_effect = TimeoutError("Connection to SMTP port timed out")

        with self.assertLogs("apps.login.forms", level="ERROR") as cm:
            response = self.client.post(self.reset_url, {"email": "testuser@example.com"})

        self.assertRedirects(response, self.reset_done_url)
        self.assertTrue(any("Failed to send password reset email" in log for log in cm.output))
