from django.utils.translation import ugettext_lazy as _

import horizon


class VPCs(horizon.Panel):
    name = _("VPCs")
    slug = 'vpcs'
