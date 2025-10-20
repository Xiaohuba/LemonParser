import platform, os, zipfile, shutil, base64, time, json
from io import BytesIO
from pdf2image import convert_from_path
import ai
from pypdf import PdfReader, PdfWriter

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


async def zipProblem(path, taskname):
    print(f"INFO: Creating zipfile for task `{taskname}`...")
    cur = os.path.abspath(os.curdir)
    zip_obj = zipfile.ZipFile(path + ".zip", "w", zipfile.ZIP_DEFLATED)
    os.chdir(path)
    for root, _, files in os.walk("."):
        for file in files:
            zip_obj.write(os.path.join(root, file))
    zip_obj.close()
    os.chdir(cur)
    print(f"INFO: Finished creating zipfile for task `{taskname}`.")


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


def pdf2images(path, st_page, ed_page):
    images = convert_from_path(path, first_page=st_page, last_page=ed_page - 1)
    encoded_images = []
    for image in images:
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        encoded_image = base64.b64encode(buffered.getvalue()).decode("utf-8")
        encoded_images.append(encoded_image)
    return encoded_images


async def parsePDF(fr, to, st_page, ed_page):
    ti_st = time.time()
    images = pdf2images(fr, st_page, ed_page)
    md = await ai.image2md(images)
    with open(to, "w") as f:
        f.write(md)
    ti_ed = time.time()
    print(f"INFO: Parsed PDF in {ti_ed - ti_st:.2f}s.")


async def parsePDFtoJSON(
    fr, to, st_page, ed_page, difficulty, impl_hardness, tags, is_public, origin
):
    ti_st = time.time()
    images = pdf2images(fr, st_page, ed_page)
    md = await ai.image2md(images)
    title = md.split("\n")[0].replace("### ", "").strip()
    description = "\n".join(md.split("\n")[1:]).strip()
    json_data = {
        "title": title,
        "description": description,
        "difficulty": difficulty,
        "tags": tags,
        "shit_score": impl_hardness,
        "public": is_public,
        "origin": origin,
    }
    with open(to, "w") as f:
        f.write(json.dumps(json_data))
    ti_ed = time.time()
    print(f"INFO: Parsed PDF in {ti_ed - ti_st:.2f}s.")


def splitPDF(fr, to, st_page, ed_page):
    reader = PdfReader(fr)
    writer = PdfWriter()

    for i in range(st_page - 1, ed_page - 1):
        writer.add_page(reader.pages[i])

    # print(f"DEBUG {fr} -> {to}")
    with open(to, "wb") as out_pdf:
        writer.write(out_pdf)
