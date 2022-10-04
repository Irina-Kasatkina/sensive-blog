from django.contrib.auth.models import User
from django.db import models
from django.db.models import Count, Prefetch
from django.urls import reverse


class PostQuerySet(models.QuerySet):
    def popular(self, max_posts_count=5):
        return (self.annotate(likes_count=Count('likes'))
                    .order_by('-likes_count')[:max_posts_count]
                    .fetch_with_author_and_tags_and_comments_count())

    def fresh(self, max_posts_count=5):
        return (self.order_by('-published_at')[:max_posts_count]
                    .annotate(comments_count=Count('comments'))
                    .fetch_with_author_and_tags())

    def detail(self, slug):
        comments_prefetch = Prefetch('comments', queryset=Comment.objects.prefetch_related('author'))
        return (self.filter(slug=slug)
                    .annotate(likes_count=Count('likes'))
                    .prefetch_related('author', comments_prefetch)
                    .fetch_with_author_and_tags()
                    .first())

    def fetch_with_comments_count(posts):
        """Функция для присоединения к каждому из постов запроса псевдо-поля
           comments_count с количеством комментариев к посту.
           Вызывать эту функцию предпочтительнее, чем использовать второй annotate
           в запросе, потому что два annotate приводят к очень долгому выполнению запроса.
        """

        posts_ids = [post.id for post in posts]
        posts_with_comments_count = (Post.objects.filter(id__in=posts_ids)
                                                 .annotate(comments_count=Count('comments')))
        ids_and_comments = posts_with_comments_count.values_list('id', 'comments_count')
        count_for_id = dict(ids_and_comments)
        for post in posts:
            post.comments_count = count_for_id[post.id]
        return list(posts)

    def fetch_with_author_and_tags(self):
        tags_prefetch = Prefetch('tags', queryset=Tag.objects.fetch_with_posts_count())
        return self.prefetch_related('author', tags_prefetch)

    def fetch_with_author_and_tags_and_comments_count(self):
        return self.fetch_with_author_and_tags().fetch_with_comments_count()


class Post(models.Model):
    title = models.CharField('Заголовок', max_length=200)
    text = models.TextField('Текст')
    slug = models.SlugField('Название в виде url', max_length=200)
    image = models.ImageField('Картинка')
    published_at = models.DateTimeField('Дата и время публикации')

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        limit_choices_to={'is_staff': True})
    likes = models.ManyToManyField(
        User,
        related_name='liked_posts',
        verbose_name='Кто лайкнул',
        blank=True)
    tags = models.ManyToManyField(
        'Tag',
        related_name='posts',
        verbose_name='Теги')
    objects = PostQuerySet.as_manager()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post_detail', args={'slug': self.slug})

    class Meta:
        ordering = ['-published_at']
        verbose_name = 'пост'
        verbose_name_plural = 'посты'


class TagQuerySet(models.QuerySet):
    def popular(self, max_tags_count=5):
        return self.annotate(posts_count=Count('posts')).order_by('-posts_count')[:max_tags_count]

    def fetch_with_posts_count(self):
        return self.annotate(posts_count=Count('posts'))


class Tag(models.Model):
    title = models.CharField('Тег', max_length=20, unique=True)
    objects = TagQuerySet.as_manager()

    def __str__(self):
        return self.title

    def clean(self):
        self.title = self.title.lower()

    def get_absolute_url(self):
        return reverse('tag_filter', args={'tag_title': self.slug})

    class Meta:
        ordering = ['title']
        verbose_name = 'тег'
        verbose_name_plural = 'теги'


class Comment(models.Model):
    post = models.ForeignKey(
        'Post',
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Пост, к которому написан')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор')

    text = models.TextField('Текст комментария')
    published_at = models.DateTimeField('Дата и время публикации')

    def __str__(self):
        return f'{self.author.username} under {self.post.title}'

    class Meta:
        ordering = ['published_at']
        verbose_name = 'комментарий'
        verbose_name_plural = 'комментарии'
