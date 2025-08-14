# graphql_crm/schema.py

import graphene

class Query(graphene.ObjectType):
    hello = graphene.String()

    def resolve_hello(self, info):
        return "Hello, GraphQL!"

schema = graphene.Schema(query=Query)

# import graphene
# from crm.schema import Query as CRMQuery, Mutation as CRMMutation

# class Query(CRMQuery, graphene.ObjectType):
#     pass

# class Mutation(CRMMutation, graphene.ObjectType):
#     pass

# schema = graphene.Schema(query=Query, mutation=Mutation)
