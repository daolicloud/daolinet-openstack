from daoliagent.i18n import _, _LE


class OPFException(Exception):
    message = "An unknown exception occurred."

    def __init__(self, msg=None, **kwargs):
        self.kwargs = kwargs

        if not msg:
            msg = self.message

            try:
                msg = msg % kwargs
            except Exception:
                # at least get the core message out if something happened
                msg = self.message

        super(OPFException, self).__init__(msg)

    def format_message(self):
        return self.args[0]

class DevicePortNotFound(OPFException):
    message = 'no such network device %(device)s'

class IPAddressNotMatch(OPFException):
    message = 'IP address %(address)s do not match'

class NotFound(OPFException):
    message = _("Resource could not be found.")

class InstanceNotFound(NotFound):
    message = _("Instance %(instance_id)s could not be found.")

class FixedIpNotFound(NotFound):
    message = _("No fixed IP associated with id %(id)s.")

class FixedIpNotFoundForInstance(FixedIpNotFound):
    message = _("Instance %(instance_uuid)s has zero fixed ips.")

class Invalid(OPFException):
    message = _("Unacceptable parameters.")

class InvalidUUID(Invalid):
    message = _("Expected a uuid but received %(uuid)s.")

class InvalidIpAddressError(Invalid):
    message = _("%(address)s is not a valid IP v4/6 address.")
