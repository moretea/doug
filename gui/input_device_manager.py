from gui import Gdk

class InputDeviceManager:
    """
    The InputDeviceMangager is responsible for keeping track of how the users wants to use
    the different available input devices.
    """

    class Device():
        """
        Settings for one devices
        """
        def __init__(self, dev):
            self.dev = dev
            self.name = dev.get_name()
            source = dev.get_source()
            self.source_type = source.value_name

        def is_pen(self):
            return self.source_type == "GDK_SOURCE_PEN"

        def is_touchscreen(self):
            return self.source_type == "GDK_SOURCE_TOUCHSCREEN"

    def __init__(self):
        display = Gdk.Display.get_default()
        self._device_manager = display.get_device_manager()
        self._device_manager.connect("device-added", self._device_added_cb)
        self._device_manager.connect("device-removed", self._device_removed_cb)

        self._devs = {}

        for dev in self._device_manager.list_devices(Gdk.DeviceType.SLAVE):
            self._devs[dev] = InputDeviceManager.Device(dev)

    def find(self, device):
        return self._devs.get(device, None)

    def _device_added_cb(self, x, dev):
        pass

    def _device_removed_cb(self, x, dev):
        pass
