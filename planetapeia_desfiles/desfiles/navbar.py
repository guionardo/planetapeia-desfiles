class NavBar:
    def __init__(self, navbar_caption: str = "Planetapéia"):
        self.caption = navbar_caption
        self.items = []
        self.form = ""

    def link(
        self,
        href: str,
        caption: str,
        active: bool = False,
        disabled: bool = False,
    ) -> "NavBar":
        self.items.append(
            lite_dict(
                href=href,
                caption=caption,
                active=active,
                disabled=disabled,
            )
        )
        return self

    def sublink(self, href: str, caption: str) -> "NavBar":
        divider = caption == "-"
        self.items[-1].setdefault("items", []).append(
            lite_dict(href=href, caption=caption, divider=divider)
        )
        return self

    def form(
        self,
        role: str = "search",
        form_type: str = "search",
        placeholder: str = "Busca",
        label: str = "Busca",
    ) -> "NavBar":
        self.form = f"""<form class="d-flex" role="{role}">
<input class="form-control me-2" type="{form_type}" placeholder="{placeholder}" aria-label="{label}">
<button class="btn btn-outline-success" type="submit">{label}</button>
</form>"""

        return self

    def to_dict(self) -> dict:
        return dict(caption=self.caption, items=self.items)

    def _to_html(self):
        navbar_dropdown_id = 0
        yield '<nav class="navbar navbar-expand-lg navbar-dark bg-dark">'
        yield '<div class="container">'
        yield f'<a class="navbar-brand" href="#">{self.caption}</a>'
        yield """<button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarSupportedContent">
            <ul class="navbar-nav me-auto mb-2 mb-lg-0">"""
        for item in self.items:
            if subitems := item.get("items"):
                navbar_dropdown_id += 1
                yield '<li class="nav-item dropdown">'
                yield f'<a class="nav-link dropdown-toggle" href="#" id="navbarDropdown{navbar_dropdown_id}" role="button" data-bs-toggle="dropdown" aria-expanded="false">{item.get("caption")}</a>'
                yield f'<ul class="dropdown-menu" aria-labelledby="navbarDropdown{navbar_dropdown_id}">'
                for sitem in subitems:
                    yield "<li>"
                    if sitem.get("divider"):
                        yield '<hr class="dropdown-divider">'
                    elif sitem.get("disabled"):
                        yield f'<a class="dropdown-item disabled">{ sitem.get("caption")}</a>'
                    else:
                        yield f'<a class="dropdown-item" href="{ sitem.get("href") }">{ sitem.get("caption") }</a>'
                    yield "</li>"
                yield "</ul></li>"
            else:
                yield '<li class="nav-item">'
                if item.get("disabled"):
                    yield f'<a class="nav-link disabled">{ item.get("caption")}</a>'
                else:
                    yield f'<a class="nav-link {"active" if item.get("active") else ""}" href="{ item.get("href")}">{ item.get("caption") }</a>'
                yield "</li>"
        yield """</ul>
</div>
</div>
</nav>"""

    def to_html(self) -> str:
        return "\n".join(self._to_html())


def lite_dict(**kwargs) -> dict:
    return {k: v for k, v in kwargs.items() if v}
