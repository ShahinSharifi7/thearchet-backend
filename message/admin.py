from django.contrib import admin
from .models import Message


class MessageAdmin(admin.ModelAdmin):
    # Fields to be displayed in the list view
    list_display = ('sender', 'receiver', 'subject', 'created_at', 'seen', 'deleted_by_sender', 'deleted_by_receiver')

    # Add search functionality
    search_fields = ('sender__username', 'receiver__username', 'subject', 'text')

    # Filter options for the admin
    list_filter = ('seen', 'deleted_by_sender', 'deleted_by_receiver')

    # Make created_at and sender/receiver fields sortable
    ordering = ('-created_at',)

    # Remove fields from here, use fieldsets instead
    # fields = ('sender', 'receiver', 'parent', 'subject', 'text', 'seen', 'deleted_by_sender', 'deleted_by_receiver')

    # Add additional options for better organization of fields
    fieldsets = (
        (None, {
            'fields': ('sender', 'receiver', 'parent')
        }),
        ('Message Content', {
            'fields': ('subject', 'text')
        }),
        ('Visibility', {
            'fields': ('seen', 'deleted_by_sender', 'deleted_by_receiver')
        }),
        ('Meta', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


# Register the Message model with the custom admin class
admin.site.register(Message, MessageAdmin)
