from dataclasses import dataclass, field


@dataclass
class HomeCard:
    """Card para a página home
    badged_list_items: list[]
    list_items: list[str]
    links: list[('texto','link','badge')]"""

    header: str
    badged_list_items: list = field(default_factory=list)
    list_items: list = field(default_factory=list)
    links: list = field(default_factory=list)
    text: str = ""
    style: str = "light"
