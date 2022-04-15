from django.contrib import admin
from blog.models import Post, Tag, Comment


class CommentAdmin(admin.ModelAdmin):
    raw_id_fields = (
        "post",
        "author",
    )


class PostAdmin(admin.ModelAdmin):
    raw_id_fields = (
        "author",
        "likes",
        "tags",
    )


admin.site.register(Post, PostAdmin)
admin.site.register(Tag)
admin.site.register(Comment, CommentAdmin)
