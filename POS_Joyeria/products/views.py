from django.http import HttpResponse

def product_list(request):
    return HttpResponse("Lista de productos")
