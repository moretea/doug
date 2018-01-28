from gui import Gtk 
from gui import Gdk

from gui.page_viewer import PageViewer as PageViewer
from gui.input_device_manager import InputDeviceManager

def get_instance():
    """Return singleton applicaiton instance"""
    return Application._INSTANCE

class Application:
    _INSTANCE = None

    def __init__(self):
        # Ensure that we can only instantiate Applicaiton once.
        assert Application._INSTANCE is None
        super(Application, self).__init__()
        Application._INSTANCE = self

        self.dev_manager = InputDeviceManager()

        # Keep track of page viewers
        initPage = PageViewer("init")
        self.page_viewers = [initPage]


    def deregister_page_viewer(self, viewer):
        self.page_viewers.remove(viewer)

        if len(self.page_viewers) == 0:
            self.quit()

    def quit(self):
        Gtk.main_quit()
