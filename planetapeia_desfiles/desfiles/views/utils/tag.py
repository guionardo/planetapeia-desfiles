class Tag:
    def __init__(self, tag_name, *children, **attributes):
        self.tag_name = tag_name
        self.children = children
        self.attributes = {
            attr.replace("cls", "class").replace("_", "-"): value
            for attr, value in (attributes or {}).items()
        }

    def __str__(self):
        attrs = " ".join(
            f'{attribute}="{value}"' for attribute, value in self.attributes.items()
        )
        if not self.children:
            return f"<{self.tag_name} {attrs} />"
        lines = [f"<{self.tag_name} {attrs}>"]
        lines.extend(str(child) for child in self.children)
        lines.append(f"</{self.tag_name}>\n")
        return "\n".join(lines)

    def __call__(self, *args, **kwds):
        return str(self)


if __name__ == "__main__":
    a = Tag("a", "Caption", cls="button testing", enabled=True)
    tag = str(a).replace("\n", "")
    assert tag == '<a class="button testing" enabled="True">Caption</a>'
    b = Tag("b", a, cls="classe teste")
    print(b)
