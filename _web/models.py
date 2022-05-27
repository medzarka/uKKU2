from django.db import models


class main_site(models.Model):
    site_id = models.AutoField(primary_key=True, verbose_name='ID')
    site_name_en = models.CharField(max_length=250, unique=True, verbose_name='Site Name', blank=False,
                                    null=False)
    site_short_name_en = models.CharField(max_length=100, unique=True, verbose_name='Site Short Name', blank=False,
                                          null=False)
    site_name_ar = models.CharField(max_length=250, unique=True, verbose_name='Site Arabic Name', blank=False,
                                    null=False)
    site_short_name_ar = models.CharField(max_length=100, unique=True, verbose_name='Site Short Arabic Name',
                                          blank=False,
                                          null=False)
    site_name_link = models.CharField(max_length=250, unique=True, verbose_name='Site Name link', blank=False,
                                      null=False)
    site_logo = models.ImageField(upload_to='media/site/images/')

    def __str__(self):
        return self.site_name_en

    class Meta:
        ordering = ['site_id']
        verbose_name_plural = 'Main Site'
        verbose_name = 'Main Site'
        indexes = [
            models.Index(fields=['site_name_en', ]),
            models.Index(fields=['site_short_name_en', ]),
            models.Index(fields=['site_name_ar', ]),
            models.Index(fields=['site_short_name_ar', ]),

        ]


class menu(models.Model):
    menu_id = models.AutoField(primary_key=True, verbose_name='ID')
    menu_order = models.IntegerField(verbose_name='Menu Order', unique=True)
    menu_name_en = models.CharField(max_length=250, unique=True, verbose_name='Menu Name', blank=False,
                                    null=False)
    menu_name_ar = models.CharField(max_length=250, unique=True, verbose_name='Menu Arabic Name', blank=False,
                                    null=False)
    menu_link = models.CharField(max_length=250, verbose_name='Menu Link', blank=False,
                                 null=True)
    menu_isRootMenu = models.BooleanField(verbose_name='is Root Menu', default=True)
    menu_super_menu = models.ForeignKey('self', null=True, blank=True, related_name='items',
                                        limit_choices_to={'menu_isRootMenu': True}, on_delete=models.CASCADE)
    menu_fontawesome = models.CharField(max_length=250, verbose_name='Menu Box Item fontawesome',
                                                 help_text="get Images form https://fontawesome.com/icons?m=free",
                                                 blank=True,
                                                 null=True)

    def __str__(self):
        return self.menu_name_en

    class Meta:
        ordering = ['menu_order']
        verbose_name_plural = 'Menu Items'
        verbose_name = 'Menu Item'
        indexes = [
            models.Index(fields=['menu_name_en', ]),
            models.Index(fields=['menu_link', ]),
            models.Index(fields=['menu_order', ]),
            models.Index(fields=['menu_super_menu', ]),
            models.Index(fields=['menu_name_ar', ]),
        ]


class footer(models.Model):
    footer_id = models.AutoField(primary_key=True, verbose_name='ID')
    footer_text_en = models.CharField(max_length=250, unique=True, verbose_name='Footer Text', blank=False,
                                      null=False)
    footer_text_ar = models.CharField(max_length=250, unique=True, verbose_name='Footer Arab Text', blank=False,
                                      null=True)
    footer_year = models.CharField(max_length=250, unique=True, verbose_name='Footer Year', blank=False,
                                   null=True)
    footer_version = models.CharField(max_length=250, unique=True, verbose_name='Footer Version', blank=False,
                                      null=False)
    footer_address_en = models.CharField(max_length=1024, unique=True, verbose_name='Footer Address', blank=False,
                                         null=False)
    footer_address_ar = models.CharField(max_length=1024, unique=True, verbose_name='Footer Arab Address', blank=False,
                                         null=False)
    footer_logo = models.ImageField(upload_to='media/site/images/')

    def __str__(self):
        return self.footer_text_en

    class Meta:
        ordering = ['footer_id']
        verbose_name_plural = 'Footers'
        verbose_name = 'Footer'
        indexes = [
            models.Index(fields=['footer_text_en', ]),
            models.Index(fields=['footer_text_ar', ]),
            models.Index(fields=['footer_year', ]),
            models.Index(fields=['footer_version', ]),
            models.Index(fields=['footer_address_en', ]),
            models.Index(fields=['footer_address_ar', ]),
        ]


class menu_box(models.Model):
    menu_box_id = models.AutoField(primary_key=True, verbose_name='ID')
    menu_box_name = models.CharField(max_length=250, unique=True, verbose_name='Menu Box Name', blank=False,
                                     null=False)
    menu_box_name_ar = models.CharField(max_length=250, unique=True, verbose_name='Menu Box Arabic Name', blank=False,
                                        null=False)
    menu_box_logo = models.ImageField(upload_to='media/site/images/', null=True, blank=True)
    menu_box_order = models.IntegerField(verbose_name='Menu Box Order')

    def __str__(self):
        return self.menu_box_name

    class Meta:
        ordering = ['menu_box_order']
        verbose_name_plural = 'Menu Boxes'
        verbose_name = 'Menu Box'
        indexes = [
            models.Index(fields=['menu_box_name', ]),
            models.Index(fields=['menu_box_name_ar', ]),
            models.Index(fields=['menu_box_order', ]),
        ]


class menu_box_item(models.Model):
    menu_box_item_id = models.AutoField(primary_key=True, verbose_name='ID')
    menu_box_item_name = models.CharField(max_length=250, unique=True, verbose_name='Menu Box Item Name', blank=False,
                                          null=False)
    menu_box_item_name_ar = models.CharField(max_length=250, unique=True, verbose_name='Menu Box Item Arabic Name',
                                             blank=False,
                                             null=False)
    menu_box_item_order = models.IntegerField(verbose_name='Menu Box Item Order')
    menu_box = models.ForeignKey(menu_box, null=True, related_name='items', on_delete=models.CASCADE)
    menu_box_link = models.CharField(max_length=250, verbose_name='Item link', blank=False,
                                     null=False, default='')

    # see https://fontawesome.com/icons?m=free
    menu_box_item_fontawesome = models.CharField(max_length=250, verbose_name='Menu Box Item fontawesome',
                                                 help_text="get Images form https://fontawesome.com/icons?m=free",
                                                 blank=True,
                                                 null=True)

    def __str__(self):
        return self.menu_box_item_name

    class Meta:
        ordering = ['menu_box', 'menu_box_item_order']
        verbose_name_plural = 'Menu Box Items'
        verbose_name = 'Menu Box Item'
        indexes = [
            models.Index(fields=['menu_box_item_name', ]),
            models.Index(fields=['menu_box_item_name_ar', ]),
            models.Index(fields=['menu_box_item_order', ]),
            models.Index(fields=['menu_box', ]),
        ]
