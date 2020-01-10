#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cairo
import math
import queue

SCALE_MAJOR_DIATONIC = (1<<0) + (1<<2) + (1<<4) + (1<<6) + (1<<7) + (1<<9) + (1<<11)
SCALE_MAJOR_MELODIC  = (1<<0) + (1<<2) + (1<<4) + (1<<6) + (1<<7) + (1<<9) + (1<<10)

#NOTE_NAMES = ['C', 'Db/C#', 'D', 'Eb/D#', 'E', 'F', 'Gb/F#', 'G', 'Ab/G#', 'A', 'Bb/A#', 'B']
NOTE_NAMES = ['I', 'ii', 'II', 'iii', 'III', 'IV', 'v', 'V', 'vi', 'VI', 'vii', 'VII']

class HexagonalLayoutPic:
    def __init__(self, D, scale=SCALE_MAJOR_DIATONIC, tonic=0, h = 4):
        self.ctx = None

        self.notes = [(scale & 1<<(r%12) != 0) for r in range(tonic*7, tonic*7 + 12)]

        # diameter of hexagon in pixels
        self.D = D

        self.vnum = h * 2 + 1
        self.hnum = 13

        # vectorial distance to next hexagon in row
        self.shift_x = (math.sqrt(3)*D/2., 0)

        # vectorial distance to hexagon in next row
        self.shift_y = (math.sqrt(3)*D/4., 3*D/4.)

        # width of surface plus some border in pixels
        self.width = int((self.hnum + 2) * math.sqrt(3)*D/2. + 3*D/4.) + 1

        # height of surface plus some border in pixels
        self.height = int(self.vnum * 3*D/4. + 2*D) + 1

        self.hexagon_points = (
            ( math.sqrt(3)*D/4.,  D/4.),
            (                0.,  D/2.),
            (-math.sqrt(3)*D/4.,  D/4.),
            (-math.sqrt(3)*D/4., -D/4.),
            (                0., -D/2.),
            ( math.sqrt(3)*D/4., -D/4.)
        )

        self.selected_notes = {}

        notes_queue = queue.Queue()
        notes_queue.put((0, 0, 0))
        while not notes_queue.empty():
            try:
                n, x, y = notes_queue.get()
                #n, x, y = notes_queue.get(timeout=wait_timeout)
                #n, x, y = notes_queue.get_nowait()
            except queue.Empty:
                continue
            #print(f"{n} ({x, y})")
            self.selected_notes[(x, y)] = f"{NOTE_NAMES[n]} ({n})"
            u = 2*x-y
            if u < 5:
                if self.notes[(n+4)%12] and y>0:
                    notes_queue.put(((n+4)%12, x, y-1))
                elif self.notes[(n+3)%12]:
                    notes_queue.put(((n+3)%12, x+1, y+1))
                elif self.notes[(n+4)%12]:
                    notes_queue.put(((n+4)%12, x, y-1))

        notes_queue = queue.Queue()
        notes_queue.put((0, 0, 0))
        while not notes_queue.empty():
            try:
                n, x, y = notes_queue.get()
                #n, x, y = notes_queue.get(timeout=wait_timeout)
                #n, x, y = notes_queue.get_nowait()
            except queue.Empty:
                continue
            #print(f"{n} ({x, y})")
            self.selected_notes[(x, y)] = f"{NOTE_NAMES[n]} ({n})"
            u = 2*x-y
            if u > -3:
                if self.notes[(n+9)%12] and y>0:
                    notes_queue.put(((n+9)%12, x-1, y-1))
                elif self.notes[(n+8)%12]:
                    notes_queue.put(((n+8)%12, x, y+1))
                elif self.notes[(n+9)%12]:
                    notes_queue.put(((n+9)%12, x-1, y-1))

    def check_chord(self, chord, note=(0,0,0)):
        base_note, base_x, base_y = note
        notes_in_scale = True
        for inc_note, inc_x, inc_y in chord:
            note_value = (base_note + self.get_note_from_coords(base_x + inc_x, base_y + inc_y) % 12)
            if not self.notes[note_value]:
                notes_in_scale = False
            #print(f"{inc_note}, {inc_x}, {inc_y}: {note_value} -> {self.notes[note_value]}")
        return notes_in_scale

    def get_note_from_coords(self, x, y):
            return (int(x * 7 - y * 4) % 12)

    def draw_hexagon(self, note, color, label, sublabel="", bold=False):
        self.ctx.save()

        self.ctx.move_to(self.hexagon_points[0][0], self.hexagon_points[0][1])
        for pair in self.hexagon_points:
            self.ctx.line_to(pair[0], pair[1])
        self.ctx.close_path()

        self.ctx.set_source_rgb(*color)
        self.ctx.fill()

        self.ctx.move_to(self.hexagon_points[0][0], self.hexagon_points[0][1])
        for pair in self.hexagon_points:
            self.ctx.line_to(pair[0], pair[1])
        self.ctx.close_path()

        self.ctx.set_source_rgb(0, 0, 0)
        self.ctx.set_line_width(0.5)
        self.ctx.stroke()

        self.ctx.set_source_rgb(0.3, 0.3, 0.3)
        self.ctx.arc(0, 0, self.D * .35, 0, 2. * math.pi)
        self.ctx.set_line_width(1.0)
        self.ctx.stroke()

        for n in range(0,12):
            angle = 2/12 * math.pi * n
            rad_i = self.D * .32
            rad_o = self.D * .35
            self.ctx.move_to(rad_i * math.sin(angle), -rad_i * math.cos(angle))
            self.ctx.line_to(rad_o * math.sin(angle), -rad_o * math.cos(angle))
        self.ctx.stroke()

        self.ctx.set_source_rgb(0., 0., 0.)
        angle = 2/12 * math.pi * ((note*7)%12)
        self.ctx.arc(rad_o * math.sin(angle), -rad_o * math.cos(angle), self.D * .03, 0, 2. * math.pi)
        self.ctx.fill()

        self.ctx.set_source_rgb(0.1, 0.1, 0.1)
        self.ctx.select_font_face("monospace", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        self.ctx.set_font_size(12)
        text_extents = self.ctx.text_extents(str(label))
        self.ctx.move_to(-text_extents.width/2., text_extents.height/2.)
        self.ctx.show_text(str(label))

        text_extents = self.ctx.text_extents(str(sublabel))
        self.ctx.move_to(-text_extents.width/2., text_extents.height*3.5/2.)
        self.ctx.set_font_size(10)
        self.ctx.show_text(str(sublabel))

        self.ctx.restore()

    def draw_circle_of_fifths(self):
        self.ctx.save()

        self.ctx.set_source_rgb(1, 0, 0)
        self.ctx.set_line_width(0.06)
        self.ctx.arc(0, 0, self.D * .4, 0, 2. * math.pi)

        self.ctx.set_line_width(0.04)
        self.ctx.stroke()

        self.ctx.restore()

    def compass_to_rgb(self, hue, saturation=1., value=1.):
        h = float(hue)
        s = float(saturation)
        v = float(value)
        h60 = h / 60.0
        h60f = math.floor(h60)
        hi = int(h60f) % 6
        f = h60 - h60f
        p = v * (1 - s)
        q = v * (1 - f * s)
        t = v * (1 - (1 - f) * s)
        r, g, b = 0, 0, 0
        if hi == 0: r, g, b = v, t, p
        elif hi == 1: r, g, b = q, v, p
        elif hi == 2: r, g, b = p, v, t
        elif hi == 3: r, g, b = p, q, v
        elif hi == 4: r, g, b = t, p, v
        elif hi == 5: r, g, b = v, p, q
        return r, g, b

    def get_color_from_note(self, note, saturation=1., value=1.):
        if note == -1:
            return (0.9, 0.9, 0.9)
        return self.compass_to_rgb(360. * ((note*7)%12)/12., saturation, value)

    def draw_pic(self, ctx):
        self.ctx = ctx

        self.ctx.set_source_rgb(1, 1, 1)
        self.ctx.rectangle(0, 0, self.width, self.height)
        self.ctx.fill()

        self.ctx.translate(2. * math.sqrt(3) * self.D/4., self.D)

        ix_offset = int(self.hnum//2)
        iy_offset = int(self.vnum//2)

        for vpos in range(self.vnum):
            hexagons_in_line = self.hnum + (vpos%2)

            for hpos in range(hexagons_in_line):
                iy = int(vpos) - iy_offset
                ix = int(hpos) - ix_offset + iy//2
                n = self.get_note_from_coords(ix, iy)

                self.ctx.translate(self.shift_x[0], self.shift_x[1])

                try:
                    color = self.get_color_from_note(n, 1.0)
                    label = self.selected_notes[(ix, iy)]
                except KeyError:
                    label = f"{NOTE_NAMES[n]} ({n})"
                    if self.notes[n]:
                        color = self.get_color_from_note(n, 0.15)
                    else:
                        color = self.get_color_from_note(n, 0.02)

                self.draw_hexagon(n, color, label, f"({ix}, {iy})")
                self.draw_circle_of_fifths()

            self.ctx.translate(-hexagons_in_line * self.shift_x[0], -hexagons_in_line * self.shift_x[1])
            self.ctx.translate((2*(vpos%2) - 1) * self.shift_y[0], self.shift_y[1])

def main_gtk():
    import gi
    gi.require_version("Gtk", "3.0")
    from gi.repository import Gtk

    pic = HexagonalLayoutPic(D=100, scale=SCALE_MAJOR_DIATONIC, tonic=1, h=4)

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

    pic = HexagonalLayoutPic(D=100, scale=SCALE_MAJOR_DIATONIC, tonic=1, h=4)
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
