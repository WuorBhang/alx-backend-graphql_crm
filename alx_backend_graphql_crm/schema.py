# alx_backend_graphql_crm/schema.py

"""
Main GraphQL schema for the alx_backend_graphql_crm project.
"""

import graphene

from crm.schema import Mutation as CrmMutation
from crm.schema import Query as CrmQuery


class Query(CrmQuery, graphene.ObjectType):
    """
    Root GraphQL Query class.

    This class inherits from all app-level Query classes to combine
    them into a single root query for the entire project.
    """

    pass


class Mutation(CrmMutation, graphene.ObjectType):
    """
    Root GraphQL Mutation class.

    This class inherits from all app-level Mutation classes to combine
    them into a single root mutation for the entire project.
    """

    pass


# Create the main schema object
schema = graphene.Schema(query=Query, mutation=Mutation)
