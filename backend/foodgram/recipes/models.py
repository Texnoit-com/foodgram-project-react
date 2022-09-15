from django.contrib.auth import get_user_model
from django.core import validators
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

User = get_user_model()


class Ingredient(models.Model):
    '''Модель ингредиента'''
    name = models.CharField('Название ингредиента',
                            max_length=200)
    measurement_unit = models.CharField('Единица измерения',
                                        max_length=200)

    class Meta:
        ordering = ['name']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}.'


class Tag(models.Model):
    '''Модель Тагетирования'''
    name = models.CharField('Тег', max_length=60,
                            unique=True)
    color = models.CharField('Цвет (HEX)', max_length=7,
                             unique=True)
    slug = models.SlugField('Ссылка', max_length=100,
                            unique=True)

    class Meta:
        ordering = ['-id']
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return f'{self.name}'


class Recipe(models.Model):
    '''Модель рецепта'''
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='recipe',
                               verbose_name='Автор рецепта')
    name = models.CharField('Название', max_length=255)
    image = models.ImageField('Изображение', upload_to='static/recipe/',
                              blank=True, null=True)
    text = models.TextField('Описание')
    ingredients = models.ManyToManyField(Ingredient,
                                         through='RecipeIngredient',
                                         verbose_name='Ингредиенты',
                                         related_name='recipes',)
    tags = models.ManyToManyField(Tag, verbose_name='Тэги',
                                  related_name='recipes')
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления в минутах',
        validators=[validators.MinValueValidator(
            1, message='Мин. время приготовления 1 минута'), ])
    pub_date = models.DateTimeField('Дата публикации',
                                    auto_now_add=True)

    class Meta:
        ordering = ['-pub_date', ]
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return f'{self.name}'


class RecipeIngredient(models.Model):
    '''Модель состава рецепта'''
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='recipe')
    ingredient = models.ForeignKey(Ingredient,
                                   on_delete=models.CASCADE,
                                   related_name='ingredient')
    amount = models.PositiveSmallIntegerField(
        default=1,
        validators=(
            validators.MinValueValidator(
                1, message='Мин. количество ингридиентов 1'),),
        verbose_name='Количество',)

    class Meta:
        ordering = ['-id']
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'
        constraints = [models.UniqueConstraint(fields=['recipe', 'ingredient'],
                                               name='unique ingredient')]

    def __str__(self):
        return f'{self.ingredients.name}-{self.amount}'


class Subscribe(models.Model):
    '''Модель подписчика'''
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='follower',
                             verbose_name='Подписчик')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='following',
                               verbose_name='Автор')
    created = models.DateTimeField('Дата подписки', auto_now_add=True)

    class Meta:
        ordering = ['-id']
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [models.UniqueConstraint(fields=['user', 'author'],
                                               name='unique_subscription')]

    def __str__(self):
        return f'Подписчик{self.user} на автора {self.author}'


class FavoriteRecipe(models.Model):
    '''Модель избранных рецептов'''
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True,
                                related_name='favorite_recipe',
                                verbose_name='Подписчик')
    recipe = models.ManyToManyField(Recipe, related_name='favorite_recipe',
                                    verbose_name='Избранный рецепт')

    class Meta:
        ordering = ['-id']
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'

    def __str__(self):
        list_recipe = [item['name'] for item in self.recipe.values('name')]
        return f'{self.user}: список избраннных рецептов {list_recipe}'

    @receiver(post_save, sender=User)
    def create_favorite_recipe(sender, instance, created, **kwargs):
        if created:
            return FavoriteRecipe.objects.create(user=instance)


class ShoppingCart(models.Model):
    '''Модель корзины выбранных рецептов'''
    user = models.OneToOneField(User, on_delete=models.CASCADE,
                                related_name='shopping_cart', null=True,
                                verbose_name='Пользователь')
    recipe = models.ManyToManyField(Recipe, related_name='shopping_cart',
                                    verbose_name='Рецепт')

    class Meta:
        ordering = ['-id']
        verbose_name = 'Корзина'
        verbose_name_plural = 'В корзине'

    def __str__(self):
        list_recipe = [item['name'] for item in self.recipe.values('name')]
        return f'{self.user}: список рецептов в корзине: {list_recipe}'

    @receiver(post_save, sender=User)
    def create_shopping_cart(sender, instance, created, **kwargs):
        if created:
            return ShoppingCart.objects.create(user=instance)
