# PiTiVi , Non-linear video editor
#
#       pitivi/ui/controller.py
#
# Copyright (c) 2009, Brandon Lewis <brandon_lewis@berkeley.edu>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.

import gtk.gdk
from pitivi.receiver import receiver, handler
from pitivi.ui.point import Point

# Controllers are reusable and implement specific behaviors. Currently this
# Includes only click, and drag. Multiple controllers could be attached to a
# given view, but might interfere with each other if they attempt to handle
# the same set of signals. It is probably better to define a new controller
# that explictly combines the functionality of both when custom behavior is
# desired.

ARROW = gtk.gdk.Cursor(gtk.gdk.ARROW)

class Controller(object):

    """A controller which implements drag-and-drop bahavior on connected view
    objects. Subclasses may override the drag_start, drag_end, pos, and
    set_pos methods"""

    # note we SHOULD be using the gtk function for this, but it doesn't appear
    # to be exposed in pygtk
    __DRAG_THRESHOLD__ = Point(0, 0)

    _view = receiver()

    _dragging = None
    _canvas = None
    _cursor = None
    _ptr_within = False
    _last_click = None
    _initial = None
    _mousedown = None
    _last_event = None

    def __init__(self, view=None):
        object.__init__(self)
        self._view = view

## convenience functions

    def from_event(self, event):
        """returns the coordinates of an event"""
        return Point(*self._canvas.convert_from_pixels(event.x, event.y))

    def from_item_event(self, item, event):
        return Point(*self._canvas.convert_from_item_space(item,
            *self.from_event(event)))

    def to_item_space(self, item, point):
        return Point(*self._canvas.convert_to_item_space(item, *point))

    def pos(self, item):
        bounds = item.get_bounds()
        return Point(bounds.x1, bounds.y1)

## signal handlers

    @handler(_view, "enter_notify_event")
    def enter_notify_event(self, item, target, event):
        self._last_event = event
        if self._cursor:
            event.window.set_cursor(self._cursor)
        self.enter(item, target)
        self._ptr_within = True
        return True

    @handler(_view, "leave_notify_event")
    def leave_notify_event(self, item, target, event):
        self._last_event = event
        self._ptr_within = False
        event.window.set_cursor(ARROW)
        if not self._dragging:
            self.leave(item, target)
        return True

    @handler(_view, "button_press_event")
    def button_press_event(self, item, target, event):
        self._last_event = event
        if not self._canvas:
            self._canvas = item.get_canvas()
        self._mousedown = self.pos(item) - self.transform(self.from_item_event(
            item, event))
        self._dragging = target
        self._initial = self.pos(target)
        self._drag_start(item, target, event)
        return True

    @handler(_view, "motion_notify_event")
    def motion_notify_event(self, item, target, event):
        self._last_event = event
        if self._dragging:
            self.set_pos(self._dragging,
                self.transform(self._mousedown + self.from_item_event(item,
                    event)))
            return True
        return False

    @handler(_view, "button_release_event")
    def button_release_event(self, item, target, event):
        self._last_event = event
        self._drag_end(item, self._dragging, event)
        self._dragging = None
        return True

## internal callbacks

    def _drag_start(self, item, target, event):
        self.drag_start()

    def _drag_end(self, item, target, event):
        self.drag_end()
        if self._ptr_within and self._drag_threshold():
            point = self.from_item_event(item, event)
            if self._last_click and (event.time - self._last_click < 400):
                self.double_click(point)
            else:
                self.click(point)
            self._last_click = event.time

    def _drag_threshold(self):
        last = self.pos(self._dragging)
        difference = abs(self._initial - last)
        if abs(self._initial - last) > self.__DRAG_THRESHOLD__:
            return False
        return True

## protected interface for subclasses

    def click(self, pos):
        pass

    def double_click(self, pos):
        pass

    def drag_start(self):
        pass

    def drag_end(self):
        pass

    def set_pos(self, obj, pos):
        obj.props.x, obj.props.y = pos

    def transform(self, pos):
        return pos

    def enter(self, item, target):
        pass

    def leave(self, item, target):
        pass
