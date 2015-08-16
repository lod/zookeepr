#from resources import MyResource
from pyramid.view import view_config
from pyramid.response import Response

@view_config(route_name='api.config', request_method='GET', permission='admin', renderer='json')
def my_view(request):
    # request.json_body
    return {'content':'Hello!'}
    # return Response('OK')
