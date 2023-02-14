import json
import os.path
import re
import subprocess
from tkinter import Text, NORMAL, DISABLED, END

import motion_spec


LogArea: Text | None = None


def rmdir(path):
    for i in os.listdir(path):
        p = os.path.join(path, i)
        if os.path.isdir(p):
            rmdir(p)
        else:
            os.remove(p)
    os.rmdir(path)


def Log(info):
    global LogArea
    LogArea.config(state=NORMAL)
    LogArea.insert(END, info + "\n")
    LogArea.see(END)
    LogArea.config(state=DISABLED)


def SetupModel(model_dir: str, modelNameBase: str = None):
    motionPath, soundPath = CheckPath(model_dir)
    if not modelNameBase:
        modelNameBase = os.path.split(model_dir)[-1]
    modelJsonPathList: list = list()
    pat = re.compile("^model\d?.json$")
    for groupName in os.listdir(model_dir):
        if pat.findall(groupName):
            modelJsonPathList.append(os.path.join(model_dir, groupName))

    Log("Model Json Found: %s" % modelJsonPathList)
    removeList = list()
    for idx, modelJsonPath in enumerate(modelJsonPathList):
        modelName = modelNameBase + "" if idx == 0 else str(idx+1)
        x = json.load(open(modelJsonPath, 'r', encoding='utf-8'))
        motions = x["FileReferences"].get("Motions", [])
        for groupName in motions:
            Log("[Motion Group]: %s" % groupName)
            for idx, motion in enumerate(motions[groupName]):
                _File: str | None = motion.get("File", None)
                _Sound: str | None = motion.get("Sound", None)
                # motions/*.motion3.json
                if _File:
                    srcPath = os.path.join(model_dir, _File)
                    fileName = _File.replace("FileReferences_Motions", modelName).replace("_File_0", "").replace(".json", ".motion3.json")
                    targetPath = os.path.join(motionPath, fileName)
                    src = json.load(open(srcPath, 'r', encoding='utf-8'))
                    Log("CurveCount: %d" % src["Meta"]["CurveCount"])
                    Log("TotalSegmentCount: %d" % src["Meta"]["TotalSegmentCount"])
                    Log("TotalPointCount: %d" % src["Meta"]["TotalPointCount"])
                    with open(targetPath, 'w', encoding='utf-8') as f:
                        curve_count, segment_count, point_count = motion_spec.recount_motion(src)
                        Log("%d, %d, %d" % (curve_count, segment_count, point_count))
                        src["Meta"]["CurveCount"] = curve_count
                        src["Meta"]["TotalSegmentCount"] = segment_count
                        src["Meta"]["TotalPointCount"] = point_count
                        json.dump(src, f, ensure_ascii=False, indent=2)
                    removeList.append(srcPath)
                    Log("[Motion]: %s >>> %s" % (_File, targetPath))
                    x["FileReferences"]["Motions"][groupName][idx]["File"] = "motions/" + fileName
                # sounds/*.wav
                if _Sound:
                    srcPath = os.path.join(model_dir, _Sound)
                    fileName = _Sound.replace("FileReferences_Motions", modelName).replace("_Sound_0", "")
                    fileName = os.path.splitext(fileName)[0] + ".wav"
                    targetPath = os.path.join(soundPath, fileName)
                    # ffmpeg *.ogg >>> *.wav 单声道
                    cmd = "ffmpeg -i \"%s\" -ac 1 \"%s\" -y -v quiet" % (srcPath, targetPath)
                    process = subprocess.Popen(
                        cmd, shell=True,
                        stderr=subprocess.PIPE
                    )
                    out = process.stderr.read().decode('gbk').strip("\n")
                    Log("[ffmpeg]: %s" % out)
                    process.kill()
                    process.wait()
                    removeList.append(srcPath)
                    Log("[Sound]: %s >>> %s" % (_Sound, targetPath))
                    x["FileReferences"]["Motions"][groupName][idx]["Sound"] = "sounds/" + fileName
        # link hitAreas with motion groups
        for idx, hitArea in enumerate(x.get("HitAreas", [])):
            if hitArea.get("Motion", None) is not None:
                x["HitAreas"][idx]["Name"] = hitArea["Motion"].split(":")[0]

        if x.get("Controllers", None) is not None:
            if x["Controllers"].get("ParamHit", None) is not None:
                if x["Controllers"]["ParamHit"].get("Items", None) is not None:
                    for idx2, item in enumerate(x["Controllers"]["ParamHit"]["Items"]):
                        if item.get("EndMtn", None) is not None:
                            x["HitAreas"].append(
                                {
                                    "Name": item.get("EndMtn"),
                                    "Id": item.get("Id")
                                }
                            )
        # save changes to model3.json
        with open(os.path.join(model_dir, modelName + ".model3.json"), "w", encoding='utf-8') as f:
            json.dump(x, f, ensure_ascii=False, indent=2)

        if os.path.exists(modelJsonPath):
            os.remove(modelJsonPath)
        for i in set(removeList):
            Log("removing: %s" % i)
            if os.path.exists(i) and i not in x.get("Pose", ""):
                os.remove(i)
        new_dir = os.path.join(os.path.split(model_dir)[0], modelName)
        if os.path.exists(new_dir):
            rmdir(new_dir)
        os.rename(model_dir, new_dir)


def CheckPath(model_dir: str):
    motionPath = os.path.join(model_dir, "motions")
    soundPath = os.path.join(model_dir, "sounds")
    if not os.path.exists(motionPath):
        os.makedirs(motionPath)
    if not os.path.exists(soundPath):
        os.makedirs(soundPath)
    return motionPath, soundPath


if __name__ == '__main__':
    SetupModel("path to model dir", "model name")