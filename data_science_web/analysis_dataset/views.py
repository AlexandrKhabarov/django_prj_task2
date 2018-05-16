from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.utils.timezone import now
from django.http import HttpResponse, Http404
from django.views import View
from django.views.generic import DetailView
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User, Permission
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
import os
import pandas as pd
from .forms import ConstantsForm, EditForm, SearchForm
from .models import Analysis, ResultAnalysis, ZipArchive
from .help_functions import get_all_abs_path, compress_zip
from .analysis_tools import filter, calculater, graphics


# Create your views here.

class UserPage(View):
    template_name = "analysis_dataset/user_page.html"

    def get(self, request):
        return render(request, self.template_name)


class AnalysisPage(View):
    template_name = "analysis_dataset/analysis.html"
    form_class = SearchForm

    def get(self, request):
        search_field = request.GET.get('search_field', None)
        if search_field:
            return render(request, self.template_name, context={
                "analysises": Analysis.objects.filter(name__contains=search_field),
                "form_search": self.form_class(),
            })
        return render(request, self.template_name, context={
            "analysises": Analysis.objects.filter(
                user=User.objects.get(username=request.user.username)),
            "form_search": self.form_class()
        })


class EditPage(View):
    template_name = "analysis_dataset/edit.html"

    def _form_and_content(self, request, name):
        query_set_analysis = dict(enumerate(Analysis.objects.all()))
        analysis_index = None

        for index, analysis in query_set_analysis.items():
            if analysis.name == name:
                analysis_index = index

        analysis = query_set_analysis.get(analysis_index, None)
        if analysis is not None:
            form = EditForm(
                initial={
                    "name": analysis.name,
                    "signal_speed": analysis.signal_speed,
                    "signal_direction": analysis.signal_direction,
                    "step_group": analysis.step_group,
                    "start_sector_direction": analysis.start_sector_direction,
                    "end_sector_direction": analysis.end_sector_direction,
                    "start_sector_speed": analysis.start_sector_speed,
                    "end_sector_speed": analysis.end_sector_speed
                })
        else:
            raise Http404("Object does not exist")

        return render(request, self.template_name, context={
            "form": form,
            "previous": query_set_analysis.get(
                analysis_index - 1,
                None
            ) if analysis_index is not None else analysis_index,
            "next": query_set_analysis.get(
                analysis_index + 1,
                None
            ) if analysis_index is not None else analysis_index,
            "name": name
        })

    def get(self, request, name):
        return self._form_and_content(request, name)

    def post(self, request, name):
        form = EditForm(data=request.POST)
        if form.is_valid():
            try:
                analysis = Analysis.objects.get(name=name)
                res = ResultAnalysis.objects.filter(analysis=analysis)
                if res:
                    zip_arc = ZipArchive.objects.filter(analysis=res[0])
                    if zip_arc:
                        zip_arc[0].delete()
                    res.delete()
                analysis.date_modification = now()
                analysis.start_sector_speed = form.cleaned_data["start_sector_speed"]
                analysis.start_sector_direction = form.cleaned_data["start_sector_direction"]
                analysis.end_sector_direction = form.cleaned_data["end_sector_direction"]
                analysis.end_sector_speed = form.cleaned_data["end_sector_speed"]
                analysis.step_group = form.cleaned_data["step_group"]
                analysis.signal_direction = form.cleaned_data["signal_direction"]
                analysis.signal_speed = form.cleaned_data["signal_speed"]
                analysis.save()

                request.user.user_permissions.add(
                    Permission.objects.get(name="Can Redirect Success")
                )

                return redirect(reverse("success-edit", kwargs={"name": analysis.name}))

            except ObjectDoesNotExist:
                raise Http404("Object Does not exist")


class SuccessEditPage(PermissionRequiredMixin, View):
    template_name = "analysis_dataset/success_page.html"
    permission_required = "auth.can_redirect_to_the_success_page"
    login_url = reverse_lazy("user")

    def get(self, request, name):
        request.user.user_permissions.remove(Permission.objects.get(name="Can Redirect Success"))
        return render(request, self.template_name, context={"analysis": name})


class DownloadZip(View):

    def get(self, _, name):
        try:
            analysis = Analysis.objects.get(name=name)
            result = ResultAnalysis.objects.get(analysis=analysis)
            archive = ZipArchive.objects.filter(
                name=name,
                analysis=result
            )
            if not archive:
                file_name = "{}_{}.zip".format(name, analysis.date_modification)
                base_name_dir = "zip_files"
                abs_path_dir = os.path.join(settings.MEDIA_ROOT, base_name_dir)
                if not os.path.exists(abs_path_dir):
                    os.mkdir(abs_path_dir)
                compress_zip(os.path.join(abs_path_dir, file_name), get_all_abs_path(result))
                archive = ZipArchive()
                archive.name = name
                archive.analysis = result
                archive.zip_file = os.path.join(base_name_dir, file_name)
                archive.save()

            response = HttpResponse(archive[0].zip_file if hasattr(archive, "__iter__") else archive.zip_file)
            response["Content-Disposition"] = 'attachment; filename="{}"'.format(
                archive[0].zip_file.name if hasattr(archive, "__iter__") else archive.zip_file.name
            )
            return response
        except ObjectDoesNotExist:
            raise Http404("Object does not exist")


class DeleteAnalysis(View):

    def get(self, _, name):
        analysis = Analysis.objects.filter(name=name)
        if analysis:
            res = ResultAnalysis.objects.filter(analysis=analysis[0])
            if res:
                zip_arc = ZipArchive.objects.filter(analysis=res[0])
                if zip_arc:
                    zip_arc[0].delete()
                res[0].delete()
            analysis[0].delete()
            return redirect(reverse('analysis'))
        raise Http404("Object does not exist")


class DetailsPage(DetailView):
    template_name = "analysis_dataset/details.html"
    model = Analysis
    slug_url_kwarg = "name"
    slug_field = "name"


class RegisterPage(View):
    form_class = UserCreationForm
    template_name = "analysis_dataset/register.html"

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, context={"form": form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            reg = form.clean()
            if reg["password1"] != reg["password2"]:
                return render(request, self.template_name, context={"form": form})
            if User.objects.filter(username=reg["username"]).exists():
                return render(request, self.template_name, context={"form": form})
            new_user = User.objects.create_user(
                username=reg['username'],
                password=reg['password1']
            )
            new_user.save()
            login(request, authenticate(
                username=reg['username'],
                password=reg['password1']
            ))
            return redirect(reverse("user"))

        return render(request, self.template_name, context={"form": form})


class SignInPage(View):
    form_class = AuthenticationForm
    template_name = "analysis_dataset/sign_in.html"

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, context={"form": form})

    def post(self, request):
        form = self.form_class(data=request.POST)
        if form.is_valid():
            login(request, authenticate(
                request,
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            ))
            return redirect(reverse("user"))
        return render(request, self.template_name, context={"form": form})


class LogOut(View):

    @staticmethod
    def get(request):
        logout(request)
        return redirect(reverse("user"))


class CreateAnalysis(View):
    form_class = ConstantsForm
    template_name = "analysis_dataset/create_analysis.html"

    def get(self, request):
        return render(request, self.template_name, context={"form": self.form_class()})

    def post(self, request):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            form = form.save(commit=False)
            form.user = User.objects.get(username=request.user.username)
            form.save()
            return redirect(reverse('details', kwargs={"name": form.name}))
        return redirect(reverse('create'))


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
