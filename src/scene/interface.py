from collections import defaultdict
from functools import partial
from pathlib import Path
from tkinter import BooleanVar, IntVar, Misc, OptionMenu, Scale, StringVar, Tk, Button, Label, HORIZONTAL, Menu, filedialog
from tkinter.ttk import Checkbutton, Notebook, Frame, Separator

from config import CONFIG_PATH, Config
from mpegh_lib.mpegh_ui import ActionEvent, MPEGHUIManager
from player import Player
from scene.props import Prop, ProminenceLevelProp, MutingProp, AzimuthProp, ElevationProp
from scene.scene_reader import AudioElement, AudioElementSwitch, AudioSceneConfig, Preset
from utils import PathPointer


prop_to_event = {
    ProminenceLevelProp: ActionEvent.audio_prominance_prop,
    MutingProp: ActionEvent.audio_muting_prop,
    AzimuthProp: ActionEvent.audio_azimuth_prop,
    ElevationProp: ActionEvent.audio_elevation_prop,
}
class PropUI:
    def __init__(self, master: Misc, prop: Prop | ProminenceLevelProp | MutingProp | AzimuthProp | ElevationProp, ui_manager: MPEGHUIManager, scene: AudioSceneConfig, player: Player):
        self.prop = prop
        self.master = master
        self.ui_manager = ui_manager
        self.scene = scene
        self.player = player
        self.var = IntVar()

    def update(self, event):
        ac = None
        if isinstance(self.prop, ProminenceLevelProp):
            ac = ActionEvent.audio_prominance_prop(self.scene.uuid, self.prop.audio_id, value=self.var.get(), is_switch=self.prop.is_switch)
        if isinstance(self.prop, MutingProp):
            ac = ActionEvent.audio_muting_prop(self.scene.uuid, self.prop.audio_id, is_muted=bool(self.var.get()), is_switch=self.prop.is_switch)
        if isinstance(self.prop, AzimuthProp):
            ac = ActionEvent.audio_azimuth_prop(self.scene.uuid, self.prop.audio_id, value=self.var.get(), is_switch=self.prop.is_switch)
        if isinstance(self.prop, ElevationProp):
            ac = ActionEvent.audio_elevation_prop(self.scene.uuid, self.prop.audio_id, value=self.var.get(), is_switch=self.prop.is_switch)
        if ac is None:
            return
        self.ui_manager.add_event_action(ac)
        self.ui_manager.apply_scene_state()
        self.re_fill_buffer(thread_it=False)

    def grid(self, row: int, column: int):
        kw: dict[str, float | None] = {
            "from_": self.prop.min,
            "to": self.prop.max,
        }
        n_kw = {k: v for k,v in kw.items() if v is not None}
        w = Scale(self.master, **n_kw, variable=self.var, orient=HORIZONTAL, command=self.update) # type: ignore
        w.set(self.prop.val)
        w.grid(row=row, column=column)

MAIN_PARAGRAPH_COL = 0
CONTENT_LABEL_COL = 1
CONTENT_COL_PREFIX = 2
CONTENT_COL = 3
CONTENT_COL_SUFIX = 4

def pause_or_resume(resume_fn, pause_fn, is_paused, bttn):
    if is_paused:
        bttn.config(text="Pause")
        pause_fn()
    else:
        bttn.config(text="Play")
        resume_fn()
def reset(reset_fn, pause_bttn):
    pause_bttn.config(text="Play")
    reset_fn()

class Interface:
    def __init__(self, scene: AudioSceneConfig | None, player: Player, ui_manager: MPEGHUIManager, input_file: PathPointer, config: Config) -> None:
        self.scene = scene
        self.player = player
        self.ui_manager = ui_manager
        self.input_file = input_file
        self.config = config

        self.window = Tk()
        self.window.title("MPEG-H 3D Audio Player")
        self.window.resizable(False, False)

        self.lang = "eng"

        menu = Menu(self.window)

        def browseFiles():
            filename = filedialog.askopenfilename(
                initialdir = "./audio",
                title = "Select a File",
                filetypes = (("MP4 files","*.mp4*"),("all files","*.*"))
            )
            if filename != "":
                self.set_file(filename)

        file = Menu(menu, tearoff=0)
        file.add_command(label='Open', command=browseFiles)
        menu.add_cascade(label='File', menu=file)

        def change_drc(drc: int):
            self.config.alter_config(drc=drc)
        def change_speaker(target_layout: int):
            self.config.alter_config(target_layout=target_layout)
        def change_drc_target_loudness(drc_target_loudness: int):
            self.config.alter_config(drc_target_loudness=drc_target_loudness)
        def change_scale_factor(scale_factor: int):
            self.config.alter_config(scale_factor=scale_factor)
        def change_album(album_mode: bool):
            self.config.alter_config(album_mode=album_mode)

        def change_lang(lang: str):
            self.lang = lang
            self.ui_manager.add_event_action(ActionEvent.select_language(lang))
            self.ui_manager.apply_scene_state()
            self.re_fill_buffer(thread_it=False)

        language = Menu(menu, tearoff=0)
        language.add_command(label='Português', command=lambda: change_lang("por"))
        language.add_command(label='English', command=lambda: change_lang("eng"))
        language.add_command(label='Deutsch', command=lambda: change_lang("ger"))
        language.add_command(label='Español', command=lambda: change_lang("spa"))
        menu.add_cascade(label='Language', menu=language)
        self.window.config(menu=menu)
        self.main_frame: None | Frame = None

        speakers = Menu(menu, tearoff=0)
        speakers.add_command(label='Mono', command=lambda: change_speaker(1))
        speakers.add_command(label='Stereo', command=lambda: change_speaker(2))
        speakers.add_command(label='5.1', command=lambda: change_speaker(6))
        speakers.add_command(label='7.1', command=lambda: change_speaker(7))
        speakers.add_command(label='7.1+4', command=lambda: change_speaker(19))
        menu.add_cascade(label='Speakers', menu=speakers)

        album_mode = Menu(menu, tearoff=0)
        album_mode.add_command(label='Off', command=lambda: change_album(False))
        album_mode.add_command(label='On', command=lambda: change_album(True))
        menu.add_cascade(label='Album Mode', menu=album_mode)

        drc = Menu(menu, tearoff=0)
        drc.add_command(label='Off', command=lambda: change_drc(-1))
        drc.add_command(label='None', command=lambda: change_drc(0))
        drc.add_command(label='Night', command=lambda: change_drc(1))
        drc.add_command(label='Noisy', command=lambda: change_drc(2))
        drc.add_command(label='Limited', command=lambda: change_drc(3))
        drc.add_command(label='LowLevel', command=lambda: change_drc(4))
        drc.add_command(label='Dialog', command=lambda: change_drc(5))
        drc.add_command(label='General', command=lambda: change_drc(6))
        menu.add_cascade(label='DRC', menu=drc)

    def re_fill_buffer(self, thread_it: bool = False):
        self.player.queue_action(self.player.re_fill_buffer, kwargs={"thread_it": thread_it})
    def reset_player(self):
        self.player.queue_action(self.player.reset)

    def set_file(self, filename: str):
        self.input_file.path = Path(filename)
        duration = self.ui_manager.apply_scene_state(str(CONFIG_PATH / "scene_state.xml"))
        self.config.duration_in_seconds = duration
        self.scene = AudioSceneConfig.start_parsing("tmp/config/scene_state.xml")
        self.build()    

    def build(self):
        if self.scene is None:
            return

        if self.main_frame is not None:
            self.main_frame.destroy()

        self.main_frame = Frame(self.window)
        self.main_frame.pack()

        self.tab_control = Notebook(self.main_frame)
        self.tab_control.grid(row=0, column=0, columnspan=3)

        preset_tab_cache: dict[str, Preset] = {}
        def handle_tab_changed(event):
            tab_name = event.widget.tab(event.widget.select(), "text")
            new_preset = preset_tab_cache[tab_name]
            self.ui_manager.add_event_action(ActionEvent.select_preset(self.scene.uuid, new_preset.id))
            self.ui_manager.apply_scene_state()
            self.re_fill_buffer(thread_it=False)

        element_switch_cache: defaultdict[int, dict[str, AudioElement]] = defaultdict(dict)
        def handle_element_switch(event, element_switch: AudioElementSwitch):
            self.ui_manager.add_event_action(
                ActionEvent.element_switch(
                    self.scene.uuid,
                    swith_group_id=element_switch.id,
                    swith_audio_id=element_switch_cache[element_switch.id][event].id
                )
            )
            self.ui_manager.apply_scene_state()
            self.re_fill_buffer(thread_it=False)

        self.tab_control.bind("<<NotebookTabChanged>>", handle_tab_changed)

        self.player.frame_slider = IntVar()
        pause_bttn = Button(
            self.main_frame,
            text=["Pause", "Play"][self.player.is_paused],
            command=lambda: pause_or_resume(self.player.pause, self.player.resume, self.player.is_paused, pause_bttn)
        )
        pause_bttn.grid(row=1, column=0)
        Button(self.main_frame, text="Reset", command=lambda: reset(self.reset_player, pause_bttn)).grid(row=1, column=1)
        Scale(self.main_frame, orient=HORIZONTAL, variable=self.player.frame_slider, to=self.player.config.duration_in_seconds).grid(row=1, column=2)

        self._vars: list[BooleanVar] = []

        for preset in self.scene.presets.values():
            tab = Frame(self.tab_control)
            self.tab_control.add(tab, text=preset.get_desc(self.lang))
            preset_tab_cache[preset.get_desc(self.lang)] = preset
            row = 0
            for audio in list(preset.audio_element_switch.values()) + list(preset.audio_elements.values()):
                Label(tab, text=audio.get_desc(self.lang)).grid(row=row, column=MAIN_PARAGRAPH_COL)

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
                    PropUI(tab, slider_prop, ui_manager=self.ui_manager, scene=self.scene, player=self.player).grid(row=row, column=CONTENT_COL)
                    row += 1

                if isinstance(audio, AudioElementSwitch):
                    audios_options = []
                    for audio_element_item in audio.audio_elements.values():
                        txt = audio_element_item.get_desc(self.lang)
                        audios_options.append(txt)
                        element_switch_cache[audio.id][txt] = audio_element_item

                    if audios_options != []:
                        value_inside = StringVar(tab)
                        value_inside.set(audios_options[0])
                        OptionMenu(tab, value_inside, *audios_options, command=partial(handle_element_switch, element_switch=audio)).grid(row=row, column=CONTENT_COL)
                        row += 1
                row += 1

                Separator(tab, orient='horizontal').grid(row=row, columnspan=4, sticky="ew")
                row += 1

    def run(self):
        self.window.mainloop()