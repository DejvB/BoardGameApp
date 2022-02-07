from django.contrib import admin

from .models import (
    Boardgames,
    Category,
    Designer,
    Gameplay,
    Mechanics,
    OwnBoardgame,
    Player,
    PlayerSpecifics,
    Results,
    UsedExpansion,
    ScoringSpecifics,
    ScoringTable,
)

from .views.admin_actions import BoardgamesAdmin

admin.site.register(Boardgames)
admin.site.register(OwnBoardgame, BoardgamesAdmin)
admin.site.register(Gameplay)
admin.site.register(Player)
admin.site.register(Results)
admin.site.register(UsedExpansion)
admin.site.register(Category)
admin.site.register(Mechanics)
admin.site.register(Designer)
admin.site.register(PlayerSpecifics)
admin.site.register(ScoringSpecifics)
admin.site.register(ScoringTable)
