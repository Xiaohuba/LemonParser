"""
Parse `.cdf` file of [lemonlime](https://github.com/Project-LemonLime/Project_LemonLime),
and generate uoj-format `problem.conf`!
Author: Xiaohuba
"""

import json, argparse, os, random, sys, math, asyncio
import utils

__version__ = "0.12"
__author__ = "Xiaohuba"

parser = argparse.ArgumentParser(description="Parse Lemonlime conf files(.cdf)")
parser.add_argument("filename", type=str, help="Lemon work path")
parser.add_argument("-S", "--silent", help="Silent mode", action="store_true")
parser.add_argument(
    "-D", "--attach-down", help="Attach statement and samples", action="store_true"
)
parser.add_argument("-E", "--editorial", help="Attach editorial", action="store_true")
parser.add_argument(
    "-H",
    "--enable-hack",
    help="Enable hack(both std and validator are required)",
    action="store_true",
)
parser.add_argument("-Z", "--zip", help="Auto create zipfile", action="store_true")
parser.add_argument(
    "--task", nargs="?", default="*", help="Parse specific task (* for all)"
)
parser.add_argument(
    "--noip-checker",
    help="Use noip-style checker instead of `wcmp`",
    action="store_true",
)
parser.add_argument(
    "--parse-pdf",
    help="[Experimental] use qwen3 vl to generate markdown version of statement from pdf, you need to set the OPENROUTER_API_KEY environment variable",
    action="store_true",
)
parser.add_argument(
    "--statement-format",
    help="Specify the output format of the parsed statement (md or json)",
    choices=["md", "json"],
    default="md",
)
parser.add_argument("--version", action="version", version=f"Lemonparser {__version__}")

args = parser.parse_args()

lemonDir = os.path.abspath(args.filename)
silent = args.silent
attach_down = args.attach_down
attach_sol = args.editorial
hack = args.enable_hack
parse_task = args.task
create_zip = args.zip
parse_pdf = args.parse_pdf
format = args.statement_format

checker_name = "noip" if args.noip_checker else "wcmp"
cdfPath = utils.getCDFPath(lemonDir)
statement_path = os.path.join("down", "statement.pdf")

if hack:
    print("WARNING: Hack is not supported yet.")

if cdfPath is None:
    print("ERROR: No .cdf file found!")
    print("Exiting...")
    exit(1)

if parse_pdf:
    if not os.path.exists(statement_path):
        print("ERROR: statement.pdf not found!")
        print("Exiting...")
        exit(1)

print(f"INFO: Loaded .cdf file: {cdfPath}\n")
print(f"INFO: default checker set to: {checker_name}\n")

background_tasks = []


async def main():
    global background_tasks
    with open(cdfPath, "r", encoding="utf-8") as cdf:
        json_obj = json.load(cdf)
        tasks = json_obj["tasks"]
        os.chdir(lemonDir)
        try:
            os.mkdir("to_uoj")
        except Exception as exp:
            print(
                f"WARNING: Failed to create folder `to_uoj`.\nReceived Exception {exp}.\nRetriing..."
            )
            os.rename("to_uoj", f"to_uoj.{random.randint(1,9999)}.old")
            os.mkdir("to_uoj")

        for task in tasks:
            try:
                taskname = task["sourceFileName"]
                if not parse_task.count("*") and not parse_task.count(taskname):
                    continue
                print("=======\n")
                print(f"INFO: Parsing task {taskname}...")
                os.mkdir(os.path.join("to_uoj", taskname))

                print("Please input page range [l, r) from statement.pdf.")
                st = int(input("start: "))
                ed = int(input("end: "))
                if parse_pdf:
                    if format == "json":
                        to = os.path.join("to_uoj", f"{taskname}.json")
                        difficulty = int(input("Please input difficulty (0-9): "))
                        impl_hardness = int(
                            input("Please input implementation hardness (800-3500): ")
                        )
                        tags = input("Please input tags (space separated): ").split()
                        is_public = (
                            input("Is this problem public? (y/n): ").lower() == "y"
                        )
                        origin = input("Please input link to the origin: ")
                        background_tasks += [
                            utils.parsePDFtoJSON(
                                statement_path,
                                to,
                                st,
                                ed,
                                difficulty,
                                impl_hardness,
                                tags,
                                is_public,
                                origin,
                            )
                        ]
                    else:
                        to = os.path.join("to_uoj", f"{taskname}.md")
                        background_tasks += [utils.parsePDF(statement_path, to, st, ed)]
                    # new_task = asyncio.create_task(
                    #     utils.parsePDF(statement_path, to, st, ed)
                    # )
                    # background_tasks.add(new_task)
                    # new_task.add_done_callback(background_tasks.discard)

                testcases = task["testCases"]
                conf = f"# auto-generated-conf-file-by-lemon-parser-{__version__}\n"
                cnt = 0
                tc_id = 0
                score = 0
                tl = 0
                ml = 0
                no_err = 1

                conf += f"input_pre {taskname}\n"
                conf += f"input_suf in\n"
                conf += f"output_pre {taskname}\n"
                conf += f"output_suf out\n"
                conf += f"n_subtasks {len(testcases)}\n"
                for case in testcases:
                    tc_id += 1
                    score += case["fullScore"]
                    # Hack: inputFiles may contain dependence flags; use outputFiles instead
                    conf += f"subtask_end_{tc_id} {cnt + len(case['outputFiles'])}\n"
                    conf += f"subtask_score_{tc_id} {case['fullScore']}\n"
                    tl = max(tl, case["timeLimit"])
                    ml = max(ml, case["memoryLimit"])
                    caseid = 0
                    dep = []
                    for inf in case["inputFiles"]:
                        depd = utils.isDependence(inf)
                        if depd != -1:
                            dep.append(depd)
                            continue
                        fr = "data" + utils.parsePath(inf)
                        caseid += 1
                        to = os.path.join(
                            "to_uoj",
                            taskname,
                            f"{taskname}{caseid + cnt}.in",
                        )
                        utils.copy_files(fr, to, silent)
                    caseid = 0
                    for ouf in case["outputFiles"]:
                        fr = "data" + utils.parsePath(ouf)
                        caseid += 1
                        to = os.path.join(
                            "to_uoj",
                            taskname,
                            f"{taskname}{caseid + cnt}.out",
                        )
                        utils.copy_files(fr, to, silent)

                    cnt += caseid
                    if len(dep) > 0:
                        conf += f"subtask_dependence_{tc_id} many\n"
                        dep_cnt = 0
                        for depd in dep:
                            dep_cnt += 1
                            conf += f"subtask_dependence_{tc_id}_{dep_cnt} {depd}\n"
                conf += f"n_tests {cnt}\n"
                conf += f"n_ex_tests 0\n"
                conf += f"n_sample_tests 0\n"
                # Hack: universaloj doesn't support float TL. Round to integer instead.
                conf += f"time_limit {math.ceil(tl / 1000)}\n"
                conf += f"memory_limit {ml}\n"
                if task["specialJudge"] in ("", "wcmp"):
                    conf += f"use_builtin_checker {checker_name}\n"
                    if not silent:
                        print(f"INFO: Using `{checker_name}` for task {taskname}.")
                else:
                    spj_name = (
                        task["specialJudge"]
                        .replace(".exe", ".cpp")
                        .replace(".bin", ".cpp")
                    )
                    if not spj_name.endswith(".cpp"):
                        spj_name += ".cpp"
                    try:
                        if not silent:
                            print(
                                f"INFO: Parsing spj {spj_name} for task {taskname}..."
                            )
                        text = utils.parseSPJ(os.path.join(lemonDir, "data", spj_name))
                    except Exception as err:
                        print(f"WARNING: Exception caught: {err}")
                        print("WARNING: This task has unsupported spj.")
                        print("You may need to edit it manually.")
                        no_err = 0
                    else:
                        spjFile = open(os.path.join("to_uoj", taskname, "chk.cpp"), "w")
                        spjFile.write(text)
                        spjFile.close()
                if attach_down:
                    sample_path = os.path.join("down", taskname)
                    down_path = os.path.join("to_uoj", taskname, "download")
                    main_path = os.path.join("to_uoj", taskname)
                    os.mkdir(down_path)
                    try:
                        utils.copy_files(statement_path, down_path, silent)
                        # utils.copy_files(statement_path, main_path, silent)
                        utils.splitPDF(
                            statement_path,
                            os.path.join(main_path, "statement.pdf"),
                            st,
                            ed,
                        )
                        utils.copy_dir(sample_path, down_path, silent)
                    except Exception as exp:
                        print(f"ERROR: Failed to attach statement!\nException is {exp}")
                        no_err = 0
                    conf += f"use_pdf_statement on\n"

                if attach_sol:
                    sol_path = "solution.pdf"
                    main_path = os.path.join("to_uoj", taskname)
                    try:
                        utils.copy_files(sol_path, main_path, silent)
                    except Exception as exp:
                        print(f"ERROR: Failed to attach solution!\nException is {exp}")
                        no_err = 0
                    conf += f"show_solution on\n"

                conf += f"use_builtin_judger on\n"
                if task["taskType"] != 0:
                    print("WARNING: Unsupported task type.")
                    print("You may need to configure it manually.")
                    no_err = 0
                confFile = open(os.path.join("to_uoj", taskname, "problem.conf"), "w")
                confFile.write(conf)
                confFile.close()

                if create_zip and no_err:
                    background_tasks += [
                        utils.zipProblem(os.path.join("to_uoj", taskname), taskname)
                    ]
                    # new_task = asyncio.create_task(
                    #     utils.zipProblem(os.path.join("to_uoj", taskname), taskname)
                    # )
                    # background_tasks.add(new_task)
                    # new_task.add_done_callback(background_tasks.discard)
                elif create_zip:
                    print("WARNING: Skipped zipfile creation.")
                print("\n=======\n")
            except Exception as exp:
                print(f"ERROR: Unhandled Exception {exp}")
                print("Passing...")
    print(f"INFO: Waiting for {len(background_tasks)} tasks to finish...")
    await asyncio.gather(*background_tasks)
    print("INFO: Finished.")


asyncio.run(main())
