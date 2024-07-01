from scene.props import ProminenceLevelProp, MutingProp, AzimuthProp, ElevationProp, Prop
from xml.etree import ElementTree as XML


def try_attrib(tree: XML.Element, key: str, alter):
    try:
        return alter(tree.attrib[key])
    except KeyError:
        return None

def custom_kind(tree: XML.Element):
    description: dict[str, str] = {}
    for desc in tree:
        description[desc.attrib["langCode"]] = desc.text.strip("\n").strip() if desc.text is not None else "<Missing Description>"
    return description

class Element:
    def __init__(
            self, _id: int,
            prominence_level: ProminenceLevelProp | None = None,
            muting: MutingProp | None = None,
            azimuth: AzimuthProp | None = None,
            elevation: ElevationProp | None = None,
        ) -> None:
        self.id: int = _id
        self.prominence_level: ProminenceLevelProp | None = prominence_level
        self.muting: MutingProp | None = muting
        self.azimuth: AzimuthProp | None = azimuth
        self.elevation: ElevationProp | None = elevation

class AudioElement(Element):
    def __init__(
            self,
            _id: int,
            prominence_level: ProminenceLevelProp | None = None,
            muting: MutingProp | None = None,
            azimuth: AzimuthProp | None = None,
            elevation: ElevationProp | None = None,
            description: dict[str, str] | None = None,
            is_active: bool | None = None, is_available: bool | None = None,
            is_default: bool | None = None, is_selectable: bool | None = None,
        ) -> None:
        super().__init__(
            _id,
            prominence_level,
            muting,
            azimuth,
            elevation
        )
        self.is_active = is_active
        self.is_available = is_available
        self.description: dict[str, str] = description if description is not None else {}
        # When inside element_switch
        self.is_default = is_default
        self.is_selectable = is_selectable

    def get_desc(self, lang: str | None = None):
        if lang is not None and lang in self.description:
            return self.description[lang]
        for lang in self.description:
            return self.description[lang]
        return "-"

    @classmethod
    def parse(cls, tree: XML.Element):
        prominence_level: ProminenceLevelProp | None = None
        muting: MutingProp | None = None
        azimuth: AzimuthProp | None = None
        elevation: ElevationProp | None = None
        description: dict[str, str] = {}

        for child in tree:
            if child.tag == "prominenceLevelProp":
                prominence_level = ProminenceLevelProp.parse(child)
            elif child.tag == "mutingProp":
                muting = MutingProp.parse(child)
            elif child.tag == "azimuthProp":
                azimuth = AzimuthProp.parse(child)
            elif child.tag == "elevationProp":
                elevation = ElevationProp.parse(child)
            if child.tag == "customKind":
                description = custom_kind(child)

        return AudioElement(
            _id = int(tree.attrib["id"]),
            description = description,
            prominence_level = prominence_level,
            muting = muting,
            azimuth = azimuth,
            elevation = elevation,
            is_available = tree.attrib["isAvailable"] is True,
            is_active = try_attrib(tree, "isActive", lambda x: x is True),
            is_default = try_attrib(tree, "isDefault", lambda x: x is True),
            is_selectable = try_attrib(tree, "isSelectable", lambda x: x is True),
        )
    
    def slider_props(self):
        props: list[Prop | None] = [
            self.prominence_level,
            self.azimuth,
            self.elevation,
        ]
        return [x for x in props if x is not None]

class AudioElementSwitch(Element):
    def __init__(
            self,
            _id: int,
            prominence_level: ProminenceLevelProp | None = None,
            muting: MutingProp | None = None,
            azimuth: AzimuthProp | None = None,
            elevation: ElevationProp | None = None,
            description: dict[str, str] | None = None,
            audio_elements: dict[int, AudioElement] | None = None,
            is_available: bool | None = None, is_action_allowed: bool | None = None,
        ) -> None:
        super().__init__(
            _id=_id,
            prominence_level=prominence_level,
            muting=muting,
            azimuth=azimuth,
            elevation=elevation,
        )
        self.audio_elements: dict[int, AudioElement] = audio_elements if audio_elements is not None else {}
        self.description: dict[str, str] = description if description is not None else {}
        self.is_available = is_available
        self.is_action_allowed = is_action_allowed

    def get_desc(self, lang: str | None = None):
        if lang is not None and lang in self.description:
            return self.description[lang]
        for lang in self.description:
            return self.description[lang]
        return "-"

    def slider_props(self):
        props: list[Prop | None] = [
            self.prominence_level,
            self.azimuth,
            self.elevation,
        ]
        return [x for x in props if x is not None]

    @classmethod
    def parse(cls, tree: XML.Element):
        prominence_level: ProminenceLevelProp | None = None
        muting: MutingProp | None = None
        azimuth: AzimuthProp | None = None
        elevation: ElevationProp | None = None
        description: dict[str, str] = {}
        audios: dict[int, AudioElement] = {}

        for child in tree:
            if child.tag == "prominenceLevelProp":
                prominence_level = ProminenceLevelProp.parse(child)
            elif child.tag == "mutingProp":
                muting = MutingProp.parse(child)
            elif child.tag == "azimuthProp":
                azimuth = AzimuthProp.parse(child)
            elif child.tag == "elevationProp":
                elevation = ElevationProp.parse(child)
            if child.tag == "customKind":
                description = custom_kind(child)
            elif child.tag == "audioElements":
                for audio_elemnt in child:
                    _e = AudioElement.parse(audio_elemnt)
                    audios[_e.id] = _e

        return AudioElementSwitch(
            _id = int(tree.attrib["id"]),
            description = description,
            prominence_level = prominence_level,
            muting = muting,
            azimuth = azimuth,
            elevation = elevation,
            audio_elements=audios,
            is_available = tree.attrib["isAvailable"] is True,
            is_action_allowed = tree.attrib["isActionAllowed"] is True,
        )

class Preset:
    def __init__(
            self,
            _id: int,
            description: dict[str, str] | None = None,
            is_active: bool | None = None, is_available: bool | None = None,
            is_default: bool | None = None, is_selectable: bool | None = None,
            audio_elements: dict[int, AudioElement] | None = None, audio_element_switch: dict[int, AudioElementSwitch] | None = None,
        ) -> None:
        self.id = _id
        self.is_active = is_active
        self.is_default = is_default
        self.is_available = is_available
        self.is_selectable = is_selectable
        self.description: dict[str, str] = description if description is not None else {}
        self.audio_elements: dict[int, AudioElement] = audio_elements if audio_elements is not None else {}
        self.audio_element_switch: dict[int, AudioElementSwitch] = audio_element_switch if audio_element_switch is not None else {}

    def get_desc(self, lang: str | None = None):
        if lang is not None and lang in self.description:
            return self.description[lang]
        for lang in self.description:
            return self.description[lang]
        return "-"

    @classmethod
    def parse(cls, tree: XML.Element):
        description: dict[str, str] = {}
        audios: dict[int, AudioElement]  = {}
        audio_switches: dict[int, AudioElementSwitch] = {}
        for child in tree:
            if child.tag == "customKind":
                description = custom_kind(child)
            elif child.tag == "audioElement":
                _e = AudioElement.parse(child)
                audios[_e.id] = _e
            elif child.tag == "audioElementSwitch":
                _e = AudioElementSwitch.parse(child)
                audio_switches[_e.id] = _e

        return Preset(
            _id = int(tree.attrib["id"]),
            description = description,
            audio_elements = audios,
            audio_element_switch = audio_switches,
            is_active= tree.attrib["isActive"] is True,
            is_default= tree.attrib["isDefault"] is True,
            is_available= tree.attrib["isAvailable"] is True,
        )

class AudioSceneConfig:
    def __init__(
            self, uuid: str,
            presets: dict[int, Preset],
            drc_info: tuple[int],
        ) -> None:
        self.uuid = uuid
        self.drc_info: tuple[int] = drc_info
        self.presets: dict[int, Preset] = presets

    @classmethod
    def start_parsing(cls, scene_path: str):
        loaded_scene = XML.parse(scene_path)
        root = loaded_scene.getroot()
        return cls.parse(root)

    @classmethod
    def parse(cls, tree: XML.Element):
        presets = {}
        drc = set()
        for child in tree:
            if child.tag == "presets":
                for preset in child:
                    _p = Preset.parse(preset)
                    presets[_p.id] = _p
            elif child.tag == "DRCInfo":
                for drc_index in child:
                    drc.add(int(drc_index.attrib["index"]))

        return AudioSceneConfig(
            uuid=tree.attrib["uuid"],
            presets=presets,
            drc_info=tuple(drc),
        )
