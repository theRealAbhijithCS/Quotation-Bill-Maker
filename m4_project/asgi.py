import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'm4_project.settings')

django_asgi_app = get_asgi_application()

from quotations.fastapi_app import fastapi_app

async def application(scope, receive, send):
    if scope['type'] == 'http' and scope['path'].startswith('/api/fastapi'):
        await fastapi_app(scope, receive, send)
    else:
        await django_asgi_app(scope, receive, send)
