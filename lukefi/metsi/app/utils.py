""" App utility functions """


class MetsiException(Exception):
    """ Base type for Metsi exceptions """


class ConfigurationException(MetsiException):
    """ Custom exception for invalid user control and configurations settings """


class ConditionFailed(MetsiException):
    """ Pre- or postcondition failed """
