from . import root

def init_routers(app):
    app.include_router(root.router)
