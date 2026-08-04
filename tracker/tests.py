from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from tracker.models import (Product,
                            Eater,
                            MealEntry,
                            Meal)


class AdminPanelTest(TestCase):
    def setUp(self) -> None:
        self.admin_user = get_user_model().objects.create_superuser(
            username="admin", password="admin123"
        )
        self.client.force_login(self.admin_user)
        self.eater = Eater.objects.create(
            username="Angel", age=25, weight=70, height=175
        )
        self.product = Product.objects.create(
            name="banana", portion="WG", calories=150, protein=55,
            fat=15, carb=5
        )
        self.meal = Meal.objects.create(
            ration="BF", eater=self.eater
        )
        self.meal_entry = MealEntry.objects.create(
            product=self.product, weight=110, meal=self.meal
        )

    def test_eater_change_page(self):
        url = reverse("admin:tracker_eater_change", args=[self.eater.id])
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)

    def test_meal_entry_change_page(self):
        url = reverse("admin:tracker_mealentry_change", args=[self.meal_entry.id])
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)


class MealEntryModelTest(TestCase):
    def test_get_weight_for_calc_piece(self):
        product = Product.objects.create(
            name="Egg", portion="PC", weight_piece=50,
            calories=144, protein=13, fat=10, carb=0
        )
        eater = Eater.objects.create(
            username="test", age=25, weight=70, height=175
        )
        meal = Meal.objects.create(
            ration="BF", eater=eater
        )
        entry = MealEntry.objects.create(
            product=product, quantity=3, meal=meal
        )
        self.assertEqual(entry.get_weight_for_calc(), 150)

    def test_get_weight_for_calc_weight(self):
        product = Product.objects.create(
            name="Bread", portion="WG",
            calories=223, protein=12, fat=0, carb=39
        )
        eater = Eater.objects.create(
            username="test2", age=25, weight=70, height=175
        )
        meal = Meal.objects.create(
            ration="BF", eater=eater
        )
        entry = MealEntry.objects.create(
            product=product, weight=100, meal=meal
        )
        self.assertEqual(entry.get_weight_for_calc(), 100)


class ProductListViewTest(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            username="user", password="user123"
        )
        self.client.force_login(self.user)

    def test_product_search_and_pagination(self):
        product = Product.objects.create(
            name="Egg", portion="PC", weight_piece=50,
            calories=144, protein=13, fat=10, carb=0
        )
        anotherproduct = Product.objects.create(
            name="Apple", portion="PC", weight_piece=50,
            calories=144, protein=13, fat=10, carb=0
        )
        url = reverse("tracker:product-list")
        res = self.client.get(url, {"name": "Egg"})
        self.assertContains(res, "Egg")
        self.assertNotContains(res, "Apple")


class EaterModelTest(TestCase):
    def test_daily_needs(self):
        eater = Eater.objects.create(
            sex="M", age=23, weight=73, height=192,
            lifestyle="L"
        )
        self.assertEqual(eater.daily_needs(), 2502)
        self.assertEqual(eater.daily_macros()["protein"], 188)
        self.assertEqual(eater.daily_macros()["fat"], 70)
        self.assertEqual(eater.daily_macros()["carb"], 281)
