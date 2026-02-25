from .models import Category

def header_context(request):
    return {'catz': Category.objects.all()}