from collections import defaultdict
from xml.etree import ElementTree as XML


class Prop:
    def __init__(
            self,
            is_action_allowed: bool | None = None,
            min: float | None = None, max: float | None = None,
            val: float | None = None, default: float | None = None,
        ) -> None:
        self.is_action_allowed = is_action_allowed
        self.min = min
        self.max = max
        self.val = val
        self.default = default

    @classmethod
    def parse(cls, tree: XML.Element):
        attrib = defaultdict(lambda: None, **tree.attrib)
        return cls(
            is_action_allowed = attrib["isActionAllowed"] is True,
            min = float(attrib["min"]) if attrib["min"] is not None else None,
            max = float(attrib["max"]) if attrib["max"] is not None else None,
            val = float(attrib["val"]) if attrib["val"] is not None else None,
            default = float(attrib["def"]) if attrib["def"] is not None else None,
        )

class ProminenceLevelProp(Prop):
    def __init__(
            self,
            is_action_allowed: bool,
            min: float, max: float,
            val: float, default: float,
        ) -> None:
        return super().__init__(
            is_action_allowed,
            min, max, val, default,
        )

class MutingProp(Prop):
    def __init__(
            self,
            is_action_allowed: bool,
            val: float, default: float,
        ) -> None:
        return super().__init__(
            is_action_allowed,
           val, default,
        )

class AzimuthProp(Prop):
    def __init__(
            self,
            is_action_allowed: bool,
            min: float, max: float,
            val: float, default: float,
        ) -> None:
        return super().__init__(
            is_action_allowed,
            min, max, val, default,
        )

class ElevationProp(Prop):
    def __init__(
            self,
            is_action_allowed: bool,
            min: float, max: float,
            val: float, default: float,
        ) -> None:
        return super().__init__(
            is_action_allowed,
            min, max, val, default,
        )
