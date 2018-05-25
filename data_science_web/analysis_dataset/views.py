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
from django.conf import settings
import os
from .forms import ConstantsForm, EditForm, SearchForm
from .models import Analysis, ZipArchive
from .help_functions import get_all_abs_paths, compress_zip
from .analysis_tools import managers


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
            managers.ApplicationManager().go(
                form.instance,
                settings.MEDIA_ROOT,
            )
        except Exception as e:
            form.errors["error"] = e
            return super().form_invalid(form)
        try:
            zip_arc = ZipArchive.objects.get(analysis=form.instance)
            zip_arc.delete()
        except ObjectDoesNotExist:
            pass
        success_url = super().form_valid(form)
        return super(ModelFormMixin, self).form_valid(success_url)


class DownloadZip(DetailView):
    response_class = HttpResponse

    def get_object(self, queryset=None):
        try:
            try:
                analysis = Analysis.objects.get(name=self.kwargs["name"])
            except ObjectDoesNotExist:
                raise Http404("Analysis does not exist")
            archive = ZipArchive.objects.filter(
                name=self.kwargs["name"],
                analysis=analysis
            )
            if not archive:
                file_name = "{}_{}.zip".format(self.kwargs["name"], analysis.date_modification)
                base_name_dir = "zip_files"
                abs_path_dir = os.path.join(settings.MEDIA_ROOT, base_name_dir)
                if not os.path.exists(abs_path_dir):
                    os.mkdir(abs_path_dir)
                compress_zip(os.path.join(abs_path_dir, file_name), get_all_abs_paths(analysis.result_analysis))
                archive = ZipArchive()
                archive.name = self.kwargs["name"]
                archive.analysis = analysis
                archive.zip_file = os.path.join(base_name_dir, file_name)
                archive.save()
            return archive
        except ObjectDoesNotExist:
            raise Http404("Object does not exist")

    def render_to_response(self, context, **response_kwargs):
        archive = context.get("object")[0] if hasattr(context.get("object"), "__iter__") else context.get("object")
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

    def get(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object:
            zip_arc = ZipArchive.objects.filter(analysis=self.object)
            if zip_arc:
                zip_arc[0].delete()
            self.object.delete()
            success_url = self.get_success_url()
            return HttpResponseRedirect(success_url)
        raise Http404("Object does not exist")


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
        if User.objects.filter(username=reg_form["username"]).exists():
            super().form_invalid(form)
        new_user = User.objects.create_user(
            username=reg_form['username'],
            password=reg_form['password1']
        )
        new_user.save()
        login(self.request, authenticate(
            username=reg_form['username'],
            password=reg_form['password1']
        ))
        return super(RegisterPage, self).form_valid(form)


class SignInPage(FormView):
    form_class = AuthenticationForm
    template_name = "analysis_dataset/sign_in.html"
    success_url = reverse_lazy("analysis")

    def form_valid(self, form):
        login(self.request, authenticate(
            self.request,
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password']
        ))
        return super().form_valid(form)


class LogOut(View):

    @staticmethod
    def get(request):
        logout(request)
        return redirect(reverse("user"))


class CreateAnalysis(CreateView):
    form_class = ConstantsForm
    model = Analysis
    template_name = "analysis_dataset/create_analysis.html"
    success_url = reverse_lazy("analysis")

    def form_valid(self, form):
        analysis = form.save(commit=False)
        try:
            managers.ApplicationManager().go(
                analysis,
                settings.MEDIA_ROOT,
            )
        except Exception as e:
            form.errors["error"] = e
            return super().form_invalid(form)
        analysis.user = User.objects.get(username=self.request.user.username)
        analysis.result_analysis = os.path.join(settings.MEDIA_ROOT, analysis.name)
        analysis.save()
        return super().form_valid(form)
