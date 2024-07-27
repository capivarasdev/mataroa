import io
import uuid
import zipfile

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render

from main import models, util


def prepend_hugo_frontmatter(body, post_title, pub_date, post_slug):
    frontmatter = "+++\n"
    frontmatter += f'title = "{post_title}"\n'
    frontmatter += f"date = {pub_date}\n"
    frontmatter += f'slug = "{post_slug}"\n'
    frontmatter += "+++\n"
    frontmatter += "\n"

    return frontmatter + body


def export_index(request):
    return render(request, "main/export_index.html")


@login_required
def export_markdown(request):
    if request.method == "POST":
        # get all user posts and add them into export_posts encoded
        posts = models.Post.objects.filter(owner=request.user)
        export_posts = []
        for p in posts:
            pub_date = p.published_at or p.created_at
            title = p.slug + ".md"
            body = f"# {p.title}\n\n"
            body += f"> Published on {pub_date.strftime('%b %-d, %Y')}\n\n"
            body += f"{p.body}\n"
            export_posts.append((title, io.BytesIO(body.encode())))

        # create zip archive in memory
        export_name = "export-markdown-" + str(uuid.uuid4())[:8]
        container_dir = f"{request.user.username}-mataroa-blog"
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(
            zip_buffer, "a", zipfile.ZIP_DEFLATED, False
        ) as export_archive:
            for file_name, data in export_posts:
                export_archive.writestr(
                    export_name + f"/{container_dir}/" + file_name, data.getvalue()
                )

        response = HttpResponse(zip_buffer.getvalue(), content_type="application/zip")
        response["Content-Disposition"] = f"attachment; filename={export_name}.zip"
        return response


@login_required
def export_hugo(request):
    if request.method == "POST":
        # load hugo templates
        with open("./export_base_hugo/config.toml") as hugo_config_file:
            blog_title = request.user.blog_title or f"{request.user.username} blog"
            blog_byline = request.user.blog_byline or ""
            hugo_config = (
                hugo_config_file.read()
                .replace("example.com", f"{request.user.username}.mataroa.blog")
                .replace("Example blog title", blog_title)
                .replace(
                    "Example blog description", "\\n".join(blog_byline.splitlines())
                )
            )
        with open("./export_base_hugo/theme.toml") as hugo_theme_file:
            hugo_theme = hugo_theme_file.read()
        with open("./main/templates/assets/style.css") as hugo_styles_file:
            hugo_styles = hugo_styles_file.read()
        with open("./export_base_hugo/single.html") as hugo_single_file:
            hugo_single = hugo_single_file.read()
        with open("./export_base_hugo/list.html") as hugo_list_file:
            hugo_list = hugo_list_file.read()
        with open("./export_base_hugo/index.html") as hugo_index_file:
            hugo_index = hugo_index_file.read()
        with open("./export_base_hugo/baseof.html") as hugo_baseof_file:
            hugo_baseof = hugo_baseof_file.read()

        # get all user posts and add them into export_posts encoded
        posts = models.Post.objects.filter(owner=request.user)
        export_posts = []
        for p in posts:
            title = p.slug + ".md"
            pub_date = p.published_at or p.created_at.date()
            body = prepend_hugo_frontmatter(
                p.body, util.escape_quotes(p.title), pub_date, p.slug
            )
            export_posts.append((title, io.BytesIO(body.encode())))

        # create zip archive in memory
        export_name = "export-hugo-" + str(uuid.uuid4())[:8]
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(
            zip_buffer, "a", zipfile.ZIP_DEFLATED, False
        ) as export_archive:
            export_archive.writestr(export_name + "/config.toml", hugo_config)
            export_archive.writestr(
                export_name + "/themes/mataroa/theme.toml", hugo_theme
            )
            export_archive.writestr(
                export_name + "/themes/mataroa/static/style.css", hugo_styles
            )
            export_archive.writestr(
                export_name + "/themes/mataroa/layouts/index.html", hugo_index
            )
            export_archive.writestr(
                export_name + "/themes/mataroa/layouts/_default/single.html",
                hugo_single,
            )
            export_archive.writestr(
                export_name + "/themes/mataroa/layouts/_default/list.html", hugo_list
            )
            export_archive.writestr(
                export_name + "/themes/mataroa/layouts/_default/baseof.html",
                hugo_baseof,
            )
            for file_name, data in export_posts:
                export_archive.writestr(
                    export_name + "/content/blog/" + file_name, data.getvalue()
                )

        response = HttpResponse(zip_buffer.getvalue(), content_type="application/zip")
        response["Content-Disposition"] = f"attachment; filename={export_name}.zip"
        return response


def export_unsubscribe_key(request, unsubscribe_key):
    if models.User.objects.filter(export_unsubscribe_key=unsubscribe_key).exists():
        user = models.User.objects.get(export_unsubscribe_key=unsubscribe_key)
        user.mail_export_on = False
        user.export_unsubscribe_key = uuid.uuid4()
        user.save()
        return render(
            request,
            "main/export_unsubscribe_success.html",
            {
                "blog_user": request.blog_user,
                "unsubscribed": True,
                "email": user.email,
            },
        )
    else:
        return render(
            request,
            "main/export_unsubscribe_success.html",
            {
                "blog_user": request.blog_user,
                "unsubscribed": False,
            },
        )


@login_required
def export_print(request):
    return render(
        request,
        "main/export_print.html",
        {
            "posts": models.Post.objects.filter(owner=request.user).order_by(
                "-published_at"
            ),
        },
    )
