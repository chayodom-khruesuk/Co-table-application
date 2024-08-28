from . import root, user

def init_routers(app):
    app.include_router(root.router)
    app.include_router(user.router)