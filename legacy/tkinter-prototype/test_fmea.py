import os
import sys
import pathlib
from time import time

from kivymd.uix.screen import MDScreen
from kivymd.uix.widget import MDWidget
from kivymd.uix.toolbar import MDTopAppBar
from kivy.uix.screenmanager import ScreenManager
from kivymd.app import MDApp
from kivymd.uix.tab import MDTabsBase
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.app import Builder
import sqlite3
import pandas as pd
#class fmea_db(sqlite3):
#    def __init__(self):
#        pass

#    def build(self):
#        pass

#    def connections(self):
#        pass
#    pass

#class FMEAstuff(MDWidget):
#    def somebutton():
#        pass
#    pass


class Tab(MDFloatLayout, MDTabsBase):
    ''''''

class FMEATableScreen(MDScreen):
    pass

class FMEATabsScreen(MDScreen):
    pass



class FMEAApp(MDApp):
    title = "Open FMEA"
    sm = ScreenManager()
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Amber"
        return Builder.load_file('test_fmea.kv')


FMEAApp().run()