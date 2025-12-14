from django.urls import path
from .web_views import (
    pos_view,
    add_to_ticket,
    dec_ticket_item,
    remove_from_ticket,
    ajax_update_ticket,
    cobrar_sale,
    sale_success,
    client_search,
    client_select,
    client_quick,
    client_clear,
    sales_list,
)
app_name = "sales"
urlpatterns = [
    path("", pos_view, name="pos"),
    path("add/<int:product_id>/", add_to_ticket, name="add"),
    path("dec/<int:product_id>/", dec_ticket_item, name="dec"),
    path("remove/<int:product_id>/", remove_from_ticket, name="remove"),
    path("ajax/update/", ajax_update_ticket, name="ajax_update"),
    # Cliente
    path("client/search/", client_search, name="client_search"),
    path("client/select/<int:client_id>/", client_select, name="client_select"),
    path("client/quick/", client_quick, name="client_quick"),
    path("client/clear/", client_clear, name="client_clear"),
    # Cobro
    path("cobrar/", cobrar_sale, name="cobrar"),
    # Confirmación/detalle
    path("success/<int:sale_id>/", sale_success, name="success"),
    #Listado ventas
    path("ventas/", sales_list, name="ventas_list"),
    #Detalle desde listado (reusa sale_success.html)
    path("ventas/<int:sale_id>/", sale_success, name="detail"),
]
