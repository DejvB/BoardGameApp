from django.contrib import admin

from .helpers import scrape_bgg_info, update_bg_info


def update_data(modeladmin, request, queryset):
    for boardgame in queryset:
        bg_info = scrape_bgg_info(boardgame.bgg_id)
        update_bg_info(boardgame.id, bg_info)


update_data.short_description = 'Update data'


class BoardgamesAdmin(admin.ModelAdmin):
    actions = [update_data, ]



