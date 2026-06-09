import jwt
from django.conf import settings
from django_tenants.utils import get_tenant_model, get_public_schema_name
from apps.core.models import User
from django.db import connection

class JWTTenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        tenant_model = get_tenant_model()
        public_schema = get_public_schema_name()
        
        # Default to public schema
        connection.set_schema_to_public()
        try:
            request.tenant = tenant_model.objects.get(schema_name=public_schema)
        except tenant_model.DoesNotExist:
            request.tenant = None
            
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            try:
                payload = jwt.decode(token, options={"verify_signature": False})
                
                # If impersonating, use the injected tenant_id
                if 'tenant_id' in payload:
                    schema_name = payload['tenant_id']
                    try:
                        tenant = tenant_model.objects.get(schema_name=schema_name)
                        connection.set_tenant(tenant)
                        request.tenant = tenant
                    except tenant_model.DoesNotExist:
                        pass
                # Otherwise use the user's cabinet
                elif 'user_id' in payload:
                    user_id = payload['user_id']
                    user = User.objects.select_related('cabinet').get(id=user_id)
                    if user.cabinet:
                        connection.set_tenant(user.cabinet)
                        request.tenant = user.cabinet
            except Exception as e:
                import logging
                logging.error(f"JWTTenantMiddleware exception: {e}")
                pass

        return self.get_response(request)
