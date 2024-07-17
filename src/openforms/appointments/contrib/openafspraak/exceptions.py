from ...exceptions import AppointmentException


class OpenAfspraakException(AppointmentException):
    pass


class GracefulOpenAfspraakException(OpenAfspraakException):
    """
    Raise when the program execution can continue with a fallback error.
    """
