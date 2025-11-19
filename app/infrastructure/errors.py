class InfrastructureProviderNotCompatibleError(Exception):
    '''
    Raises if the Symbol or Currency isn't supported by the asked provider
    '''
    pass



class InfrastructureBadURL(Exception):
    pass



class InfrastructureExternalApiTimeout(Exception):
    pass

class InfrastructureExternalApiError(Exception):
    pass

class InfrastructureExternalApiMalformedResponse(Exception):
    pass
