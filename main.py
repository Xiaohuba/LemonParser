import json, argparse, os, shutil, random
import utils

parser = argparse.ArgumentParser(description="Parse Lemonlime conf files(.cdf)")
parser.add_argument("filename", type=str, help="Lemon work path")
args = parser.parse_args()

lemonDir = os.path.abspath(args.filename)
cdfPath = utils.getCDFPath(lemonDir)

print(f"Load .cdf file: {cdfPath}")

with open(cdfPath, "r") as cdf:
    json_obj = json.load(cdf)
    tasks = json_obj["tasks"]
    os.chdir(lemonDir)
    try:
        os.mkdir("to_uoj")
    except Exception as exp:
        print(
            f"Failed to create folder `to_uoj`.\nReceived Exception {exp}.\nRetriing..."
        )
        os.rename("to_uoj", f"to_uoj.{random.randint(1,9999)}.old")
        os.mkdir("to_uoj")
    for task in tasks:
        taskname = task["problemTitle"]
        print(f"Parsing task {taskname}...")
        os.mkdir(os.path.join("to_uoj", taskname))
        testcases = task["testCases"]
        conf = ""
        cnt = 0
        id = 0
        score = 0
        tl = 0
        ml = 0
        conf += f"input_pre {taskname}\n"
        conf += f"input_suf in\n"
        conf += f"output_pre {taskname}\n"
        conf += f"output_suf out\n"
        conf += f"n_subtasks {len(testcases)}\n"
        for case in testcases:
            id += 1
            score += case["fullScore"]
            conf += f"subtask_end_{id} {cnt + len(case['inputFiles'])}\n"
            conf += f"subtask_score_{id} {case['fullScore']}\n"
            tl = max(tl, case["timeLimit"])
            ml = max(ml, case["memoryLimit"])
            caseid = 0
            for inf in case["inputFiles"]:
                fr = "data" + utils.parsePath(inf)
                caseid += 1
                to = os.path.join(
                    "to_uoj",
                    taskname,
                    f"{task['problemTitle']}{caseid + cnt}.in",
                )
                print(fr, "->", to)
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
                print(fr, "->", to)
                shutil.copy2(fr, to)
            cnt += len(case["inputFiles"])
        conf += f"n_tests {cnt}\n"
        conf += f"n_ex_tests 0\n"
        conf += f"n_sample_tests 0\n"
        conf += f"time_limit_ms {tl}\n"
        conf += f"memory_limit {ml}\n"
        if len(task["specialJudge"]) == 0:
            conf += f"use_builtin_checker wcmp\n"
        else:
            print("This task has spj.\nYou may need to edit it manually.")
        conf += f"use_builtin_judger on\n"
        confFile = open(os.path.join("to_uoj", taskname, "problem.conf"), "w")
        confFile.write(conf)
        confFile.close()
        print("\n\n")
