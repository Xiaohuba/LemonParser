import platform, os

os_info = platform.system()


def getCDFPath(pth):
    files = os.listdir(pth)
    for file in files:
        if file.endswith(".cdf"):
            return os.path.join(pth, file)


def parsePath(pth):
    pth += "/"
    cur = ""
    final = ""
    for ch in pth:
        if ch == "/" or ch == "\\":
            if os_info == "Windows":
                final += "\\" + cur
            else:
                final += "/" + cur
            cur = ""
        else:
            cur += ch
    return final


if __name__ == "__main__":
    print(parsePath("a\\b"))
    print(parsePath("a/b\\c"))
    print(parsePath("casio/casio1.in/"))
