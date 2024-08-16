import platform, os, zipfile, shutil

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


def parseSPJ(file):
    with open(os.path.join(file), "r") as spj:
        content = spj.read()
        content = content.replace("testlib_for_lemon.h", "testlib.h")
        content = content.replace("testlib_for_lemons.h", "testlib.h")
        content = content.replace("registerLemonChecker", "registerTestlibCmd")
        # print(content)
        if content.find("testlib.h") == -1:
            raise Exception("SPJ must be written with testlib.h.")
        else:
            return content


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


def copy_files(fr, to, silent):
    if not silent:
        print("INFO: Copying", fr, "->", to)
    shutil.copy2(fr, to)


def copy_dir(fr, to, silent):
    files = os.listdir(fr)
    for file in files:
        path = os.path.join(fr, file)
        if not os.path.isdir(path):
            copy_files(path, to, silent)
