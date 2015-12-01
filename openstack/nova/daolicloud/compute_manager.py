from nova.compute import manager

class ComputeManager(manager.ComputeManager):

    def __init__(self, compute_driver=None, *args, **kwargs):
        super(ComputeManager, self).__init__(
            compute_driver=compute_driver, *args, **kwargs)
