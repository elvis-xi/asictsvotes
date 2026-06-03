from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Student, Election, Candidate, Vote

class StudentAdmin(UserAdmin):
    list_display = ('matric_number', 'full_name', 'email', 'is_active', 'is_staff')
    search_fields = ('matric_number', 'full_name')
    ordering = ('matric_number',)
    
    fieldsets = (
        (None, {'fields': ('matric_number', 'password')}),
        ('Personal info', {'fields': ('full_name', 'email', 'department')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('matric_number', 'full_name', 'password1', 'password2'),
        }),
    )

class CandidateInline(admin.TabularInline):
    model = Candidate
    extra = 1

class ElectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_time', 'end_time', 'status', 'total_votes')
    list_filter = ('is_active', 'start_time')
    search_fields = ('title',)
    inlines = [CandidateInline]
    
    def status(self, obj):
        return obj.status
    status.short_description = 'Status'

class VoteAdmin(admin.ModelAdmin):
    list_display = ('user', 'election', 'candidate', 'voted_at')
    list_filter = ('election', 'voted_at')
    search_fields = ('user__matric_number', 'candidate__name')
    readonly_fields = ('vote_hash',)

admin.site.register(Student, StudentAdmin)
admin.site.register(Election, ElectionAdmin)
admin.site.register(Candidate)
admin.site.register(Vote, VoteAdmin)