from django.contrib import admin
from _data._data_dashboard import Link


class LinkAdmin(admin.ModelAdmin):
    list_display = ('link_id', 'link_description', 'link_url', 'link_time', 'link_semester',)
    search_fields = ('link_id', 'link_description', 'link_url', 'link_semester',)
    list_filter = ('link_semester',)


admin.site.register(Link, LinkAdmin)
