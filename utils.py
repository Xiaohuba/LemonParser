import platform, os

os_info = platform.system()


def getCDFPath(pth):
    files = os.listdir(pth)
    for file in files:
        if file.endswith(".cdf"):
            return os.path.join(pth, file)
    return None


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


def parseSPJ(pth):
    files = os.listdir(pth)
    for file in files:
        # print(f"{file}")
        if file == "chk.cpp" or file == "checker.cpp":
            with open(os.path.join(pth, file), "r") as spj:
                content = spj.read()
                content = content.replace("testlib_for_lemon.h", "testlib.h")
                content = content.replace("testlib_for_lemons.h", "testlib.h")
                content = content.replace("registerLemonChecker", "registerTestlibCmd")
                # print(content)
                if content.find("testlib.h") == -1:
                    return (-1, "")
                else:
                    return (0, content)
    return (-1, "")
