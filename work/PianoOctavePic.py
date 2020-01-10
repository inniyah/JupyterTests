#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cairo
import math

class PianoOctavePic:
    def __init__(self, width, height, num_octaves=5):
        self.ctx = None
        self.width = width
        self.height = height
        self.num_octaves = num_octaves

    def white_key(self, pos):
        self.ctx.set_line_width(0.01)
        self.ctx.set_source_rgb(0.0, 0.0, 0.0)
        self.ctx.rectangle(pos, 0.0, 0.2, 1.0)
        self.ctx.stroke()
        self.ctx.set_source_rgb(1.0, 1.0, 1.0)
        self.ctx.rectangle(pos, 0.0, 0.2, 1.0)
        self.ctx.fill()

    def black_key(self, pos):
        self.ctx.set_line_width(0.01)
        self.ctx.set_source_rgb(0.0, 0.0, 0.0)
        self.ctx.rectangle(pos + 0.045, 0.0 , 0.1 , 0.6)
        self.ctx.fill()
        self.ctx.stroke()

    def draw_octave(self, ctx, pos=0):
        self.white_key(pos + .1)
        self.white_key(pos + .3)
        self.white_key(pos + .5)
        self.white_key(pos + .7)
        self.white_key(pos + .9)
        self.white_key(pos + 1.1)
        self.white_key(pos + 1.3)

        self.black_key(pos + .2)
        self.black_key(pos + .4)
        self.black_key(pos + .8)
        self.black_key(pos + 1.0)
        self.black_key(pos + 1.2)

    def draw_pic(self, ctx):
        self.ctx = ctx

        self.ctx.set_source_rgb(0.5, 0.5, 0.5)
        self.ctx.rectangle(0, 0, self.width, self.height)
        self.ctx.fill()

        self.ctx.translate(10, 20)
        self.ctx.scale((self.width - 40) / (self.num_octaves * 1.4), (self.height - 40) / 1.0)
        for n in range(self.num_octaves):
            self.draw_octave(ctx, 1.4 * n)

def main_gtk():
    import gi
    gi.require_version("Gtk", "3.0")
    from gi.repository import Gtk

    pic = PianoOctavePic(width=600, height=150, num_octaves=5)

    def draw(da, ctx):
        pic.draw_pic(ctx)

    win = Gtk.Window(title="Music Pic")
    win.connect('destroy', lambda w: Gtk.main_quit())
    win.set_default_size(pic.width, pic.height)

    drawingarea = Gtk.DrawingArea()
    win.add(drawingarea)
    drawingarea.connect('draw', draw)

    win.show_all()
    Gtk.main()

def main_pyglet():
    import ctypes
    import time

    from pyglet import app, clock, font, gl, image, window

    from MusicDefs import MusicDefs

    pic = PianoOctavePic(width=600, height=150, num_octaves=5)
    win = window.Window(width=pic.width, height=pic.height)

    # create data shared by ImageSurface and Texture
    data = (ctypes.c_ubyte * (pic.width * pic.height * 4))()
    stride = pic.width * 4
    surface = cairo.ImageSurface.create_for_data (data, cairo.FORMAT_ARGB32, pic.width, pic.height, stride); 
    texture = image.Texture.create_for_size(gl.GL_TEXTURE_2D, pic.width * pic.height, gl.GL_RGBA)

    def update_surface(dt, surface):
        ctx = cairo.Context(surface)
        pic.draw_pic(ctx)

    @window.event
    def on_draw():
        window.clear()

        gl.glEnable(gl.GL_TEXTURE_2D)

        gl.glBindTexture(gl.GL_TEXTURE_2D, texture.id)
        gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, pic.width, pic.height, 0, gl.GL_BGRA, gl.GL_UNSIGNED_BYTE, data)

        gl.glBegin(gl.GL_QUADS)
        gl.glTexCoord2f(0.0, 1.0)
        gl.glVertex2i(0, 0)
        gl.glTexCoord2f(1.0, 1.0)
        gl.glVertex2i(pic.width, 0)
        gl.glTexCoord2f(1.0, 0.0)
        gl.glVertex2i(pic.width, pic.height)
        gl.glTexCoord2f(0.0, 0.0)
        gl.glVertex2i(0, pic.height)
        gl.glEnd()

        #print('FPS: %f' % clock.get_fps())

    clock.schedule_interval(update_surface, 1/120.0, surface)
    app.run()

if __name__ == '__main__':
    main_gtk()
