from timeit import default_timer as timer

from django.conf import settings
from django.http import Http404, HttpResponseBadRequest
from django.shortcuts import redirect

from main import denylist, models, util


def host_middleware(get_response):
    def middleware(request):
        host = request.META.get("HTTP_HOST")

        # no http Host header in testing
        if not host:
            return get_response(request)

        host_parts = host.split(".")
        canonical_parts = settings.CANONICAL_HOST.split(".")

        if host == settings.CANONICAL_HOST:
            return get_response(request)
        elif (
            len(host_parts) == 3
            and host_parts[1] == canonical_parts[0]  # should be "mataroa"
            and host_parts[2] == canonical_parts[1]  # should be "blog"
        ):
            # this case is for <subdomain>.capivaras.dev:
            # * set subdomain to given subdomain
            # * the lists indexes are different because CANONICAL_HOST has no subdomain
            # * also validation will happen inside views
            request.subdomain = host_parts[0]

            # check if subdomain is disallowed
            if request.subdomain in denylist.DISALLOWED_USERNAMES:
                return redirect(f"{util.get_protocol()}//{settings.CANONICAL_HOST}")
            # check if subdomain exists as blog
            elif models.User.objects.filter(username=request.subdomain).exists():
                request.blog_user = models.User.objects.get(username=request.subdomain)

                # redirect to custom and/or retired urls for cases:
                # * logged out / anon users
                # * logged in but on other user's subdomain
                if not request.user.is_authenticated or (
                    request.user.is_authenticated
                    and request.user.username != request.subdomain
                ):
                    redir_domain = ""
                    if request.blog_user.custom_domain:  # user has set custom domain
                        redir_domain = (
                            request.blog_user.custom_domain + request.path_info
                        )

                    # user has retired their mataroa blog, redirect to new domain
                    if request.blog_user.redirect_domain:
                        redir_domain = (
                            request.blog_user.redirect_domain + request.path_info[5:]
                        )

                    # if there is no protocol prefix,
                    # prepend double slashes to indicate other domain
                    if redir_domain and "://" not in redir_domain:
                        redir_domain = "//" + redir_domain

                    if redir_domain:
                        return redirect(redir_domain)
            else:
                raise Http404()
        elif models.User.objects.filter(custom_domain=host).exists():
            # custom domain case
            request.blog_user = models.User.objects.get(custom_domain=host)
            request.subdomain = request.blog_user.username

            # if user has retired their mataroa blog (and keeps the custom domain)
            # redirect to new domain
            if request.blog_user.redirect_domain:
                redir_domain = request.blog_user.redirect_domain + request.path_info[5:]

                # if there is no protocol prefix,
                # prepend double slashes to indicate other domain
                if "://" not in redir_domain:
                    redir_domain = "//" + redir_domain

                return redirect(redir_domain)

        else:
            return HttpResponseBadRequest()

        return get_response(request)

    return middleware


def speed_middleware(get_response):
    def middleware(request):
        request.start = timer()

        response = get_response(request)

        end = timer()
        response["X-Request-Time"] = end - request.start
        return response

    return middleware
