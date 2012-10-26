# -*- coding: utf-8 -*-
#Copyright (c) 2011 Walter Bender
#Copyright (c) 2012 Ignacio Rodriguez

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.

import os
from gi.repository import Gtk, Gdk, GObject, GdkPixbuf
import sugar3
from sugar3.activity import activity
from sugar3 import profile
from sugar3.graphics.toolbarbox import ToolbarBox
from sugar3.bundle.activitybundle import ActivityBundle
from sugar3.activity.widgets import ActivityToolbarButton
from sugar3.activity.widgets import StopButton
from sugar3.graphics.toolbarbox import ToolbarButton

from toolbar_utils import button_factory, separator_factory, label_factory
from sprites import Sprites, Sprite

from gettext import gettext as _

from sugar3.graphics import style
GRID_CELL_SIZE = style.GRID_CELL_SIZE

SERVICE = 'org.sugarlabs.NapierActivity'
IFACE = SERVICE
PATH = '/org/augarlabs/NapierActivity'
BONE_WIDTH = 101
BONE_HEIGHT = 901


def _svg_header(scale=1.0):
    ''' Return standard header for SVG bones '''
    return '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\
<!-- Created with Emacs (http://gnu.org/) -->\
<svg\
   xmlns:dc="http://purl.org/dc/elements/1.1/"\
   xmlns:cc="http://creativecommons.org/ns#"\
   xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"\
   xmlns:svg="http://www.w3.org/2000/svg"\
   xmlns="http://www.w3.org/2000/svg"\
   version="1.1"\
   width="%f"\
   height="%f">' % (101 * scale, 901 * scale)


def _svg_footer():
    ''' Return standard footer for SVG bones '''
    return '</svg>\
'

def _svg_single_box(a, scale=1.0):
    ''' Return standard top-of-column box for SVG bones '''
    return '    <g>\
      <rect\
	  width="%f"\
	  height="%f"\
	  x="%f"\
	  y="%f"\
	  style="fill:#ffffff;stroke:#000000;stroke-width:%f;stroke-linecap:square;stroke-linejoin:round;stroke-miterlimit:%f;stroke-opacity:1;stroke-dasharray:none" />\
      <text\
      style="font-size:%fpx;font-style:normal;font-weight:bold;fill:#000000;fill-opacity:1;stroke:none;font-family:Sans;text-align:center;text-anchor:middle">\
	<tspan x="%f" y="%f">\
	  %d\
	</tspan>\
      </text>\
    </g>' % (99 * scale, 99 * scale, scale, scale, 2 * scale,
             4 * scale, 40 * scale, 55 * scale, 65 * scale, a)


def _svg_double_box(a, b, y, scale=1.0):
    ''' Return standard double-digit box for SVG bones '''
    return '    <g>\
      <rect\
	  width="%f"\
	  height="%f"\
	  x="%f"\
	  y="%f"\
	  style="fill:#ffffff;stroke:none;stroke-width:%f;stroke-linecap:square;stroke-linejoin:round;stroke-miterlimit:%f;stroke-opacity:1;stroke-dasharray:none" />\
      <line\
	  x1="%f"\
	  y1="%f"\
	  x2="%f"\
	  y2="%f"\
	  style="fill:none;stroke:#000000;stroke-width:%f;stroke-linecap:butt;stroke-linejoin:miter;stroke-miterlimit:%f;stroke-opacity:1;stroke-dasharray:none" />\
      <line\
	  x1="%f"\
	  y1="%f"\
	  x2="%f"\
	  y2="%f"\
	  style="fill:none;stroke:#000000;stroke-width:%f;stroke-linecap:butt;stroke-linejoin:miter;stroke-miterlimit:%f;stroke-opacity:1;stroke-dasharray:none" />\
      <text\
	  style="font-size:%fpx;font-style:normal;font-weight:bold;fill:#000000;fill-opacity:1;stroke:none;font-family:Sans">\
	<tspan x="%f" y="%f">\
	  %d\
	</tspan>\
      </text>\
      <text\
      style="font-size:%fpx;font-style:normal;font-weight:bold;fill:#000000;fill-opacity:1;stroke:none;font-family:Sans">\
	<tspan x="%f" y="%f">\
	  %d\
	</tspan>\
      </text>\
    </g>' % (99 * scale, 99 * scale, scale, y * scale, 2 * scale,
             4 * scale, scale, (y + 99) * scale, 99 * scale,
             (y + 1) * scale, 2 * scale, 4 * scale, scale, (y + 1) * scale,
             99 * scale, (y + 1) * scale, 2 * scale, 4 * scale, 40 * scale,
             12 * scale, (y + 51) * scale, a, 40 * scale, 54 * scale,
             (y + 85) * scale, b)


def _bone_factory(value, scale=1.0):
    svg = _svg_header(scale=scale)
    svg += _svg_single_box(value, scale=scale)
    for i in range(9):
        if i > 0:
            j = (i + 1) * value
            svg += _svg_double_box(int(j / 10), j % 10, i * 100, scale=scale)
    return svg + _svg_footer()


def _svg_str_to_pixbuf(svg_string):
    ''' Load pixbuf from SVG string '''
    pl = GdkPixbuf.PixbufLoader.new_with_type('svg')
    pl.write(svg_string)
    pl.close()
    pixbuf = pl.get_pixbuf()
    return pixbuf


def _load_svg_from_file(file_path, width, height):
    '''Create a pixbuf from SVG in a file. '''
    return GdkPixbuf.Pixbuf.new_from_file_at_size(file_path, width, height)


class NapierActivity(activity.Activity):
    ''' Napier's bones: Napier's bones were invented by John Napier
    (1550-1617), a Scottish mathematician and scientist. They help you
    to do multiplication. '''

    # TODO: Define your own bone.

    def __init__(self, handle):
        ''' Initialize the toolbars and the work surface '''
        super(NapierActivity, self).__init__(handle)

        if os.path.exists(os.path.join('~', 'Activities', 'Napier.activity')):
            self._bone_path = os.path.join('~', 'Activities', 'Napier.activity',
                                      'bones')
        else:
            self._bone_path = os.path.join('.', 'bones')

        self._bones = []
        self._bone_images = [None, None, None, None, None, None, None, None,
                             None, None]
        self._blank_image = None
        self._number = 0
        self._number_of_bones = 0

        self._setup_toolbars()
        self._setup_canvas()
        self._circles = [None, None]
        self._ovals = []
        self._setup_workspace()
        self._restore()

    def _setup_canvas(self):
        ''' Create a canvas '''
        self._canvas = Gtk.DrawingArea()
        self._canvas.set_size_request(Gdk.Screen.width(),
                                      Gdk.Screen.height())
        self.set_canvas(self._canvas)
        self._canvas.show()
        self.show_all()

        self._canvas.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self._canvas.add_events(Gdk.EventMask.BUTTON_RELEASE_MASK)
        self._canvas.add_events(Gdk.EventMask.POINTER_MOTION_MASK)
        self._canvas.connect("draw", self.__draw_cb)
        self._canvas.connect("motion-notify-event", self._mouse_move_cb)
        # self._canvas.connect("key_press_event", self._key_press_cb)

    def _setup_workspace(self):
        ''' Add the bones. '''
        self._width = Gdk.Screen.width()
        self._height = int(Gdk.Screen.height() - (GRID_CELL_SIZE * 2))
        self._scale = self._height * 1.0 / BONE_HEIGHT
        self._bone_width = int(BONE_WIDTH * self._scale)
        self._bone_height = int(BONE_HEIGHT * self._scale)

        # Generate the sprites we'll need...
        self._sprites = Sprites(self._canvas)
        self._bone_index = Sprite(self._sprites, 0, 0, _load_svg_from_file(
                os.path.join(self._bone_path, 'bones-index.svg'),
                self._bone_width, self._bone_height))
        self._max_bones = int(self._width / self._bone_width) - 1
        self._blank_image = _load_svg_from_file(
                os.path.join(self._bone_path, 'blank-bone.svg'),
                self._bone_width, self._bone_height)
        for bones in range(self._max_bones):
            self._bones.append(Sprite(self._sprites, bones * self._bone_width,
                                      0, self._blank_image))
        circle_image = _load_svg_from_file(
            os.path.join(self._bone_path, 'circle.svg'), int(self._scale * 45),
            int(self._scale * 45))
        self._circles[0] = Sprite(self._sprites, 0, -100, circle_image)
        self._circles[1] = Sprite(self._sprites, 0, -100, circle_image)
        oval_image = _load_svg_from_file(
            os.path.join(self._bone_path, 'oval.svg'), int(self._scale * 129),
            int(self._scale * 92))
        for bones in range(self._max_bones - 1):
            self._ovals.append(Sprite(self._sprites, 0, -100, oval_image))

    def _setup_toolbars(self):
        ''' Setup the toolbars. '''

        self.max_participants = 1  # no sharing

        toolbox = ToolbarBox()

        # Activity toolbar
        activity_button = ActivityToolbarButton(self)

        toolbox.toolbar.insert(activity_button, 0)
        activity_button.show()

        self._bones_toolbar = Gtk.Toolbar()
        self._bones_toolbar_button = ToolbarButton(label=_('Select a bone'),
                                                       page=self._bones_toolbar,
                                                       icon_name='bones')

        self._bones_toolbar_button.show()
        toolbox.toolbar.insert(self._bones_toolbar_button, -1)
        self.set_toolbar_box(toolbox)
        toolbox.show()
        self.toolbar = toolbox.toolbar


        self._new_calc_button = button_factory(
            'erase', self.toolbar, self._new_calc_cb, tooltip=_('Clear'))

        self._status = label_factory(self.toolbar, '')

        button_factory('number-0', self._bones_toolbar, self._number_cb,
                        cb_arg=0, tooltip=_('zero'))

        button_factory('number-1', self._bones_toolbar, self._number_cb,
                        cb_arg=1, tooltip=_('one'))

        button_factory('number-2', self._bones_toolbar, self._number_cb,
                        cb_arg=2, tooltip=_('two'))

        button_factory('number-3', self._bones_toolbar, self._number_cb,
                        cb_arg=3, tooltip=_('three'))

        button_factory('number-4', self._bones_toolbar, self._number_cb,
                        cb_arg=4, tooltip=_('four'))

        button_factory('number-5', self._bones_toolbar, self._number_cb,
                        cb_arg=5, tooltip=_('five'))

        button_factory('number-6', self._bones_toolbar, self._number_cb,
                        cb_arg=6, tooltip=_('six'))

        button_factory('number-7', self._bones_toolbar, self._number_cb,
                        cb_arg=7, tooltip=_('seven'))

        button_factory('number-8', self._bones_toolbar, self._number_cb,
                        cb_arg=8, tooltip=_('eight'))

        button_factory('number-9', self._bones_toolbar, self._number_cb,
                        cb_arg=9, tooltip=_('nine'))

        separator_factory(toolbox.toolbar, True, False)
        stop_button = StopButton(self)
        stop_button.props.accelerator = '<Ctrl>q'
        toolbox.toolbar.insert(stop_button, -1)
        stop_button.show()
        self._bones_toolbar_button.set_expanded(True)

    def _new_calc_cb(self, button=None):
        ''' Start a new calculation. '''
        for bone in range(self._max_bones):
            self._bones[bone].set_shape(self._blank_image)
            self._bones[bone].inval()
        self._number_of_bones = 0
        self._number = 0
        self._status.set_label('')
        return

    def _number_cb(self, button=None, value=0):
        ''' Try to add a digit. '''
        if self._number_of_bones == self._max_bones:
            return
        self._number_of_bones += 1
        if self._bone_images[value] is None:
            self._bone_images[value] = _svg_str_to_pixbuf(
                _bone_factory(value, scale=self._scale))
        self._bones[self._number_of_bones].set_shape(self._bone_images[value])
        self._bones[self._number_of_bones].inval()
        self._number = self._number * 10 + value

    def _mouse_move_cb(self, win, event):
        ''' Determine which row we are in and then calculate the product. '''
        win.grab_focus()
        x, y = map(int, event.get_coords())
        factor = int(y / self._bone_width)  # The row determines a factor

        if self._number == 0 or factor == 0:
            self._status.set_label('')
            self._circles[0].move((0, -100))
            self._circles[1].move((0, -100))
            for number in range(self._max_bones - 1):
                self._ovals[number].move((0, -100))
        else:
            c0dx = int(4 * self._scale)
            c0dy = int(12 * self._scale)
            c1dx = int(44 * self._scale)
            c1dy = int(47 * self._scale)
            odx = int(42 * self._scale)
            ody = int(2 * self._scale)
            self._circles[0].move((self._bone_width + c0dx,
                                   factor * self._bone_width + c0dy))
            self._circles[1].move((
                    self._number_of_bones * self._bone_width + c1dx,
                    factor * self._bone_width + c1dy))
            for number in range(self._number_of_bones - 1):
                self._ovals[number].move(((number + 1) * self._bone_width + odx,
                                          factor * self._bone_width + ody))
            self._status.set_label('%d × %d = %d' % (
                    factor + 1, self._number, (factor + 1) * self._number))
        return True

    def _key_press_cb(self, win, event):
        ''' TODO: Add bones by typing numbers '''
        return True

    def __draw_cb(self, canvas, cr):
        self._sprites.redraw_sprites(cr=cr)

    def do_expose_event(self, event):
        ''' Handle the expose-event by drawing '''
        # Restrict Cairo to the exposed area
        cr = self._canvas.window.cairo_create()
        cr.rectangle(event.area.x, event.area.y,
                event.area.width, event.area.height)
        cr.clip()
        # Refresh sprite list
        self._sprites.redraw_sprites(cr=cr)

    def _destroy_cb(self, win, event):
        Gtk.main_quit()

    def _restore(self):
        ''' Try to restore previous state. '''
        if 'number' in self.metadata and self.metadata['number'] != '0':
            for digit in range(len(self.metadata['number'])):
                self._number_cb(button=None,
                                value=int(self.metadata['number'][digit]))

    def write_file(self, file_path):
        ''' Write the status to the Journal. '''
        if not hasattr(self, '_number'):
            return
        self.metadata['number'] = str(self._number)
