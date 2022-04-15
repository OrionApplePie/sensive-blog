from django.shortcuts import render

from blog.models import Post, Tag
from django.db.models import Count, Prefetch


def serialize_post(post):
    tags = [serialize_tag(tag) for tag in post.tags.all()]
    return {
        "title": post.title,
        "teaser_text": post.text[:200],
        "author": post.author.username,
        "comments_amount": post.comments_count,
        "image_url": post.image.url if post.image else None,
        "published_at": post.published_at,
        "slug": post.slug,
        "tags": tags,
        "first_tag_title": tags[0]["title"] if tags else "N/A",
    }


def serialize_tag(tag):
    return {
        "title": tag.title,
        "posts_with_tag": tag.posts_count,
    }


def index(request):
    tags_queryset = Tag.objects.annotate(posts_count=Count("posts"))

    most_popular_posts = (
        Post.objects.popular()
        .prefetch_related("author")[:5]
        .prefetch_related(Prefetch("tags", queryset=tags_queryset))
        .fetch_with_comments_count()
    )
    most_fresh_posts = (
        Post.objects.prefetch_related("author")
        .prefetch_related(Prefetch("tags", queryset=tags_queryset))
        .order_by("-published_at")[:5]
        .fetch_with_comments_count()
    )

    most_popular_tags = Tag.objects.popular()[:5].annotate(posts_count=Count("posts"))

    context = {
        "most_popular_posts": [serialize_post(post) for post in most_popular_posts],
        "page_posts": [serialize_post(post) for post in most_fresh_posts],
        "popular_tags": [serialize_tag(tag) for tag in most_popular_tags],
    }
    return render(request, "index.html", context)


def post_detail(request, slug):
    post = (
        Post.objects.prefetch_related("tags")
        .prefetch_related("comments")
        .get(slug=slug)
    )
    comments = post.comments.prefetch_related("author").all()
    serialized_comments = [
        {
            "text": comment.text,
            "published_at": comment.published_at,
            "author": comment.author.username,
        }
        for comment in comments
    ]

    likes_count = post.likes.all().count()

    related_tags = post.tags.popular().annotate(posts_count=Count("posts"))

    serialized_post = {
        "title": post.title,
        "text": post.text,
        "author": post.author.username,
        "comments": serialized_comments,
        "likes_amount": likes_count,
        "image_url": post.image.url if post.image else None,
        "published_at": post.published_at,
        "slug": post.slug,
        "tags": [serialize_tag(tag) for tag in related_tags],
    }

    most_popular_tags = Tag.objects.popular()[:5].annotate(posts_count=Count("posts"))

    tags_queryset = Tag.objects.annotate(posts_count=Count("posts"))

    most_popular_posts = (
        Post.objects.popular()
        .prefetch_related("author")[:5]
        .prefetch_related(Prefetch("tags", queryset=tags_queryset))
        .fetch_with_comments_count()
    )

    context = {
        "post": serialized_post,
        "popular_tags": [serialize_tag(tag) for tag in most_popular_tags],
        "most_popular_posts": [serialize_post(post) for post in most_popular_posts],
    }
    return render(request, "post-details.html", context)


def tag_filter(request, tag_title):
    tags_queryset = Tag.objects.annotate(posts_count=Count("posts"))
    tag = tags_queryset.filter(title=tag_title)

    most_popular_tags = Tag.objects.popular()[:5].annotate(posts_count=Count("posts"))

    most_popular_posts = (
        Post.objects.popular()
        .prefetch_related("author")[:5]
        .prefetch_related(Prefetch("tags", queryset=tags_queryset))
        .fetch_with_comments_count()
    )

    related_posts = (
        Post.objects.popular()[:20]
        .prefetch_related("author")
        .prefetch_related(Prefetch("tags", queryset=tag))
        .fetch_with_comments_count()
    )

    context = {
        "tag": tag.first().title,
        "popular_tags": [serialize_tag(tag) for tag in most_popular_tags],
        "posts": [serialize_post(post) for post in related_posts],
        "most_popular_posts": [serialize_post(post) for post in most_popular_posts],
    }
    return render(request, "posts-list.html", context)


def contacts(request):
    # позже здесь будет код для статистики заходов на эту страницу
    # и для записи фидбека
    return render(request, "contacts.html", {})
