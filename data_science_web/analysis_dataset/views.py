from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.views import View
from django.views.generic import DetailView, ListView, CreateView, UpdateView, DeleteView, TemplateView, FormView, \
    RedirectView
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
import os
from .forms import ConstantsForm, EditForm, SearchForm
from .models import Analysis, ResultAnalysis, ZipArchive
from .help_functions import get_all_abs_path, compress_zip
from .analysis_tools import managers


# Create your views here.

class UserPage(TemplateView):
    template_name = "analysis_dataset/user_page.html"


class AnalysisPage(ListView):
    template_name = "analysis_dataset/analysis.html"
    form_class = SearchForm
    model = Analysis
    paginate_by = 10
    context_object_name = "analysises"

    def get_queryset(self):
        return super(AnalysisPage, self).get_queryset().filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        queryset = self.get_queryset()
        if self.request.GET.get('search_field', None):
            queryset = (
                queryset.filter(
                    name__contains=self.request.GET.get('search_field'),
                    user=self.request.user
                )
            )
        return super().get_context_data(object_list=queryset, form_search=self.form_class())


class EditPage(UpdateView):
    model = Analysis
    form_class = EditForm
    slug_field = "name"
    slug_url_kwarg = "name"
    template_name = "analysis_dataset/edit.html"
    success_url = reverse_lazy("analysis")

    def get_object(self, queryset=None):
        analysis = super().get_object()
        try:
            res = ResultAnalysis.objects.get(analysis=analysis)
            try:
                zip_arc = ZipArchive.objects.get(analysis=res)
                zip_arc.delete()
            except ObjectDoesNotExist:
                pass
            res.delete()
        except ObjectDoesNotExist:
            pass
        return analysis


class DownloadZip(DetailView):
    response_class = HttpResponse

    def get_object(self, queryset=None):
        try:
            analysis = Analysis.objects.get(name=self.kwargs["name"])
            try:
                result = ResultAnalysis.objects.get(analysis=analysis)
            except ObjectDoesNotExist:
                return analysis.name
            archive = ZipArchive.objects.filter(
                name=self.kwargs["name"],
                analysis=result
            )
            if not archive:
                file_name = "{}_{}.zip".format(self.kwargs["name"], analysis.date_modification)
                base_name_dir = "zip_files"
                abs_path_dir = os.path.join(settings.MEDIA_ROOT, base_name_dir)
                if not os.path.exists(abs_path_dir):
                    os.mkdir(abs_path_dir)
                compress_zip(os.path.join(abs_path_dir, file_name), get_all_abs_path(result))
                archive = ZipArchive()
                archive.name = self.kwargs["name"]
                archive.analysis = result
                archive.zip_file = os.path.join(base_name_dir, file_name)
                archive.save()
            return archive
        except ObjectDoesNotExist:
            raise Http404("Object does not exist")

    def render_to_response(self, context, **response_kwargs):
        archive = context.get("object")[0] if hasattr(context.get("object"), "__iter__") else context.get("object")
        if isinstance(archive, ZipArchive):
            response = self.response_class(archive)
            response["Content-Disposition"] = 'attachment; filename="{}"'.format(archive.zip_file.name)
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
        return self.model.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object:
            res = ResultAnalysis.objects.filter(analysis=self.object)
            if res:
                zip_arc = ZipArchive.objects.filter(analysis=res[0])
                if zip_arc:
                    zip_arc[0].delete()
                res[0].delete()
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
        analysis.user = User.objects.get(username=self.request.user.username)
        return super().form_valid(form)


class CalculateAnalysis(View):# Use calculate chunck in create and update forms (delete CalculateAnalysis view)
    def get(self, _, name):
        try:
            analysis = Analysis.objects.get(name=name)
            result_analysis = ResultAnalysis()

            managers.ApplicationManager().go(
                analysis,
                result_analysis,
                settings.MEDIA_ROOT,
                "with_density",
                "group_data_frame",
                "density_graph",
                "hist_graph",
                "dot_graphs",
                "rose_graph"
            )

            result_analysis.analysis = analysis
            result_analysis.save()

            return redirect(reverse('analysis'))

        except ObjectDoesNotExist:
            raise Http404("object does not exist")
