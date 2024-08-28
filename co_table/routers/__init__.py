from . import root, user, authentication

def init_routers(app):
    app.include_router(root.router)
    app.include_router(user.router)
    app.include_router(authentication.router)