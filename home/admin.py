from django.contrib import admin
from .models import LoanApplication, Testimonial

# Register your models here.
class LoanApplicationAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'loan_reason', 'approved', 'created_at')
    list_filter = ('approved',)
    actions = ['approve_loans', 'reject_loans']

    def approve_loans(self, request, queryset):
        queryset.update(approved=True)

    def reject_loans(self, request, queryset):
        queryset.update(approved=False)

    approve_loans.short_description = "Approve selected loans"
    reject_loans.short_description = "Reject selected loans"

admin.site.register(LoanApplication, LoanApplicationAdmin)

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('user', 'content', 'created_at', 'approved')
    list_filter = ('approved',)
    search_fields = ('user__username', 'content')