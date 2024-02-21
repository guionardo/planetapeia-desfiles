from dataclasses import dataclass, field


@dataclass
class HomeCard:
    header: str
    badged_list_items: list = field(default_factory=list)
    list_items: list = field(default_factory=list)
    links: list = field(default_factory=list)
    text: str = ""
