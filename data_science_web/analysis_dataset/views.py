from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.views import View
from django.views.generic import DetailView, ListView, CreateView, UpdateView, DeleteView, TemplateView, FormView
from django.views.generic.edit import ModelFormMixin
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
import os
from .forms import CreateAnalysisForm, EditForm, SearchForm
from .models import Analysis, ZipArchive


# Create your views here.

class UserPage(TemplateView):
    template_name = "analysis_dataset/user_page.html"


class AnalysisPage(ListView):
    template_name = "analysis_dataset/analysis.html"
    form_class = SearchForm
    model = Analysis
    paginate_by = 1
    context_object_name = "analysises"

    def get_queryset(self):
        queryset = super().get_queryset().filter(user=self.request.user)
        if self.request.GET.get('search_field', None):
            queryset = queryset.filter(
                name__contains=self.request.GET.get('search_field')
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context["form_search"] = self.form_class()
        return context


class EditPage(UpdateView):
    model = Analysis
    form_class = EditForm
    slug_field = "name"
    slug_url_kwarg = "name"
    template_name = "analysis_dataset/edit.html"
    success_url = reverse_lazy("analysis")

    def form_valid(self, form):
        try:
            success_url = super().form_valid(form)
        except Exception as e:
            form.errors["error"] = e
            return super().form_invalid(form)
        try:
            zip_arc = ZipArchive.objects.get(analysis=form.instance)
            zip_arc.delete()
        except ObjectDoesNotExist:
            pass
        return super(ModelFormMixin, self).form_valid(success_url)


class DownloadZip(DetailView):
    response_class = HttpResponse

    def get_object(self, queryset=None):
        try:
            try:
                analysis = Analysis.objects.get(name=self.kwargs["name"])
            except ObjectDoesNotExist:
                raise Http404("Analysis does not exist")
            try:
                archive = ZipArchive.objects.get(name=self.kwargs["name"], analysis=analysis)
            except ObjectDoesNotExist:
                archive = analysis.create_archive()
            return archive
        except ObjectDoesNotExist:
            raise Http404("Object does not exist")

    def render_to_response(self, context, **response_kwargs):  # можно использовать isinstance
        archive = context.get("object")
        if isinstance(archive, ZipArchive):
            response = self.response_class(archive.zip_file.read(), content_type='application/zip')
            response["Content-Disposition"] = 'attachment; filename="{}"'.format(
                os.path.basename(archive.zip_file.name))
            return response
        return HttpResponseRedirect(reverse("analysis") + "?warning=" + context.get("object"))


class DeleteAnalysis(DeleteView):
    model = Analysis
    success_url = reverse_lazy("analysis")
    slug_field = "name"
    slug_url_kwarg = "name"
    object = None

    def post(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        zip_arc = ZipArchive.objects.filter(analysis=self.object)
        if zip_arc:
            zip_arc[0].delete()
        self.object.delete()
        success_url = self.get_success_url()
        return HttpResponseRedirect(success_url)


class DetailsPage(DetailView):
    template_name = "analysis_dataset/details.html"
    model = Analysis
    slug_url_kwarg = "name"
    slug_field = "name"


class RegisterPage(FormView):
    form_class = UserCreationForm
    template_name = "analysis_dataset/register.html"
    success_url = reverse_lazy("analysis")

    def form_valid(self, form):
        reg_form = form.clean()
        username = reg_form["username"]
        password1 = reg_form["password1"]
        if User.objects.filter(username=username).exists():
            super().form_invalid(form)
        new_user = User.objects.create_user(username=username, password=password1)
        new_user.save()
        login(self.request, authenticate(username=username, password=password1))
        return super(RegisterPage, self).form_valid(form)


class SignInPage(FormView):
    form_class = AuthenticationForm
    template_name = "analysis_dataset/sign_in.html"
    success_url = reverse_lazy("analysis")

    def form_valid(self, form):
        login(self.request, authenticate(self.request, **form.cleaned_data))
        return super().form_valid(form)


class LogOut(View):

    # @staticmethod
    # def get(request):
    #     logout(request)
    #     return redirect(reverse("user"))
    @staticmethod
    def post(request):
        logout(request)
        return redirect(reverse("sign-in"))


class CreateAnalysis(CreateView):
    form_class = CreateAnalysisForm
    model = Analysis
    template_name = "analysis_dataset/create_analysis.html"
    success_url = reverse_lazy("analysis")
    object = None

    def form_valid(self, form):
        form.instance.user = User.objects.get(username=self.request.user.username)
        try:
            response = super().form_valid(form)
        except Exception as e:
            form.errors["error"] = e
            return super().form_invalid(form)
        return response


