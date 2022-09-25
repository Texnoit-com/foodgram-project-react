from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from drf_base64.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag

from .users import GetIsSubscribedMixin

User = get_user_model()

ERR_INGREDIENT = 'Ингредиент уже существует'
ERR_INGREDIENT_TAG = 'Нужен хотя бы один тэг для рецепта!'
ERR_MIN_INGREDIENT = 'Укажите минимум один ингедиент'
ERR_TAG = 'Данный тег не существует'
ERR_TIME_COOKING = 'Время приготовления минимум одна минута'
ERR_MIN_COOKING = 'Укажите минимум один ингредиент в рецепте!'


class TagSerializer(serializers.ModelSerializer):
    '''Получение тега'''
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug',)


class IngredientSerializer(serializers.ModelSerializer):
    '''Получение ингредиента'''
    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeIngredientSerializer(serializers.ModelSerializer):
    '''Получение ингредиентов рецепта'''
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeUserSerializer(GetIsSubscribedMixin, serializers.ModelSerializer):
    '''Получение рецепта пользователя'''
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed')


class IngredientsEditSerializer(serializers.ModelSerializer):
    '''Изменение ингридиента'''
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = Ingredient
        fields = ('id', 'amount')


class RecipeWriteSerializer(serializers.ModelSerializer):
    '''Запись рецепта'''
    image = Base64ImageField(max_length=None, use_url=True)
    tags = serializers.PrimaryKeyRelatedField(many=True,
                                              queryset=Tag.objects.all())
    ingredients = IngredientsEditSerializer(many=True)

    class Meta:
        model = Recipe
        fields = '__all__'
        read_only_fields = ('author',)

    def validate(self, data):
        '''Проверка записи ингредиента'''
        ingredients = data['ingredients']
        ingredient_list = []

        for items in ingredients:
            ingredient = get_object_or_404(Ingredient, id=items['id'])
            if ingredient in ingredient_list:
                raise serializers.ValidationError(ERR_INGREDIENT)
            ingredient_list.append(ingredient)

        tags = data['tags']

        if not tags:
            raise serializers.ValidationError(ERR_INGREDIENT_TAG)
        for tag_name in tags:
            if not Tag.objects.filter(name=tag_name).exists():
                raise serializers.ValidationError(ERR_TAG)
        return data

    def validate_cooking_time(self, cooking_time):
        '''Проверка времени приготовления'''
        if int(cooking_time) < 1:
            raise serializers.ValidationError(ERR_TIME_COOKING)
        return cooking_time

    def validate_ingredients(self, ingredients):
        '''Проверка указания ингредиентов'''
        if not ingredients:
            raise serializers.ValidationError(ERR_MIN_COOKING)
        for ingredient in ingredients:
            if int(ingredient.get('amount')) < 1:
                raise serializers.ValidationError(ERR_MIN_INGREDIENT)
        return ingredients

    def create_ingredients(self, ingredients, recipe):
        '''Создание дополнительных игредиентов'''
        for ingredient in ingredients:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient_id=ingredient.get('id'),
                amount=ingredient.get('amount'), )

    def create(self, validated_data):
        '''Создание рецепта'''
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(ingredients, recipe)

        return recipe

    def update(self, instance, validated_data):
        '''Обновление даннных о рецепте'''
        if 'ingredients' in validated_data:
            ingredients = validated_data.pop('ingredients')
            instance.ingredients.clear()
            self.create_ingredients(ingredients, instance)

        if 'tags' in validated_data:
            instance.tags.set(validated_data.pop('tags'))

        return super().update(instance, validated_data)

    def to_representation(self, instance):
        '''Вывод рецепта'''
        return RecipeReadSerializer(
            instance,
            context={'request': self.context.get('request')}).data


class RecipeReadSerializer(serializers.ModelSerializer):
    '''Вывод данных рецепта'''
    image = Base64ImageField()
    tags = TagSerializer(many=True, read_only=True)
    author = RecipeUserSerializer(read_only=True,
                                  default=serializers.CurrentUserDefault())
    ingredients = RecipeIngredientSerializer(many=True,
                                             required=True,
                                             source='recipe')
    is_favorited = serializers.BooleanField(read_only=True)
    is_in_shopping_cart = serializers.BooleanField(read_only=True)

    class Meta:
        model = Recipe
        fields = '__all__'
