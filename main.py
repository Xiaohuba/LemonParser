"""
Parse `.cdf` file of [lemonlime](https://github.com/Project-LemonLime/Project_LemonLime),
and generate uoj-format `problem.conf`!
Author: Xiaohuba
"""

import json, argparse, os, shutil, random, sys
import utils

__version__ = "0.9"
__author__ = "Xiaohuba"

parser = argparse.ArgumentParser(description="Parse Lemonlime conf files(.cdf)")
parser.add_argument("filename", type=str, help="Lemon work path")
parser.add_argument("-S", "--silent", help="Silent mode", action="store_true")
parser.add_argument("-A", "--attach", help="Attach statement", action="store_true")
parser.add_argument("-Z", "--zip", help="Auto create zipfile", action="store_true")
parser.add_argument(
    "--task", nargs="?", default="*", help="Parse specific task (* for all)"
)
args = parser.parse_args()

lemonDir = os.path.abspath(args.filename)
silent = args.silent
attach_statement = args.attach
parse_task = args.task
create_zip = args.zip
cdfPath = utils.getCDFPath(lemonDir)

if cdfPath is None:
    print("ERROR: No .cdf file found!")
    print("Exiting...")
    exit(1)

print(f"INFO: Load .cdf file: {cdfPath}\n")

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
            taskname = task["problemTitle"]
            if not parse_task.count("*") and not parse_task.count(taskname):
                continue
            print("=======\n")
            print(f"INFO: Parsing task {taskname}...")
            os.mkdir(os.path.join("to_uoj", taskname))
            testcases = task["testCases"]
            conf = f"# auto-generated-conf-file-by-lemon-parser-{__version__}\n"
            cnt = 0
            tc_id = 0
            score = 0
            tl = 0
            ml = 0
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
                        f"{task['problemTitle']}{caseid + cnt}.in",
                    )
                    if not silent:
                        print("INFO: Copying", fr, "->", to)
                    shutil.copy2(fr, to)
                caseid = 0
                for ouf in case["outputFiles"]:
                    fr = "data" + utils.parsePath(ouf)
                    caseid += 1
                    to = os.path.join(
                        "to_uoj",
                        taskname,
                        f"{task['problemTitle']}{caseid + cnt}.out",
                    )
                    if not silent:
                        print("INFO: Copying", fr, "->", to)
                    shutil.copy2(fr, to)
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
            conf += f"time_limit {round(tl / 1000)}\n"
            conf += f"memory_limit {ml}\n"
            if len(task["specialJudge"]) == 0:
                conf += f"use_builtin_checker wcmp\n"
                if not silent:
                    print(f"INFO: Using `wcmp` for task {taskname}.")
            else:
                (state, text) = utils.parseSPJ(os.path.join(lemonDir, "data", taskname))
                # print(f"LOG: {os.path.join(lemonDir, 'data', taskname)}")
                if state == 0:
                    if not silent:
                        print(f"INFO: Parsing spj for task {taskname}...")
                    spjFile = open(os.path.join("to_uoj", taskname, "chk.cpp"), "w")
                    spjFile.write(text)
                    spjFile.close()
                else:
                    print("WARNING: This task has unsupported spj.")
                    print("You may need to edit it manually.")
            conf += f"use_builtin_judger on\n"
            if task["taskType"] != 0:
                print("WARNING: Unsupported task type.")
                print("You may need to configure it manually.")
            confFile = open(os.path.join("to_uoj", taskname, "problem.conf"), "w")
            confFile.write(conf)
            confFile.close()
            if attach_statement:
                statement_path = os.path.join("down", "statement.pdf")
                down_path = os.path.join("to_uoj", taskname, "download")
                os.mkdir(down_path)
                try:
                    print("INFO: Copying", fr, "->", to)
                    shutil.copy2(statement_path, down_path)
                except Exception as exp:
                    print(f"ERROR: Failed to attach statement!\nException is {exp}")
            if create_zip:
                print(f"INFO: creating zipfile for task `{taskname}`...", end=" ")
                sys.stdout.flush()
                utils.zipProblem(os.path.join("to_uoj", taskname))
                print(f"done.")
            print("\n=======\n")
        except Exception as exp:
            print(f"ERROR: Unhandled Exception {exp}")
            print("Passing...")
