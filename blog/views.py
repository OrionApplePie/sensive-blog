from django.shortcuts import render

from blog.models import Post, Tag
from django.db.models import Count, Prefetch


def serialize_post_optimized(post):
    return {
        "title": post.title,
        "teaser_text": post.text[:200],
        "author": post.author.username,
        "comments_amount": post.comments_count,
        "image_url": post.image.url if post.image else None,
        "published_at": post.published_at,
        "slug": post.slug,
        "tags": [serialize_tag_optimized(tag) for tag in post.tags.all()],
        "first_tag_title": post.tags.first().title,
    }


def serialize_tag_optimized(tag):
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

    most_popular_tags = Tag.objects.popular()[:5].fetch_with_post_count()

    context = {
        "most_popular_posts": [
            serialize_post_optimized(post) for post in most_popular_posts
        ],
        "page_posts": [serialize_post_optimized(post) for post in most_fresh_posts],
        "popular_tags": [serialize_tag_optimized(tag) for tag in most_popular_tags],
    }
    return render(request, "index.html", context)


def post_detail(request, slug):
    post = Post.objects.prefetch_related("tags").get(slug=slug)
    comments = post.comments.all()
    serialized_comments = []
    for comment in comments:
        serialized_comments.append(
            {
                "text": comment.text,
                "published_at": comment.published_at,
                "author": comment.author.username,
            }
        )

    likes_count = post.likes.all().count()

    related_tags = post.tags.popular().fetch_with_post_count()

    serialized_post = {
        "title": post.title,
        "text": post.text,
        "author": post.author.username,
        "comments": serialized_comments,
        "likes_amount": likes_count,
        "image_url": post.image.url if post.image else None,
        "published_at": post.published_at,
        "slug": post.slug,
        "tags": [serialize_tag_optimized(tag) for tag in related_tags],
    }

    most_popular_tags = Tag.objects.popular()[:5].fetch_with_post_count()

    most_popular_posts = (
        Post.objects.popular()
        .prefetch_related("author")[:5]
        .fetch_with_comments_count()
    )

    context = {
        "post": serialized_post,
        "popular_tags": [serialize_tag_optimized(tag) for tag in most_popular_tags],
        "most_popular_posts": [
            serialize_post_optimized(post) for post in most_popular_posts
        ],
    }
    return render(request, "post-details.html", context)


def tag_filter(request, tag_title):
    tag = Tag.objects.get(title=tag_title)

    most_popular_tags = Tag.objects.popular()[:5].fetch_with_post_count()

    most_popular_posts = (
        Post.objects.popular()
        .prefetch_related("author")[:5]
        .fetch_with_comments_count()
    )

    related_posts = tag.posts.popular()[:20].fetch_with_comments_count()

    context = {
        "tag": tag.title,
        "popular_tags": [serialize_tag_optimized(tag) for tag in most_popular_tags],
        "posts": [serialize_post_optimized(post) for post in related_posts],
        "most_popular_posts": [
            serialize_post_optimized(post) for post in most_popular_posts
        ],
    }
    return render(request, "posts-list.html", context)


def contacts(request):
    # позже здесь будет код для статистики заходов на эту страницу
    # и для записи фидбека
    return render(request, "contacts.html", {})
