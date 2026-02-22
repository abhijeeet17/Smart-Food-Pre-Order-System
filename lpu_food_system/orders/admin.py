from django.contrib import admin
from .models import (
    StudentProfile, FoodStall, FoodItem,
    BreakTimeSlot, Order, OrderItem, DemandRecord
)


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'registration_number', 'department', 'semester']
    search_fields = ['user__username', 'registration_number']


@admin.register(FoodStall)
class FoodStallAdmin(admin.ModelAdmin):
    list_display = ['name', 'location', 'is_open']
    list_editable = ['is_open']


@admin.register(FoodItem)
class FoodItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'stall', 'price', 'category', 'is_available']
    list_editable = ['price', 'is_available']
    list_filter = ['category', 'stall', 'is_available']
    search_fields = ['name']


@admin.register(BreakTimeSlot)
class BreakTimeSlotAdmin(admin.ModelAdmin):
    list_display = ['slot_time', 'max_capacity']


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['price_at_order']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'student', 'stall', 'time_slot', 'status', 'total_amount', 'order_date']
    list_editable = ['status']
    list_filter = ['status', 'order_date', 'stall']
    inlines = [OrderItemInline]


@admin.register(DemandRecord)
class DemandRecordAdmin(admin.ModelAdmin):
    list_display = ['food_item', 'date', 'time_slot', 'quantity_ordered', 'predicted_demand']
    list_filter = ['date', 'food_item']
