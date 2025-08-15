import graphene_django
import graphene
from graphene_django.views import GraphQLView
from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from graphene_django import DjangoObjectType
from graphene import ObjectType, Field, String, List
from crm.models import User, Booking
from crm.schema import Query as CRMQuery, Mutation as CRMMutation


class Query(ObjectType):
    """
    The root query for the GraphQL schema.
    """
    hello = String(default_value="Hello, GraphQL!")
    #all_users = List(DjangoObjectType, description="Query to fetch all users")
schema = graphene.Schema(query=Query)

'''
class UserType(DjangoObjectType):
    """
    GraphQL type for the User model.
    """
    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name")
        '''
class Query(CRMQuery, graphene.ObjectType):
    pass

class Mutation(CRMMutation, graphene.ObjectType):
    pass

schema = graphene.Schema(query=Query, mutation=Mutation)
