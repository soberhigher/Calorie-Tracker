from django.contrib import admin

from tracker.models import (Eater,
                            Product,
                            MealEntry,
                            Meal)


@admin.register(Eater)
class EaterAdmin(admin.ModelAdmin):
    readonly_fields = ("today_summary", )


@admin.register(MealEntry)
class MealEntryAdmin(admin.ModelAdmin):
    readonly_fields = ("actual_calories", "actual_protein",
                       "actual_fat", "actual_carb", )


admin.site.register(Product)


admin.site.register(Meal)
