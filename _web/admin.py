from django.contrib import admin

from .models import main_site
from .models import menu
from .models import footer
from .models import menu_box
from .models import menu_box_item


class main_siteAdmin(admin.ModelAdmin):
    list_display = ('site_id', "site_name_en", 'site_name_ar', 'is_actual')
    search_fields = ('site_name_en',)

    def is_actual(self, object_):
        return object_.site_id == main_site.objects.order_by('-site_id')[0].site_id

    is_actual.short_description = u'Actual Main Site'
    is_actual.boolean = True


admin.site.register(main_site, main_siteAdmin)


class menuAdmin(admin.ModelAdmin):
    list_display = ('menu_id', 'menu_order', 'menu_name_en', 'menu_link', 'menu_super_menu', 'menu_isRootMenu')
    search_fields = ('menu_name_en',)


admin.site.register(menu, menuAdmin)


class footerAdmin(admin.ModelAdmin):
    list_display = ('footer_id', 'footer_text_en', 'footer_year', 'footer_version', 'is_actual')
    search_fields = ('footer_text_en',)

    def is_actual(self, object_):
        return object_.footer_id == footer.objects.order_by('-footer_id')[0].footer_id

    is_actual.short_description = u'Actual Footer'
    is_actual.boolean = True


admin.site.register(footer, footerAdmin)


class menuboxAdmin(admin.ModelAdmin):
    list_display = ('menu_box_id', 'menu_box_order', 'menu_box_name')
    search_fields = ('menu_box_name',)


admin.site.register(menu_box, menuboxAdmin)


class menu_box_itemAdmin(admin.ModelAdmin):
    list_display = ('menu_box_item_id', 'menu_box_item_order', 'menu_box', 'menu_box_item_name',)
    search_fields = ('menu_box_item_name',)
    list_filter = ('menu_box__menu_box_name',)


admin.site.register(menu_box_item, menu_box_itemAdmin)
