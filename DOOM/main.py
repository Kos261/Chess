from wad_data import WADData
from settings import *
from map_renderer import MapRenderer
import pygame as pg
import sys
from player import Player
from bsp import BSP


class DoomEngine:
    def __init__(self, wad_path = "WAD_Files/DOOM1.WAD") -> None:
        self.wad_path = wad_path
        self.screen = pg.display.set_mode(WIN_RES)
        self.clock = pg.time.Clock()
        self.running = True
        self.dt = 1/60
        self.on_init()  #Header 12 bytes: 4 ASCII for Wad type, 4 bytes for number of lumps, 
                        #4 for an integer holding pointer to directory
        


    def on_init(self):
        self.wad_data = WADData(self, map_name="E1M1")
        self.map_renderer = MapRenderer(self)
        self.player = Player(self)
        self.bsp = BSP(self)


    def update(self):
        self.player.update()
        self.bsp.update()
        self.dt = self.clock.tick()
        pg.display.set_caption(f"{self.clock.get_fps()}")

    def draw(self):
        self.screen.fill('black')
        self.map_renderer.draw()
        pg.display.flip()

    def check_events(self):
        for e in pg.event.get():
            if e.type == pg.QUIT:
                self.running = False

    def run(self):
        while self.running:
            self.check_events()
            self.update()
            self.draw()
        pg.quit()
        sys.exit()




if __name__ == "__main__":
    doom = DoomEngine()
    doom.run()