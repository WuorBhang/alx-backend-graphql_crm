"""alx_backend_graphql_crm URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from graphene_django.views import GraphQLView
from django.views.decorators.csrf import csrf_exempt

# Import the schema instance directly so GraphQLView doesn't need to resolve it each time
from alx_backend_graphql_crm.schema import schema

urlpatterns = [
<<<<<<<< HEAD:alx_backend_graphql_crm/alx_backend_graphql_crm/urls.py
    path('admin/', admin.site.urls),
    path("graphql", csrf_exempt(GraphQLView.as_view(graphiql=True))),
========
    path("admin/", admin.site.urls),
    path("graphql", csrf_exempt(GraphQLView.as_view(graphiql=True, schema=schema))),
>>>>>>>> 3d5371b352cc2b853c543c3756ae8dd29199bce3:alx_backend_graphql_crm/urls.py
]
