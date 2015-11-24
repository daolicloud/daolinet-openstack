"""Custom SQLAlchemy types."""

from oslo_serialization import jsonutils

import netaddr
from oslo_utils import netutils
from sqlalchemy.dialects import postgresql
from sqlalchemy import Text
from sqlalchemy import types

from daoliagent import utils

class JsonBlob(types.TypeDecorator):
    impl = Text

    def process_bind_param(self, value, dialect):
        return jsonutils.dumps(value)

    def process_result_value(self, value, dialect):
        return jsonutils.loads(value)

class IPAddress(types.TypeDecorator):
    """An SQLAlchemy type representing and IP-address."""

    impl = types.String

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(postgresql.INET())
        else:
            return dialect.type_descriptor(types.String(39))

    def process_bind_param(self, value, dialect):
        """Process/Formats the value before insert it into the db."""
        if dialect.name == 'postgresql':
            return value
        # NOTE(maurosr): The purpose here is to convert ipv6 to the shortened
        # form, not validate it.
        elif netutils.is_valid_ipv6(value):
            return utils.get_shortened_ipv6(value)
        return value

class CIDR(types.TypeDecorator):
    """An SQLAlchemy type representing a CIDR definition."""

    impl = types.String

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(postgresql.INET())
        else:
            return dialect.type_descriptor(types.String(43))

    def process_bind_param(self, value, dialect):
        """Process/Formats the value before insert it into the db."""
        # NOTE(sdague): normalize all the inserts
        if utils.is_valid_ipv6_cidr(value):
            return utils.get_shortened_ipv6_cidr(value)
        return value

    def process_result_value(self, value, dialect):
        try:
            return str(netaddr.IPNetwork(value, version=4).cidr)
        except netaddr.AddrFormatError:
            return str(netaddr.IPNetwork(value, version=6).cidr)
        except TypeError:
            return None 
