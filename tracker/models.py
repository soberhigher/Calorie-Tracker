import datetime
from decimal import Decimal

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class Sex(models.TextChoices):
    male = "M", "Male"
    female = "F", "Female"


class Lifestyle(models.TextChoices):
    sedentary = "S", "Sedentary"
    light = "L", "Light"
    average = "A", "Average"


class Eater(AbstractUser):
    MIN_AGE = 1
    MAX_AGE = 110
    MIN_WEIGHT = 15
    MAX_WEIGHT = 150
    MIN_HEIGHT = 80
    MAX_HEIGHT = 250

    sex = models.CharField(choices=Sex.choices, default="M", max_length=6)
    age = models.IntegerField(default=23,
                              validators=[MinValueValidator(MIN_AGE),
                                          MaxValueValidator(MAX_AGE)])
    weight = models.FloatField(default=73,
                               validators=[MinValueValidator(MIN_WEIGHT),
                                           MaxValueValidator(MAX_WEIGHT)])
    height = models.FloatField(default=193,
                               validators=[MinValueValidator(MIN_HEIGHT),
                                           MaxValueValidator(MAX_HEIGHT)])
    lifestyle = models.CharField(default="L", choices=Lifestyle.choices,
                                 max_length=10)

    def __str__(self):
        return self.username

    def daily_needs(self):

        if self.sex == "M":
            bmr = 10 * self.weight + 6.25 * self.height - 5 * self.age + 5
        else:
            bmr = 10 * self.weight + 6.25 * self.height - 5 * self.age - 161

        if self.lifestyle == "S":
            total = bmr * 1.2
        elif self.lifestyle == "L":
            total = bmr * 1.375
        elif self.lifestyle == "A":
            total = bmr * 1.55
        return round(total)

    def daily_macros(self):
        total = self.daily_needs()

        return dict(protein=round(total * 0.30 / 4),
                    fat=round(total * 0.25 / 9),
                    carb=round(total * 0.45 / 4))

    def daily_summary(self, date):

        dates = MealEntry.objects.filter(
            meal__eater=self, meal__date__date=date).select_related("product")

        return dict(calories=sum(entry.actual_calories() for entry in dates),
                    protein=sum(entry.actual_protein() for entry in dates),
                    fat=sum(entry.actual_fat() for entry in dates),
                    carb=sum(entry.actual_carb() for entry in dates))

    def today_summary(self):
        return self.daily_summary(datetime.date.today())


class TypePortion(models.TextChoices):
    PIECE = "PC", "By Piece"
    WEIGHT = "WG", "By Weight"


class Product(models.Model):

    name = models.CharField(max_length=30)
    portion = models.CharField(choices=TypePortion.choices, max_length=20)
    weight_piece = models.PositiveSmallIntegerField(null=True, blank=True)
    calories = models.DecimalField(
        max_digits=6,
        decimal_places=1,
        validators=[
            MinValueValidator(Decimal("0")),
            MaxValueValidator(Decimal("5000"))]
    )
    protein = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        validators=[
            MinValueValidator(Decimal("0")),
            MaxValueValidator(Decimal("500"))]
    )
    fat = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        validators=[
            MinValueValidator(Decimal("0")),
            MaxValueValidator(Decimal("500"))])
    carb = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        validators=[
            MinValueValidator(Decimal("0")),
            MaxValueValidator(Decimal("500"))])

    def __str__(self):
        return self.name


class Ration(models.TextChoices):
    BREAKFAST = "BF", "Breakfast"
    LUNCH = "LU", "Lunch"
    DINNER = "DI", "Dinner"


class Meal(models.Model):
    ration = models.CharField(choices=Ration.choices, max_length=5)
    date = models.DateTimeField(auto_now_add=True)
    eater = models.ForeignKey(
        Eater,
        on_delete=models.CASCADE,
        related_name="meals"
    )

    def total_calories(self):
        return sum(entry.actual_calories() for entry in self.infos.all())

    def total_protein(self):
        return sum(entry.actual_protein() for entry in self.infos.all())

    def total_fat(self):
        return sum(entry.actual_fat() for entry in self.infos.all())

    def total_carbs(self):
        return sum(entry.actual_carb() for entry in self.infos.all())

    def __str__(self):
        return (f"{self.get_ration_display()} - "
                f"{self.date.strftime('%d.%m.%y %H:%M')} - "
                f"{self.total_calories()} calories")


class MealEntry(models.Model):

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="products"
    )
    weight = models.PositiveSmallIntegerField(null=True, blank=True)
    quantity = models.PositiveSmallIntegerField(null=True, blank=True)
    meal = models.ForeignKey(
        Meal,
        on_delete=models.CASCADE,
        related_name="infos"
    )

    def clean(self):
        super().clean()

        if self.product.portion == "PC" and self.quantity is None:
            raise ValidationError({
                "quantity": "Quantity is required for piece products."
            })
        if self.product.portion == "WG" and self.weight is None:
            raise ValidationError({
                "weight": "Weight is required for weight products."
            })

    def __str__(self):
        return f"{self.product} - {self.quantity or self.weight}"

    def get_weight_for_calc(self):
        if self.product.portion == "PC":
            if self.quantity is None:
                return 0
            return self.quantity * self.product.weight_piece

        return self.weight or 0

    def actual_calories(self):
        c = self.get_weight_for_calc()
        return self.product.calories / 100 * c

    def actual_protein(self):
        p = self.get_weight_for_calc()
        return self.product.protein / 100 * p

    def actual_fat(self):
        f = self.get_weight_for_calc()
        return self.product.fat / 100 * f

    def actual_carb(self):
        c = self.get_weight_for_calc()
        return self.product.carb / 100 * c
