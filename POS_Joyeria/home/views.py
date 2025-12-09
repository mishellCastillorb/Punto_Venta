from django.http import HttpResponse

def inicio(request):
    return HttpResponse('Iniciando')