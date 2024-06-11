"""
URL configuration for educhain project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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

from django.urls import path
from .views import validate_transaction, validate_block, get_transaction_in_pool
from .views import known_node_request, new_node_advertisement, get_blockchain, get_user_txids
from .views import get_transaction, reset



urlpatterns = [
    path('transaction/', validate_transaction, name="transaction"),
    path('block/', validate_block, name="block"),
    path('reset/', reset, name="reset"),
    path('new-node-advertisement/', new_node_advertisement, name="new_node_advertisement"),
    path('known-node-request/', known_node_request, name="known_node_request"),
    path('get-blockchain/', get_blockchain, name="get_blockchain"),
    path('get-pool/', get_transaction_in_pool, name="get_pool"),
    path('get-user-txids/<str:user_code>/', get_user_txids, name="get_user_txids"),
    path('get-transaction/<str:txid>/', get_transaction, name="get_transaction"),
]
