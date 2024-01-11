# from django.http import HttpResponse
# from django.template import loader
# Não precisa por estar usando o render
from django.shortcuts import render

def index(request):
    return render(request, 'index.html')
# Mesma coisa que a de cima
    # template = loader.get_template('index.html')
    # return HttpResponse(template.render({}, request))

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')