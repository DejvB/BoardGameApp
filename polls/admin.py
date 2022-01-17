from django.contrib import admin

from .models import (
    Boardgames,
    Category,
    Designer,
    Expansion,
    Gameplay,
    Mechanics,
    OwnBoardgame,
    OwnExpansion,
    Player,
    PlayerSpecifics,
    Results,
    UsedExpansion,
)

admin.site.register(Boardgames)
admin.site.register(OwnBoardgame)
admin.site.register(Gameplay)
admin.site.register(Player)
admin.site.register(Results)
admin.site.register(Expansion)
admin.site.register(OwnExpansion)
admin.site.register(UsedExpansion)
admin.site.register(Category)
admin.site.register(Mechanics)
admin.site.register(Designer)
admin.site.register(PlayerSpecifics)
