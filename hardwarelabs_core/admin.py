from django.contrib import admin
from django import forms
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.auth.models import User, Group, Permission
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.utils.translation import ugettext_lazy as _

from django.contrib.admin.options import flatten_fieldsets

from guardian.admin import UserManage, GroupManage, GuardedModelAdmin
from guardian.shortcuts import get_objects_for_user


class UserManageWithUsersListWidget(UserManage):
    user = forms.ModelChoiceField(
        queryset=User.objects.all().order_by('username')
    )


class GroupManageWithGroupsListWidget(GroupManage):
    group = forms.ModelChoiceField(queryset=Group.objects.all().order_by('name'))


class GuardedModelAdminMod(GuardedModelAdmin):
    def get_queryset(self, request):
        qs = super(GuardedModelAdminMod, self).get_queryset(request)
        return get_objects_for_user(request.user, [], qs)

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = self.readonly_fields
        if not request.user.is_superuser:
            readonly_fields = [field.name for field in self.opts._get_fields() if hasattr(self.model, field.name)]
        return readonly_fields

    def get_obj_perms_user_select_form(self, request):
        """
        Returns form class for selecting a user for permissions management. By
        default :form:`UserManageWithUsersListWidget` is returned.
        """
        return UserManageWithUsersListWidget

    def get_obj_perms_group_select_form(self, request):
        """
        Returns form class for selecting a group for permissions management. By
        default :form:`GroupManageWithGroupsListWidget` is returned.
        """
        return GroupManageWithGroupsListWidget


class GroupAdminForm(forms.ModelForm):
    users = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        required=False,
        widget=FilteredSelectMultiple(
            verbose_name=_('Users'),
            is_stacked=False
        )
    )

    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all(),
        required=False,
        widget=FilteredSelectMultiple(
            verbose_name=_('Permissions'),
            is_stacked=False
        )
    )

    class Meta:
        model = Group
        fields = ['name', 'permissions']

    def __init__(self, *args, **kwargs):
        super(GroupAdminForm, self).__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            self.fields['users'].initial = self.instance.user_set.all()

    def save(self, commit=True):
        selected_users = self.cleaned_data['users']
        added_users = []
        removed_users = []
        if self.fields['users'].initial is not None:
            added_users = [user for user in selected_users if user not in self.fields['users'].initial]
            removed_users = [user for user in self.fields['users'].initial if user not in selected_users]

        group = super(GroupAdminForm, self).save(commit=False)

        for user in added_users:
            user.groups.add(group)
            user.save()
        for user in removed_users:
            user.groups.remove(group)
            user.save()
        group.save()

        return group


class GroupAdmin(admin.ModelAdmin):
    form = GroupAdminForm


class CustomUserAdmin(GuardedModelAdminMod, UserAdmin):
    pass


class CustomGroupAdmin(GuardedModelAdminMod, GroupAdmin):
    pass

admin.site.unregister(Group)
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Group, CustomGroupAdmin)
