from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from django.views.generic import CreateView
from .forms import UserForm
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView as LoginBase
from django.http import response



class SignUpView(CreateView):
    template_name = 'auth/signup.html'
    form_class = UserForm
    success_url = reverse_lazy('dashboard')

    def post(self, request, *args, **kwargs):
        form = self.get_form_class()(request.POST)
        if form.is_valid():
            form.save()
            email = form.cleaned_data.get('email')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(email=email, password=raw_password)
            login(request, user)
            return redirect('dashboard')
        else:
            form = self.get_form_class()()
        return render(request, 'auth/signup.html', {'form': form})


class LoginView(LoginBase):
    template_name = 'auth/login.html'

    def get(self, request, *args, **kwargs):
        if not request.user.is_anonymous and request.user.is_authenticated:
            return response.HttpResponseRedirect(reverse_lazy('dashboard'))
        else:
            return super().get(request, *args, **kwargs)

    def get_redirect_url(self):
        return reverse_lazy('dashboard')

    def get_success_url(self):
        return reverse_lazy('dashboard')


