import django.contrib.auth.password_validation as validators
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from recipes.models import Recipe, Subscribe

User = get_user_model()
ERR_MSG_USER = 'Не удается войти в систему.'


class TokenSerializer(serializers.Serializer):
    '''Проверка токена'''
    email = serializers.CharField(label='Email', write_only=True)
    password = serializers.CharField(label='Пароль',
                                     style={'input_type': 'password'},
                                     trim_whitespace=False, write_only=True)
    token = serializers.CharField(label='Токен', read_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'),
                                email=email,
                                password=password)
            if not user:
                raise serializers.ValidationError(ERR_MSG_USER,
                                                  code='authorization')
        else:
            msg = 'Укажите электронную почту и пароль.'
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs


class UserCreateSerializer(serializers.ModelSerializer):
    '''Создание пользователя'''
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name',
                  'last_name', 'password',)

    def validate_password(self, password):
        validators.validate_password(password)
        return password


class GetIsSubscribedMixin:
    '''Получить Подписку пользователя'''
    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if not user.is_authenticated:
            return False
        return user.follower.filter(author=obj).exists()


class UserListSerializer(GetIsSubscribedMixin, serializers.ModelSerializer):
    '''Список пользователей'''
    is_subscribed = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed')


class UserPasswordSerializer(serializers.Serializer):
    '''Изменение пароля'''
    new_password = serializers.CharField(label='Новый пароль')
    current_password = serializers.CharField(label='Текущий пароль')

    def validate_current_password(self, current_password):
        user = self.context['request'].user

        if not authenticate(username=user.email, password=current_password):
            raise serializers.ValidationError(ERR_MSG_USER,
                                              code='authorization')
        return current_password

    def validate_new_password(self, new_password):
        validators.validate_password(new_password)
        return new_password

    def create(self, validated_data):
        user = self.context['request'].user
        password = make_password(validated_data.get('new_password'))
        user.password = password
        user.save()
        return validated_data


class SubscribeRecipeSerializer(serializers.ModelSerializer):
    '''Подписка на рецепты'''
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscribeSerializer(serializers.ModelSerializer):
    '''Подписка на автора'''
    id = serializers.IntegerField(source='author.id')
    email = serializers.EmailField(source='author.email')
    username = serializers.CharField(source='author.username')
    first_name = serializers.CharField(source='author.first_name')
    last_name = serializers.CharField(source='author.last_name')
    recipes = serializers.SerializerMethodField()
    is_subscribed = serializers.BooleanField(read_only=True)
    recipes_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Subscribe
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count',)

    def get_recipes(self, obj):
        '''Получить рецепты автора'''
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = (
            obj.author.recipe.all()[:int(limit)] if limit
            else obj.author.recipe.all())

        return SubscribeRecipeSerializer(recipes, many=True).data
