from packaging.version import Version
import os
import datetime


def read_version_pyproject() -> Version:
    with open("pyproject.toml") as f:
        for line in f.readlines():
            if line.startswith('version = "'):
                version = Version(
                    "".join([c for c in line if "0" <= c <= "9" or c == "."])
                )
                break
    return version


def write_version_pyproject(new_version: Version):
    lines = []
    with open("pyproject.toml") as f:
        for line in f.readlines():
            if line.startswith('version = "'):
                lines.append(f'version = "{new_version}"\n')
            else:
                lines.append(line)

    with open("pyproject.toml", "w") as f:
        f.writelines(lines)


def write_version_file(new_version: Version):
    with open(os.path.join("planetapeia_desfiles", "desfiles", "version.py"), "w") as f:
        f.writelines(
            [
                "# FILE AUTOMATICALLY GENERATED\n",
                "\n",
                f'__VERSION__ = "{new_version}"\n',
                f'__VERSION_DATE__ = "{datetime.datetime.now()}"\n',
            ]
        )


def main():
    v = read_version_pyproject()
    major, minor, micro = v.major, v.minor, v.micro
    micro += 1
    new_v = Version(f"{major}.{minor}.{micro}")
    write_version_pyproject(new_v)
    write_version_file(new_v)


if __name__ == "__main__":
    main()
