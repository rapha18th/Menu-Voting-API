from rest_framework import serializers

class RestaurantSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()

class MenuSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    description = serializers.CharField()
    created_at = serializers.CharField()
    restaurant = RestaurantSerializer()