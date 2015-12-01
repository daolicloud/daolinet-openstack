from django.utils.translation import ugettext_lazy as _

import horizon


class Edges(horizon.Panel):
    name = _("Distributed Firewall")
    slug = 'edges'
