# -*- coding: utf-8 -*-
#Copyright (c) 2011 Walter Bender

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.

import gtk
import gobject
import os

import sugar
from sugar.activity import activity
from sugar import profile
try:
    from sugar.graphics.toolbarbox import ToolbarBox
    _have_toolbox = True
except ImportError:
    _have_toolbox = False

if _have_toolbox:
    from sugar.bundle.activitybundle import ActivityBundle
    from sugar.activity.widgets import ActivityToolbarButton
    from sugar.activity.widgets import StopButton
    from sugar.graphics.toolbarbox import ToolbarButton

from sugar.graphics.toolbutton import ToolButton
from sugar.graphics.menuitem import MenuItem

from sprites import Sprites, Sprite

from gettext import gettext as _

try:
    from sugar.graphics import style
    GRID_CELL_SIZE = style.GRID_CELL_SIZE
except ImportError:
    GRID_CELL_SIZE = 0

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
	  style="fill:none;stroke:#000000;stroke-width:%f;stroke-linecap:square;stroke-linejoin:round;stroke-miterlimit:%f;stroke-opacity:1;stroke-dasharray:none" />\
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
	  style="fill:none;stroke:#000000;stroke-width:%f;stroke-linecap:square;stroke-linejoin:round;stroke-miterlimit:%f;stroke-opacity:1;stroke-dasharray:none" />\
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
             (y + 1) * scale, 2 * scale, 4 * scale, 40 * scale, 12 * scale,
             (y + 51) * scale, a, 40 * scale, 52 * scale, (y + 81) * scale, b)


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
    pl = gtk.gdk.PixbufLoader('svg')
    pl.write(svg_string)
    pl.close()
    pixbuf = pl.get_pixbuf()
    return pixbuf


def _load_svg_from_file(file_path, width, height):
    '''Create a pixbuf from SVG in a file. '''
    return gtk.gdk.pixbuf_new_from_file_at_size(file_path, width, height)


def _button_factory(icon_name, tooltip, callback, toolbar, cb_arg=None,
                    accelerator=None):
    '''Factory for making toolbar buttons'''
    my_button = ToolButton(icon_name)
    my_button.set_tooltip(tooltip)
    my_button.props.sensitive = True
    if accelerator is not None:
        my_button.props.accelerator = accelerator
    if cb_arg is not None:
        my_button.connect('clicked', callback, cb_arg)
    else:
        my_button.connect('clicked', callback)
    if hasattr(toolbar, 'insert'):  # the main toolbar
        toolbar.insert(my_button, -1)
    else:  # or a secondary toolbar
        toolbar.props.page.insert(my_button, -1)
    my_button.show()
    return my_button


def _label_factory(label, toolbar):
    ''' Factory for adding a label to a toolbar '''
    my_label = gtk.Label(label)
    my_label.set_line_wrap(True)
    my_label.show()
    toolitem = gtk.ToolItem()
    toolitem.add(my_label)
    toolbar.insert(toolitem, -1)
    toolitem.show()
    return my_label


def _separator_factory(toolbar, visible=True, expand=False):
    ''' Factory for adding a separator to a toolbar '''
    separator = gtk.SeparatorToolItem()
    separator.props.draw = visible
    separator.set_expand(expand)
    toolbar.insert(separator, -1)
    separator.show()


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
        self._circles = [None, None]
        self._ovals = []

        self._setup_toolbars(_have_toolbox)
        self._setup_canvas()
        self._setup_workspace()

    def _setup_canvas(self):
        ''' Create a canvas '''
        self._canvas = gtk.DrawingArea()
        self._canvas.set_size_request(gtk.gdk.screen_width(),
                                      gtk.gdk.screen_height())
        self.set_canvas(self._canvas)
        self._canvas.show()
        self.show_all()

        self._canvas.set_flags(gtk.CAN_FOCUS)
        self._canvas.add_events(gtk.gdk.BUTTON_PRESS_MASK)
        self._canvas.add_events(gtk.gdk.BUTTON_RELEASE_MASK)
        self._canvas.add_events(gtk.gdk.POINTER_MOTION_MASK)
        self._canvas.connect("expose-event", self._expose_cb)
        self._canvas.connect("motion-notify-event", self._mouse_move_cb)
        # self._canvas.connect("key_press_event", self._key_press_cb)

    def _setup_workspace(self):
        ''' Add the bones. '''
        self._width = gtk.gdk.screen_width()
        self._height = int(gtk.gdk.screen_height() - (GRID_CELL_SIZE * 2))
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

    def _setup_toolbars(self, have_toolbox):
        ''' Setup the toolbars. '''

        self.max_participants = 1  # no sharing

        if have_toolbox:
            toolbox = ToolbarBox()

            # Activity toolbar
            activity_button = ActivityToolbarButton(self)

            toolbox.toolbar.insert(activity_button, 0)
            activity_button.show()

            self._bones_toolbar = gtk.Toolbar()
            self._bones_toolbar_button = ToolbarButton(label=_('Select a bone'),
                                                       page=self._bones_toolbar,
                                                       icon_name='bones')

            self._bones_toolbar_button.show()
            toolbox.toolbar.insert(self._bones_toolbar_button, -1)
            self.set_toolbar_box(toolbox)
            toolbox.show()
            self.toolbar = toolbox.toolbar

        else:
            # Use pre-0.86 toolbar design
            self._bones_toolbar = gtk.Toolbar()
            self.toolbar = gtk.Toolbar()
            toolbox = activity.ActivityToolbox(self)
            self.set_toolbox(toolbox)
            toolbox.add_toolbar(_('Bones'), self._bones_toolbar)
            toolbox.add_toolbar(_('Results'), self.toolbar)
            toolbox.show()
            toolbox.set_current_toolbar(1)

        _separator_factory(self.toolbar)

        self._new_calc_button = _button_factory(
            'new-game', _('Clear'), self._new_calc_cb, self.toolbar)

        self._status = _label_factory('', self.toolbar)

        _button_factory('number-0', _('zero'), self._number_cb,
                        self._bones_toolbar, cb_arg=0)

        _button_factory('number-1', _('one'), self._number_cb,
                        self._bones_toolbar, cb_arg=1)

        _button_factory('number-2', _('two'), self._number_cb,
                        self._bones_toolbar, cb_arg=2)

        _button_factory('number-3', _('three'), self._number_cb,
                        self._bones_toolbar, cb_arg=3)

        _button_factory('number-4', _('four'), self._number_cb,
                        self._bones_toolbar, cb_arg=4)

        _button_factory('number-5', _('five'), self._number_cb,
                        self._bones_toolbar, cb_arg=5)

        _button_factory('number-6', _('six'), self._number_cb,
                        self._bones_toolbar, cb_arg=6)

        _button_factory('number-7', _('seven'), self._number_cb,
                        self._bones_toolbar, cb_arg=7)

        _button_factory('number-8', _('eight'), self._number_cb,
                        self._bones_toolbar, cb_arg=8)

        _button_factory('number-9', _('nine'), self._number_cb,
                        self._bones_toolbar, cb_arg=9)

        if _have_toolbox:
            _separator_factory(toolbox.toolbar, False, True)

            stop_button = StopButton(self)
            stop_button.props.accelerator = '<Ctrl>q'
            toolbox.toolbar.insert(stop_button, -1)
            stop_button.show()
            self._bones_toolbar_button.set_expanded(True)

    def _new_calc_cb(self, button=None):
        ''' Start a new calculation. '''
        for bone in range(self._max_bones):
            self._bones[bone].images[0] = self._blank_image
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
        self._bones[self._number_of_bones].images[0] = self._bone_images[value]
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
            for number in range(self._max_bones):
                self._ovals[number].move((0, -100))
        else:
            c0dx = int(4 * self._scale)
            c0dy = int(12 * self._scale)
            c1dx = int(44 * self._scale)
            c1dy = int(42 * self._scale)
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

    def _expose_cb(self, win, event):
        self._sprites.redraw_sprites()
        return True

    def _destroy_cb(self, win, event):
        gtk.main_quit()
