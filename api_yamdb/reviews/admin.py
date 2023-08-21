from django import forms
from django.contrib import admin

from .models import Category, Comment, Genre, Review, Title


class TitleAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "description"]
    list_filter = ["name", "description"]
    search_fields = ["name"]


admin.site.register(Title, TitleAdmin)


class ReviewAdminForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = "__all__"

    title = forms.ModelChoiceField(queryset=Title.objects.all(), required=True)


class ReviewAdmin(admin.ModelAdmin):
    title = forms.ModelChoiceField(queryset=Title.objects.all(), required=True)
    list_display = ["text", "id", "pub_date", "author"]
    list_filter = ["author", "pub_date"]
    search_fields = ["text"]
    form = ReviewAdminForm


admin.site.register(Review, ReviewAdmin)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    list_filter = ["name", "slug"]
    search_fields = ["name"]


admin.site.register(Category, CategoryAdmin)


class GenreAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    list_filter = ["name", "slug"]
    search_fields = ["name"]


admin.site.register(Genre, GenreAdmin)


class CommentAdmin(admin.ModelAdmin):
    list_display = ["text", "id"]
    list_filter = ["text", "id"]
    search_fields = ["text"]


admin.site.register(Comment, CommentAdmin)
