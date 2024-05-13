import platform, os, zipfile

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
        if ch in ("/", "\\"):
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
        if file in ("chk.cpp", "checker.cpp"):
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


def isDependence(name):
    name = name.lower()
    if name.endswith("lemon_subtaskdependence_flag"):
        return int(name.split("_")[0])
    else:
        return -1


def zipProblem(path):
    cur = os.path.abspath(os.curdir)
    zip_obj = zipfile.ZipFile(path + ".zip", "w", zipfile.ZIP_DEFLATED)
    os.chdir(path)
    for root, _, files in os.walk("."):
        for file in files:
            zip_obj.write(os.path.join(root, file))
    zip_obj.close()
    os.chdir(cur)
