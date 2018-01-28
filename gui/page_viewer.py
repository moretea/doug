from gui import GObject

from gui import Gtk
from gui import Gdk
from gui import application

import lib

class PageViewer:
    def __init__(self, id):
        self.window = Gtk.Window(title = "Hello World")
        self.page_widget = PageWidget()
        self.window.add(self.page_widget)
        self.window.connect("destroy", self.quit_cb)
        self.window.show_all()

    def quit_cb(self, widget):
        gui.application.get_instance().deregister_page_viewer(self)

class Stroke:
    """
    Models a continuous stroke

    The problem is that we'd get events with less accuracy than we'd ideally have.
    We need to use a cutoff time between events to ensure that we group events in the
    correct.
    
    """
    CUTOFF_TIME=100

    def __init__(self, first_point):
        """
            first_point = (t,x,y)
        """

        (t, x, y) = first_point
        self.points = [(x,y)]
        self.last_added = t

    def attempt_add(self, point):
        """
            Attempt to add a (t,x,y) to this troke.
            Returns True if it is considered to be part of the same stroe,
            False if it should be a new stroke
        """

        (t,x,y) = point

        max_acceptable_time_as_same_stroke = self.last_added + Stroke.CUTOFF_TIME

        if max_acceptable_time_as_same_stroke > t:
            self.points.append((x,y))
            self.last_added = t
            return True
        else:
            return False

    def intersects_with_line(self, a, b):
        (line_x1, line_y1) = a
        (line_x2, line_y2) = b

        if len(self.points) < 2:
            return False

        stroke_prev_coord = self.points[0]
        for stroke_current_coord in self.points[1:]:
            stroke_line_segment = (stroke_prev_coord, stroke_current_coord)
            cursor_line_segment = (a,b)
            if lib.stroke.intersection(stroke_line_segment, cursor_line_segment):
                return True
            continue
            stroke_a = stroke_prev_coord
            stroke_b = stroke_current_coord

            p0_x = float(line_x1)
            p0_y = float(line_y1)
            p1_x = float(line_x2)
            p1_y = float(line_y2)
            p2_x = float(stroke_a[0])
            p2_y = float(stroke_a[1])
            p3_x = float(stroke_b[0])
            p3_y = float(stroke_b[1])

            s10_x = p1_x - p0_x;
            s10_y = p1_y - p0_y;
            s32_x = p3_x - p2_x;
            s32_y = p3_y - p2_y;

            denom = s10_x * s32_y - s32_x * s10_y
            if denom == 0:
                continue # Collinear

            denomPositive = denom > 0

            s02_x = p0_x - p2_x
            s02_y = p0_y - p2_y
            s_numer = s10_x * s02_y - s10_y * s02_x
            if (s_numer < 0) == denomPositive:
                continue # No collision

            t_numer = s32_x * s02_y - s32_y * s02_x
            if (t_numer < 0) == denomPositive:
                continue # No collision

            if ((s_numer > denom) == denomPositive) or ((t_numer > denom) == denomPositive):
                continue # No collision

            # Collision detected
            return True
        
        return False

class BaseMode(GObject.GObject):
    __gsignals__ = {
            "enter-mode": (GObject.SIGNAL_RUN_FIRST, None, ()),
            "leave-mode": (GObject.SIGNAL_RUN_FIRST, None, ())
    }

    def __init__(self, page_widget):
        super().__init__()
        self.page_widget = page_widget

    def motion_notify_cb(self, widget, event):
        pass

    def button_press_cb(self, widget, event):
        pass

    def button_release_cb(self, widget, event):
        pass

    def touch_event_cb(self, widget, event):
        pass

class DrawMode(BaseMode):
    NAME = "Draw"
    def __init__(self, page_widget):
        super().__init__(page_widget)
        self.connect("enter-mode", self.enter_mode_cb)

    def enter_mode_cb(self,x):
        print("Enter draw mode")

    def motion_notify_cb(self, widget, event):
        device = application.get_instance().dev_manager.find(event.get_source_device())

        if device.is_pen():
            state_flags = event.get_state()
            if state_flags & Gdk.ModifierType.BUTTON1_MASK:
                self.page_widget.renderer.add((event.time, event.x,event.y))

class DeleteStrokeMode(BaseMode):
    NAME = "Delete strokes"
    def __init__(self, page_widget):
        super().__init__(page_widget)
        self.last_del_pos = None

    def motion_notify_cb(self, widget, event):
        device = application.get_instance().dev_manager.find(event.get_source_device())

        if device.is_pen():
            state_flags = event.get_state()
            if state_flags & Gdk.ModifierType.BUTTON1_MASK:
                current_pos = (event.x, event.y)
                if self.last_del_pos is not None:
                    self.delete_matching_strokes(self.last_del_pos, current_pos)
                self.last_del_pos = current_pos

    def delete_matching_strokes(self, p1, p2)
        for stroke in self.page_widget.renderer.strokes:
            if stroke.intersects_with_line(p1,p2):
                self.page_widget.renderer.strokes.remove(stroke)
                self.page_widget.queue_draw()

class ZoomMode(BaseMode):
    NAME = "Zoom"

class PanMode(BaseMode):
    NAME = "Pan"

class ContextMenu():
    def __init__(self, page_widget):
        self.page_widget = page_widget

        # Build the menu items
        self._menu = Gtk.Menu()
        self._menu_items = {}

        for mode_name in page_widget.modes:
            item = Gtk.CheckMenuItem(mode_name)
            item.connect("activate", self._menu_activated_cb, mode_name)
            self._menu_items[mode_name] = item
            self._menu.append(item)

        self._menu_visible = False
        self._menu.show_all()
        self._menu.connect("deactivate", self._cancel_popup_cb)
        self._menu.connect("cancel", self._cancel_popup_cb)
        self._menu.connect("hide", self._cancel_popup_cb)
        self._menu.connect("focus-out-event", self._cancel_popup_cb)

        self._tick_current_mode()

        # Prevents re-triggering states
        self._updating_ticks = False

        self.visible = False

    def show(self):
        self.visible = True
        self._menu.popup(None, None, None, None, 0, 0)

    def _tick_current_mode(self):
        """Updates the tick in the context menu to select the mode."""

        self._updating_ticks = True

        for mode_name in self.page_widget.modes:
            is_active = self.page_widget.current_mode == self.page_widget.modes[mode_name]
            print(mode_name, is_active)
            self._menu_items[mode_name].set_active(is_active)

        self._updating_ticks = False

    def _menu_activated_cb(self, widget, mode_name):
        if self._updating_ticks:
            return
        else:
            self.context_menu_visible = False
            self.page_widget.set_mode(self.page_widget.modes[mode_name])
            self._tick_current_mode() # Prepare for next menu

    def _cancel_popup_cb(self, widget, event = None):
        self.visible = False

class PageWidget(Gtk.EventBox):
    """
        Captures events, delegates them to correct mode.
    """
    MODES = [ DrawMode, DeleteStrokeMode, ZoomMode, PanMode ]
    INITIAL_MODE_NAME = DrawMode.NAME

    def __init__(self):
        super().__init__()

        # Add page renderer
        self.renderer = PageRenderer(self)
        self.add(self.renderer)

        # Select which events we're interested in
        self.add_events(Gdk.EventMask.BUTTON_PRESS_MASK |
                        Gdk.EventMask.BUTTON_RELEASE_MASK |
                        Gdk.EventMask.TOUCH_MASK |
                        Gdk.EventMask.POINTER_MOTION_MASK |
                        Gdk.EventMask.POINTER_MOTION_HINT_MASK |
                        Gdk.EventMask.SMOOTH_SCROLL_MASK)

        # Generic callbacks
        self.connect("motion-notify-event", self.motion_notify_cb)
        self.connect("button-release-event", self.button_release_cb)
        self.connect("button-press-event", self.button_press_cb)
        #self.connect("touch-event", self.touch_event_cb)
        #self.zoom_gesture = Gtk.GestureZoom()
        #self.zoom_gesture.connect("scale-changed", self.scale_changed_cb)

        # Modes
        self._init_modes()
        self.context_menu = ContextMenu(self) # Must be initilaized after _init_modes()

    def set_mode(self, mode):
        if self.current_mode != mode:
            self.current_mode.emit("leave-mode")
            self.current_mode = mode
            self.current_mode.emit("enter-mode")

    def _init_modes(self):
        self.modes = {}

        for mode_class in PageWidget.MODES:
            self.modes[mode_class.NAME] = mode_class(self)

        self.current_mode = self.modes[PageWidget.INITIAL_MODE_NAME]
    
    def button_press_cb(self, widget, event):
        device = application.get_instance().dev_manager.find(event.get_source_device())
        #print("press", device.name)

    def button_release_cb(self, widget, event):
        device = application.get_instance().dev_manager.find(event.get_source_device())
        #print("release", device.name)

    def motion_notify_cb(self, widget, event):
        device = application.get_instance().dev_manager.find(event.get_source_device())

        if device.is_pen():
            state_flags = event.get_state()

            if state_flags & Gdk.ModifierType.BUTTON2_MASK:
                if not self.context_menu.visible:
                    self.context_menu.show()
                return

        self.current_mode.motion_notify_cb(widget, event)

    def scale_changed_cb(self, widget, scale):
        print("Scale changed", scale)

    def touch_event_cb(self, widget, event):
        if event.touch.type == Gdk.EventType.TOUCH_BEGIN:
            print("touch begin")
            self.touches[event.touch.sequence] = (event.x, event.y)
        elif event.touch.type == Gdk.EventType.TOUCH_END:
            print("touch end")
            del self.touches[event.touch.sequence]
        else:
            print(event.touch.type.value_name)

class PageRenderer(Gtk.DrawingArea):
    """
        Actually renders everything on the page.
    """
    def __init__(self, page_widget):
        super().__init__()
        self.connect("draw", self.draw_cb)
        self.strokes = []
        self.last_stroke = None


    def add(self, tpoint):
        """tpoint == (t,x,y)"""

        added_to_existing = False

        if self.last_stroke is not None:
            if self.last_stroke.attempt_add(tpoint):
                added_to_existing = True

        if not added_to_existing:
            stroke = Stroke(tpoint)
            self.strokes.append(stroke)
            self.last_stroke = stroke

        self.queue_draw()

    def draw_cb(self, widget, cr):
        self.draw_roster(cr)
        self.draw_strokes(cr)

    def draw_strokes(self, cr):
        for stroke in self.strokes:
            self.draw_stroke(stroke, cr)

    def draw_stroke(self, stroke, cr):
        points = list(stroke.points)

        if len(points) > 2:
            cr.set_source_rgba(0, 30, 0, 1)
            cr.set_line_width(2)
            (x,y) = points.pop(0)
            cr.move_to(x,y)

            for (x,y) in points:
                cr.line_to(x,y)

            cr.stroke()


    ROSTER_SPACE=20
    ROSTER_WIDTH=2
    def draw_roster(self, cr):
        width = self.get_allocated_width()
        height = self.get_allocated_height()

        # Fill background with white
        cr.set_source_rgba(255,255,255,1)
        cr.rectangle(0, 0, width, height)
        cr.fill()

        # Set color for roster.
        cr.set_source_rgba(0, 0, 50, 0.2)

        # Draw columns
        for x in range(self.ROSTER_SPACE, (width // self.ROSTER_SPACE) * self.ROSTER_SPACE, self.ROSTER_SPACE):
            cr.rectangle(x, 0, self.ROSTER_WIDTH, height)
            cr.fill()
            
        # Draw rows
        for y in range(self.ROSTER_SPACE, (height // self.ROSTER_SPACE) * self.ROSTER_SPACE, self.ROSTER_SPACE):
            cr.rectangle(0, y, width, self.ROSTER_WIDTH)
            cr.fill()
