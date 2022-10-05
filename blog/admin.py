from django.contrib import admin
from django.utils.safestring import mark_safe

from blog.models import Post, Tag, Comment


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    fields = ('title', 'slug', 'author', 'image', 'preview',
              'text', 'tags', 'published_at', 'likes',)
    list_display = ('title', 'slug', 'published_at',)
    list_display_links = ('title',)
    list_filter = ('published_at',)
    raw_id_fields = ('author', 'likes', 'tags',)
    readonly_fields = ('preview',)
    search_fields = ('title',)

    def preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" style="max-height: 200px;">')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('title',)
    fields = ('title',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    fields = ('text', 'published_at', 'author', 'post',)
    list_display = ('text', 'published_at',)
    list_display_links = ('text',)
    list_filter = ('published_at',)
    raw_id_fields = ('post', 'author',)
