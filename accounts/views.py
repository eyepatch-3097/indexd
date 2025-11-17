# accounts/views.py
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy

from .forms import SignupForm, LoginForm


def signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(
                request,
                user,
                backend="accounts.backends.EmailOrUsernameModelBackend",
            )
            return redirect("accounts:profile")
    else:
        form = SignupForm()

    return render(request, "accounts/signup.html", {"form": form})


class LoginViewCustom(LoginView):
    authentication_form = LoginForm
    template_name = "accounts/login.html"

    def get_success_url(self):
        return self.get_redirect_url() or reverse_lazy("accounts:profile")


@login_required
def profile(request):
    return render(request, "accounts/profile.html")
