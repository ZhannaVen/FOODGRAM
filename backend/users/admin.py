from django.contrib import admin

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'username',
        'email',
        'first_name',
        'last_name',
        'followers',
        'following',
        'number_of_recipes'

    )
    search_fields = ('email', 'username', 'first_name', 'last_name')
    list_filter = ('email', 'first_name')
    empty_value_display = '-empty-'

    def followers(self, obj):
        """The function counts total number
        of followers.
        """
        return obj.follower.count()

    def following(self, obj):
        """The function counts total number
        of followings.
        """
        return obj.following.count()

    def number_of_recipes(self, obj):
        """The function counts total number
        of recipes.
        """
        return obj.recipes.count()
