from collections import defaultdict
from xml.etree import ElementTree as XML


class Prop:
    def __init__(
            self,
            name: str = "Prop",
            is_action_allowed: bool | None = None,
            min: float | None = None, max: float | None = None,
            val: bool | float | None = None, default: bool | float | None = None,
        ) -> None:
        self.audio_id: int = -1
        self.is_switch = False
        self.name = name
        self.is_action_allowed = is_action_allowed
        self.min = min
        self.max = max
        self.val = val
        self.default = default

    @classmethod
    def parse(cls, tree: XML.Element):
        attrib: defaultdict[str, None | str] = defaultdict(lambda: None, **tree.attrib)
        _min = float(attrib["min"]) if attrib["min"] is not None else None
        _max = float(attrib["max"]) if attrib["max"] is not None else None
        val = attrib["val"]
        if val == "false" or val == "true":
            val = val == "true"
        elif val is not None:
            val = float(val)
        default = attrib["def"]
        if default == "false" or default == "true":
            default = default == "true"
        elif default is not None:
            default = float(default)
        return cls(
            is_action_allowed = attrib["isActionAllowed"] is True,
            min = _min,
            max = _max,
            val = val,
            default = default,
        )

class ProminenceLevelProp(Prop):
    def __init__(
            self,
            is_action_allowed: bool,
            min: float, max: float,
            val: float, default: float,
        ) -> None:
        return super().__init__(
            name="Prominence",
            is_action_allowed=is_action_allowed,
            min=min, max=max, val=val, default=default,
        )

class MutingProp(Prop):
    def __init__(
            self,
            is_action_allowed: bool,
            val: bool, default: bool, min, max,
        ) -> None:
        super().__init__(
            name="Enabled",
            is_action_allowed=is_action_allowed,
            val=val, default=default,
        )
        self.val: bool
        self.default: bool

class AzimuthProp(Prop):
    def __init__(
            self,
            is_action_allowed: bool,
            min: float, max: float,
            val: float, default: float,
        ) -> None:
        return super().__init__(
            name="Azimuth",
            is_action_allowed=is_action_allowed,
            min=min, max=max, val=val, default=default,
        )

class ElevationProp(Prop):
    def __init__(
            self,
            is_action_allowed: bool,
            min: float, max: float,
            val: float, default: float,
        ) -> None:
        return super().__init__(
            name="Elevation",
            is_action_allowed=is_action_allowed,
            min=min, max=max, val=val, default=default,
        )
