import base64
import binascii
import os
import uuid

import bleach
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils import timezone

from main import util, validators


def _generate_key():
    """Return 32-char random string."""
    return binascii.b2a_hex(os.urandom(16)).decode("utf-8")


class User(AbstractUser):
    username = models.CharField(
        max_length=150,
        unique=True,
        help_text="This is your subdomain. Lowercase alphanumeric.",
        validators=[
            validators.AlphanumericHyphenValidator(),
            validators.HyphenOnlyValidator(),
        ],
        error_messages={"unique": "A user with that username already exists."},
    )
    email = models.EmailField(
        blank=True,
        null=True,
        help_text="Optional, but also the only way to recover password if forgotten.",
    )
    api_key = models.CharField(max_length=32, default=_generate_key, unique=True)
    about = models.TextField(blank=True, null=True)
    blog_title = models.CharField(max_length=500, blank=True, null=True)
    blog_byline = models.TextField(
        blank=True,
        null=True,
        help_text="Supports markdown",
    )
    subscribe_note = models.CharField(
        max_length=350,
        blank=True,
        null=True,
        default="Subscribe via [RSS](/rss/) / [via Email](/newsletter/).",
        help_text="Default: Subscribe via [RSS](/rss/) / [via Email](/newsletter/).",
    )
    footer_note = models.TextField(
        blank=True,
        null=True,
        default="Powered by [capivaras.dev](https://capivaras.dev/).",
        help_text="Supports markdown",
    )

    redirect_domain = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        help_text="Retiring your mataroa blog? We can redirect to your new domain.",
        validators=[validators.validate_domain_name],
    )
    custom_domain = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        help_text="To setup: Add an A record in your domain's DNS with IP 91.107.232.152",
        validators=[validators.validate_domain_name],
    )

    notifications_on = models.BooleanField(
        default=True,
        help_text="Allow/disallow people subscribing for email newsletter for new posts.",
        verbose_name="Newsletter",
    )
    mail_export_on = models.BooleanField(
        default=False,
        help_text="Enable/disable auto emailing of account exports every month.",
        verbose_name="Mail export",
    )
    post_backups_on = models.BooleanField(
        default=False,
        help_text="Enable/disable automatic post backups.",
        verbose_name="Post Backups On",
    )
    markdown_link_paste_on = models.BooleanField(
        default=False,
        help_text="Enable/disable automatic markdown link formatting on paste.",
        verbose_name="Markdown link formatting",
    )
    export_unsubscribe_key = models.UUIDField(default=uuid.uuid4, unique=True)

    # webring related
    webring_name = models.CharField(max_length=200, blank=True, null=True)
    webring_url = models.URLField(
        blank=True,
        null=True,
        verbose_name="Webring info URL",
        help_text="Informational URL.",
    )
    webring_prev_url = models.URLField(
        blank=True,
        null=True,
        verbose_name="Webring previous URL",
        help_text="URL for your webring's previous website.",
    )
    webring_next_url = models.URLField(
        blank=True,
        null=True,
        verbose_name="Webring next URL",
        help_text="URL for your webring's next website.",
    )

    is_premium = models.BooleanField(default=False)
    is_grandfathered = models.BooleanField(default=False)

    # moderation
    is_approved = models.BooleanField(default=False)

    class Meta:
        ordering = ["-id"]

    @property
    def blog_absolute_url(self):
        protocol = f"{util.get_protocol()}"
        return f"{protocol}//{self.username}.{settings.CANONICAL_HOST}"

    @property
    def blog_url(self):
        url = f"{util.get_protocol()}"
        if self.custom_domain:
            return url + f"//{self.custom_domain}"
        else:
            return url + f"//{self.username}.{settings.CANONICAL_HOST}"

    @property
    def blog_byline_as_text(self):
        linker = bleach.linkifier.Linker(callbacks=[lambda attrs, new: None])
        html_text = util.md_to_html(self.blog_byline, strip_tags=True)
        return linker.linkify(html_text)

    @property
    def blog_byline_as_html(self):
        return util.md_to_html(self.blog_byline)

    @property
    def about_as_html(self):
        return util.md_to_html(self.about, strip_tags=True)

    @property
    def subscribe_note_as_html(self):
        return util.md_to_html(self.subscribe_note)

    @property
    def footer_note_as_html(self):
        return util.md_to_html(self.footer_note)

    @property
    def post_count(self):
        return Post.objects.filter(owner=self).count()

    @property
    def class_status(self):
        if self.is_premium or self.is_grandfathered:
            return "💠"
        return "∅"

    def get_export_unsubscribe_url(self):
        domain = self.custom_domain or f"{self.username}.{settings.CANONICAL_HOST}"
        path = reverse("export_unsubscribe_key", args={self.export_unsubscribe_key})
        return f"//{domain}{path}"

    def reset_api_key(self):
        self.api_key = _generate_key()
        self.save()

    def __str__(self):
        return self.username


class Post(models.Model):
    title = models.CharField(max_length=300)
    slug = models.CharField(max_length=300)
    body = models.TextField(blank=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateField(
        default=timezone.now,
        blank=True,
        null=True,
        help_text="Leave blank to keep as draft/unpublished. Use a future date for auto-posting.",
    )
    broadcasted_at = models.DateTimeField(blank=True, null=True, default=None)

    class Meta:
        ordering = ["-published_at", "-created_at"]
        unique_together = [["slug", "owner"]]

    @property
    def body_as_html(self):
        return util.md_to_html(self.body)

    @property
    def body_as_text(self):
        as_html = util.md_to_html(self.body)
        return bleach.clean(as_html, strip=True, tags=[])

    @property
    def is_draft(self):
        return not self.published_at

    @property
    def is_published(self):
        # draft case
        if not self.published_at:
            return False
        # future publishing date case
        if self.published_at > timezone.now().date():  # noqa: SIM103
            return False
        return True

    def get_absolute_url(self):
        path = reverse("post_detail", kwargs={"slug": self.slug})
        return f"//{self.owner.username}.{settings.CANONICAL_HOST}{path}"

    def get_proper_url(self):
        """Returns custom domain URL if custom_domain exists, else subdomain URL."""
        if self.owner.custom_domain:
            path = reverse("post_detail", kwargs={"slug": self.slug})
            return f"//{self.owner.custom_domain}{path}"
        else:
            return self.get_absolute_url()

    def __str__(self):
        return self.title


class Image(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=300)  # original filename
    slug = models.CharField(max_length=300, unique=True)
    data = models.BinaryField()
    extension = models.CharField(max_length=10)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]

    @property
    def filename(self):
        return self.slug + "." + self.extension

    @property
    def data_as_base64(self):
        return base64.b64encode(self.data).decode("utf-8")

    @property
    def data_size(self):
        """Get image size in MB."""
        return round(len(self.data) / (1024 * 1024), 2)

    @property
    def raw_url_absolute(self):
        path = reverse(
            "image_raw", kwargs={"slug": self.slug, "extension": self.extension}
        )
        return f"//{settings.CANONICAL_HOST}{path}"

    def get_absolute_url(self):
        path = reverse("image_detail", kwargs={"slug": self.slug})
        return f"//{settings.CANONICAL_HOST}{path}"

    def __str__(self):
        return self.name


class Page(models.Model):
    title = models.CharField(max_length=300)
    slug = models.CharField(
        max_length=300,
        validators=[validators.AlphanumericHyphenValidator()],
        help_text="Lowercase letters, numbers, and - (hyphen) allowed.",
    )
    body = models.TextField(blank=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_hidden = models.BooleanField(
        default=False,
        help_text="If checked, page link will not appear on the blog header.",
    )

    class Meta:
        ordering = ["slug"]
        unique_together = [["slug", "owner"]]

    @property
    def body_as_html(self):
        return util.md_to_html(self.body)

    def get_absolute_url(self):
        path = reverse("page_detail", kwargs={"slug": self.slug})
        return f"//{self.owner.username}.{settings.CANONICAL_HOST}{path}"

    def __str__(self):
        return self.title


class AnalyticPage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    path = models.CharField(max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.created_at.strftime("%c") + ": " + self.user.username


class AnalyticPost(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.created_at.strftime("%c") + ": " + self.post.title


class Notification(models.Model):
    blog_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    email = models.EmailField()
    unsubscribe_key = models.UUIDField(default=uuid.uuid4, unique=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["email"]
        unique_together = [["email", "blog_user"]]

    def get_unsubscribe_url(self):
        domain = (
            self.blog_user.custom_domain
            or f"{self.blog_user.username}.{settings.CANONICAL_HOST}"
        )
        path = reverse("notification_unsubscribe_key", args={self.unsubscribe_key})
        return f"//{domain}{path}"

    def __str__(self):
        return self.email + " – " + str(self.unsubscribe_key)


class NotificationRecord(models.Model):
    """
    NotificationRecord model is to keep track of all notifications
    for the newsletter feature.
    """

    notification = models.ForeignKey(Notification, on_delete=models.SET_NULL, null=True)
    post = models.ForeignKey(Post, on_delete=models.SET_NULL, null=True)
    sent_at = models.DateTimeField(default=timezone.now, null=True)

    class Meta:
        ordering = ["-sent_at"]
        unique_together = [["post", "notification"]]

    def __str__(self):
        if not self.sent_at:
            return str(self.id)
        if self.notification:
            return self.sent_at.strftime("%c") + " – " + self.notification.email
        else:
            return self.sent_at.strftime("%c") + " – NULL"


class ExportRecord(models.Model):
    """ExportRecord model is to keep track of each export email."""

    name = models.CharField(max_length=150)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-sent_at"]

    def __str__(self):
        return self.name


class Snapshot(models.Model):
    """Snapshot model is used to keep track of all versions of Posts."""

    title = models.CharField(max_length=300)
    body = models.TextField(blank=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
