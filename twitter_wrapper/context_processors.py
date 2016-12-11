def app_name_processor(request):
    return { 'app_name': request.resolver_match.app_name }
