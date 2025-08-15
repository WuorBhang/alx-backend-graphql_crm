###########################
# graphql_crm/schema.py   #  (Task 0: hello + integrate CRM)
###########################

import graphene
from crm.schema import Query as CRMQuery, Mutation as CRMMutation


class Query(CRMQuery, graphene.ObjectType):
    # Task 0: Simple hello field
    hello = graphene.String(description="Simple sanity check field")

    def resolve_hello(root, info):
        return "Hello, GraphQL!"


class Mutation(CRMMutation, graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
