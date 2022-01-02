from django.contrib import admin

from .models import *

admin.site.register(Boardgames)
admin.site.register(OwnBoardgame)
admin.site.register(Gameplay)
admin.site.register(Player)
admin.site.register(Results)
admin.site.register(Expansion)
admin.site.register(OwnExpansion)
admin.site.register(UsedExpansion)