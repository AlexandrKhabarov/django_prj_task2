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
import pandas as pd
from .forms import ConstantsForm, EditForm, SearchForm
from .models import Analysis, ResultAnalysis, ZipArchive
from .help_functions import get_all_abs_path, compress_zip
from .analysis_tools import filter, calculater, graphics


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


class CalculateAnalysis(View):
    def get(self, _, name):
        try:
            analysis = Analysis.objects.get(name=name)
            result_analysis = ResultAnalysis()
            try:
                df = pd.read_csv(analysis.data_set.path, engine="python", sep=None, index_col="Timestamp")
            except ValueError:
                return redirect(reverse("analysis"))
            df = filter.FilterDataFrame.del_duplicate(df)
            df = filter.FilterDataFrame.del_empty_rows(df)
            df = filter.FilterDataFrame.filter_by_direct(
                df,
                "WD_{}".format(analysis.signal_direction),
                analysis.start_sector_direction,
                analysis.end_sector_direction
            )
            df = filter.FilterDataFrame.filter_by_speed(
                df,
                "WS_{}".format(analysis.signal_speed),
                analysis.start_sector_speed,
                analysis.end_sector_speed
            )

            density_calculater = calculater.DensityCalcDataFrame()

            density_dir = "with_density"
            abs_density_dir = os.path.join(settings.MEDIA_ROOT, density_dir)
            density_file = "{}.csv".format(analysis.name)
            df = density_calculater.calc_density(df)
            if not os.path.exists(abs_density_dir):
                os.mkdir(abs_density_dir)
            abs_path_file = os.path.join(abs_density_dir, density_file)
            df.to_csv(abs_path_file)
            result_analysis.with_density = os.path.join(density_dir, density_file)

            group_density_dir = "group_data_frame"
            abs_group_density_dir = os.path.join(settings.MEDIA_ROOT, group_density_dir)
            group_density_file = "{}.csv".format(analysis.name)

            group_data_frame = filter.FilterDataFrame.group_data_frame(
                df,
                analysis.start_sector_direction,
                analysis.end_sector_direction,
                analysis.step_group,
                "WD_{}".format(analysis.signal_direction)
            ).mean()
            if not os.path.exists(abs_group_density_dir):
                os.mkdir(abs_group_density_dir)

            abs_path_file = os.path.join(abs_group_density_dir, group_density_file)
            group_data_frame.to_csv(abs_path_file)
            result_analysis.group_data_frame = os.path.join(group_density_dir, group_density_file)

            graphic_imager = graphics.GraphManager(settings.MEDIA_ROOT)

            density_graph_dir = "density_graph"
            basename_density_graph = os.path.join(density_graph_dir, "{}.png".format(analysis.name))
            if not os.path.exists(os.path.join(settings.MEDIA_ROOT, density_graph_dir)):
                os.mkdir(os.path.join(settings.MEDIA_ROOT, density_graph_dir))
            try:
                graphic_imager.density_graph(
                    df,
                    basename_density_graph
                )
            except Exception:
                pass
            else:
                result_analysis.density_graph = basename_density_graph

            hist_graph = "hist_graph"
            base_name_hist_graph = os.path.join(hist_graph, "{}.png".format(analysis.name))
            if not os.path.exists(os.path.join(settings.MEDIA_ROOT, hist_graph)):
                os.mkdir(os.path.join(settings.MEDIA_ROOT, hist_graph))

            try:
                graphic_imager.hist_graph(
                    df,
                    "WS_{}".format(analysis.signal_speed),
                    base_name_hist_graph
                )
            except Exception:
                pass
            else:
                result_analysis.hist_graph = base_name_hist_graph

            dot_graphs = "dot_graphs"
            base_name_dot_graph = os.path.join(dot_graphs, "{}.png".format(analysis.name))
            if not os.path.exists(os.path.join(settings.MEDIA_ROOT, dot_graphs)):
                os.mkdir(os.path.join(settings.MEDIA_ROOT, dot_graphs))

            try:
                graphic_imager.dot_graph(
                    "WD_{}".format(analysis.signal_direction),
                    "WS_{}".format(analysis.signal_speed),
                    df,
                    group_data_frame,
                    base_name_dot_graph
                )
            except Exception:
                pass
            else:
                result_analysis.dot_graph = base_name_dot_graph

            rose_graph = "rose_graph"
            base_name_rose_graph = os.path.join(rose_graph, "{}.png".format(analysis.name))
            if not os.path.exists(os.path.join(settings.MEDIA_ROOT, rose_graph)):
                os.mkdir(os.path.join(settings.MEDIA_ROOT, rose_graph))

            try:
                graphic_imager.rose_graph(
                    df,
                    "WD_{}".format(analysis.signal_direction),
                    analysis.step_group,
                    base_name_rose_graph
                )
            except Exception:
                pass
            else:
                result_analysis.rose_graph = base_name_rose_graph

            result_analysis.analysis = analysis
            result_analysis.save()

            return redirect(reverse('analysis'))

        except ObjectDoesNotExist:
            raise Http404("object does not exist")
