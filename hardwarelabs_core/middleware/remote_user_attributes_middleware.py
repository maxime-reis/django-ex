# -*- coding: utf-8 -*-
from django.contrib import auth
from django.contrib.auth.models import Group
from django.contrib.auth.backends import RemoteUserBackend
from django.contrib.auth.middleware import (
    RemoteUserMiddleware, PersistentRemoteUserMiddleware
)
from django.conf import settings


class RemoteUserAttrMiddleware(PersistentRemoteUserMiddleware):

    def add_group_if_nonexistent(self, name):
        """ Check if group exists, add it if not."""
        if name not in [group.name for group in Group.objects.all()]:
            Group.objects.create(name=name).save()

    def update_user_groups(self, request):
        """
        Get remote user ADFS groups and add corresponding django group
        – if any – to django user.
        """
        adfs_groups = [request.META[key] for key in request.META if key.startswith('ADFS_GROUP')]
        user_django_groups = [group.name for group in request.user.groups.all()]
        for adfs_group in adfs_groups:
            if adfs_group in settings.ADFS_TO_DJANGO_GROUPS_MAPPING:
                groups_to_add_to_user = [django_group for django_group in settings.ADFS_TO_DJANGO_GROUPS_MAPPING[adfs_group] if django_group not in user_django_groups]
                for django_group in groups_to_add_to_user:
                    self.add_group_if_nonexistent(django_group)
                    group_obj = Group.objects.get(name=django_group)
                    request.user.groups.add(group_obj)
            if adfs_group in settings.ADFS_GROUPS_THAT_GIVE_STAFF_STATUS:
                request.user.is_staff = True
            if adfs_group in settings.ADFS_GROUPS_THAT_GIVE_SUPERUSER_STATUS:
                request.user.is_superuser = True

    def update_user(self, request):
        """ Get remote user metadata and save it in the django user object."""
        stored_backend = auth.load_backend(
            request.session.get(auth.BACKEND_SESSION_KEY, '')
        )
        if isinstance(stored_backend, RemoteUserBackend):
            user = request.user
            email = request.META.get("ADFS_EMAIL", None)
            if email is not None:
                user.email = email
            firstname = request.META.get("ADFS_FIRSTNAME", None)
            if firstname is not None:
                user.first_name = firstname
            lastname = request.META.get("ADFS_LASTNAME", None)
            if lastname is not None:
                user.last_name = lastname
            self.update_user_groups(request)
            # Add user in the base group.
            self.add_group_if_nonexistent(settings.BASE_GROUP)
            base_group = Group.objects.get(name=settings.BASE_GROUP)
            if base_group not in user.groups.all():
                user.groups.add(base_group)
            # Save user object
            user.save()

    def process_request(self, request):
        # AuthenticationMiddleware is required so that request.user exists.
        if not hasattr(request, 'user'):
            raise ImproperlyConfigured(
                "The Django remote user auth middleware requires the"
                " authentication middleware to be installed. Edit your"
                " MIDDLEWARE_CLASSES setting to insert"
                " 'django.contrib.auth.middleware.AuthenticationMiddleware'"
                " before the RemoteUserMiddleware class.")
        try:
            username = request.META[self.header]
        except KeyError:
            # If specified header doesn't exist then remove any existing
            # authenticated remote-user, or return (leaving request.user set to
            # AnonymousUser by the AuthenticationMiddleware).
            if request.user.is_authenticated():
                self._remove_invalid_user(request)
            return
        # If the user is already authenticated and that user is the user we are
        # getting passed in the headers, then the correct user is already
        # persisted in the session and we don't need to continue.
        if request.user.is_authenticated():
            if request.user.get_username() == self.clean_username(
                username, request
            ):
                return
            else:
                # An authenticated user is associated with the request, but
                # it does not match the authorized user in the header.
                self._remove_invalid_user(request)

        # We are seeing this user for the first time in this session, attempt
        # to authenticate the user.
        user = auth.authenticate(remote_user=username)
        if user:
            # User is valid.  Set request.user and persist user in the session
            # by logging the user in.
            auth.login(request, user)
            # Check user attributes (email, name, etc.) and update if necessary
            self.update_user(request)
