from tkinter import BooleanVar, IntVar, Misc, OptionMenu, Scale, StringVar, Tk, Button, Entry, Label, HORIZONTAL
from tkinter.ttk import Checkbutton, Notebook, Frame, Separator

from mpegh_ui import MPEGHUIManager
from player import Player
from scene.props import Prop, ProminenceLevelProp
from scene.scene_reader import AudioElementSwitch, AudioSceneConfig


class PropUI:
    def __init__(self, window: Misc, prop: Prop):
        self.prop = prop
        self.window = window

    def grid(self, row: int, column: int):
        kw: dict[str, float | None] = {
            "from_": self.prop.min,
            "to": self.prop.max,
        }
        n_kw = {k: v for k,v in kw.items() if v is not None}
        w = Scale(self.window, **n_kw, orient=HORIZONTAL) # type: ignore
        w.set(self.prop.val)
        w.grid(row=row, column=column)

MAIN_PARAGRAPH_COL = 0
CONTENT_LABEL_COL = 1
CONTENT_COL_PREFIX = 2
CONTENT_COL = 3
CONTENT_COL_sufix = 4
class Interface:
    def __init__(self, scene: AudioSceneConfig, player: Player, ui_manager: MPEGHUIManager) -> None:
        self.scene = scene
        self.player = player
        self.ui_manager = ui_manager

        self.window = Tk()
        self.window.title("MPEG-H 3D Audio Player")
        self.window.resizable(None, None)

        tab_control = Notebook(self.window)
        lang = "eng"

        self._vars = []

        for preset in scene.presets.values():
            tab = Frame(tab_control)
            tab_control.add(tab, text=preset.get_desc(lang))
            row = 0
            for audio in list(preset.audio_element_switch.values()) + list(preset.audio_elements.values()):
                Label(tab, text=audio.get_desc(lang)).grid(row=row, column=MAIN_PARAGRAPH_COL)

                if audio.muting is not None:
                    chk_state = BooleanVar(tab)
                    self._vars.append(chk_state)
                    if audio.muting.val is not None:
                        chk_state.set(audio.muting.val)
                    check = Checkbutton(tab, text=audio.muting.name, variable=chk_state, onvalue=False, offvalue=True)
                    check.grid(row=row, column=CONTENT_LABEL_COL)
                    check.setvar()
                    row += 1

                for slider_prop in audio.slider_props():
                    Label(tab, text=slider_prop.name).grid(row=row, column=CONTENT_LABEL_COL)
                    PropUI(tab, slider_prop).grid(row=row, column=CONTENT_COL)
                    row += 1

                if isinstance(audio, AudioElementSwitch):
                    audios_options = [x.get_desc(lang) for x in audio.audio_elements.values()]
                    if audios_options != []:
                        value_inside = StringVar(tab)
                        value_inside.set(audios_options[0])
                        OptionMenu(tab, value_inside, *audios_options).grid(row=row, column=CONTENT_COL)
                        row += 1
                row += 1

                Separator(tab, orient='horizontal').grid(row=row, columnspan=4, sticky="ew")
                row += 1

        tab_control.pack()

    def run(self):
        self.window.mainloop()