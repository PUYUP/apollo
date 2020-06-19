from django.views import View
from django.shortcuts import render


class HomeView(View):
    template_name = 'global/home.html'
    context = dict()

    def get(self, request):
        return render(request, self.template_name, self.context)
