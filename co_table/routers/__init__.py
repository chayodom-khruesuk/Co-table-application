from . import root, user, authentication, room, table, reservation

def init_routers(app):
    app.include_router(root.router)
    app.include_router(user.router)
    app.include_router(authentication.router)
    app.include_router(room.router)
    app.include_router(table.router)
    app.include_router(reservation.router)