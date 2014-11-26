class Error(Exception):
    """Base class for exceptions in this module."""
    pass

class InstagramPermissionError(Error):
    """Exception raised for errors derived from calling the Intsgram API.

    Attributes:
        userid -- user id that caused a permissions error
    """

    def __init__(self, userid):
        self.id = userid

class GeocodeQuotaError(Error):
    """Exception raised for errors derived from exceeding the Geocode API quota

    Attributes:
        key -- API key used to hit the endpoint
    """

    def __init__(self, userid):
        self.id = userid