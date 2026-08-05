from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import generic
from tracker.models import Eater, Product, MealEntry, Meal



class IndexView(LoginRequiredMixin, generic.View):
    def get(self, request):
        total = request.user.today_summary()
        goals = request.user.daily_macros()
        calories_goal = request.user.daily_needs()
        calories_percent = round((total["calories"] / calories_goal) * 100)
        protein_percent = round((total["protein"] / goals["protein"]) * 100)
        fat_percent = round((total["fat"] / goals["fat"]) * 100)
        carb_percent = round((total["carb"] / goals["carb"]) * 100)

        return render(request,
                      "tracker/index.html",
                      {"eater": request.user, "total": total,
                       "goals": goals, "calories_goals": calories_goal,
                       "calories_percent": calories_percent, "protein_percent": protein_percent,
                       "fat_percent": fat_percent, "carb_percent": carb_percent})

class DuplicateView(LoginRequiredMixin, generic.View):
    def get(self, request, pk):
        old_meal = Meal.objects.filter(eater=request.user).get(pk=pk)
        entries = list(old_meal.infos.all())
        old_meal.pk = None
        old_meal.save()

        for entry in entries:
            entry.pk = None
            entry.meal = old_meal
            entry.save()
        return redirect("tracker:meal-list")


class EaterListView(LoginRequiredMixin, generic.ListView):
    model = Eater

    def get_queryset(self):
        queryset = super().get_queryset().order_by("id")
        query = self.request.GET.get("username")
        if query:
            filtered = queryset.filter(username__icontains=query)
            return filtered
        return queryset


class EaterCreateView(LoginRequiredMixin, generic.CreateView):
    model = Eater
    fields = ["username", "age", "sex", "lifestyle", "weight", "height"]
    success_url = reverse_lazy("tracker:eater-list")


class EaterUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Eater
    fields = ["age", "sex", "lifestyle", "weight", "height"]
    success_url = reverse_lazy("tracker:eater-list")


class EaterDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Eater
    success_url = reverse_lazy("tracker:eater-list")


class EaterDetailView(LoginRequiredMixin, generic.DetailView):
    model = Eater


class ProductListView(LoginRequiredMixin, generic.ListView):
    model = Product
    paginate_by = 8

    def get_queryset(self):
        queryset = super().get_queryset().order_by("name")
        query = self.request.GET.get("name")
        if query:
            filtered = queryset.filter(name__icontains=query)
            return filtered
        return queryset


class ProductCreateView(LoginRequiredMixin, generic.CreateView):
    model = Product
    fields = ["name", "portion", "weight_piece",
              "calories", "protein", "fat", "carb"]
    success_url = reverse_lazy("tracker:product-list")


class ProductUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Product
    fields = ["name", "portion", "weight_piece",
              "calories", "protein", "fat", "carb"]
    success_url = reverse_lazy("tracker:product-list")



class ProductDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Product
    success_url = reverse_lazy("tracker:product-list")


class ProductDetailView(LoginRequiredMixin, generic.DetailView):
    model = Product


class MealEntryListView(LoginRequiredMixin, generic.ListView):
    model = MealEntry
    template_name = "tracker/meal_entry_list.html"

    def get_queryset(self):
        return MealEntry.objects.filter(meal__eater=self.request.user)


class MealEntryCreateView(LoginRequiredMixin, generic.CreateView):
    model = MealEntry
    fields = ["product", "weight", "quantity"]
    template_name = "tracker/mealentry_form.html"

    def form_valid(self, form):
        form.instance.meal = Meal.objects.get(
            pk=self.kwargs["pk"],
            eater=self.request.user,)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("tracker:meal-entry-form", kwargs={"pk": self.kwargs["pk"]})


class MealEntryUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = MealEntry
    fields = ["weight", "quantity"]
    success_url = reverse_lazy("tracker:meal-entry-list")

    def get_queryset(self):
        return MealEntry.objects.filter(meal__eater=self.request.user)


class MealEntryDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = MealEntry
    success_url = reverse_lazy("tracker:meal-list")

    def get_queryset(self):
        return MealEntry.objects.filter(meal__eater=self.request.user)


class MealListView(LoginRequiredMixin, generic.ListView):
    model = Meal
    paginate_by = 4

    def get_queryset(self):
        queryset = super().get_queryset().filter(
            eater=self.request.user).order_by("-id")
        query = self.request.GET.get("ration")

        if query:
            queryset = queryset.filter(ration__icontains=query)
        return queryset


class MealCreateView(LoginRequiredMixin, generic.CreateView):
    model = Meal
    fields = ["ration"]

    def form_valid(self, form):
        form.instance.eater = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("tracker:meal-entry-form", kwargs={"pk": self.object.id})


class MealUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Meal
    fields = ["ration"]
    success_url = reverse_lazy("tracker:meal-list")

    def get_queryset(self):
        return Meal.objects.filter(eater=self.request.user)


class MealDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Meal
    success_url = reverse_lazy("tracker:meal-list")

    def get_queryset(self):
        return Meal.objects.filter(eater=self.request.user)

class MealDetailView(LoginRequiredMixin, generic.DetailView):
    model = Meal

    def get_queryset(self):
        return Meal.objects.filter(eater=self.request.user)
