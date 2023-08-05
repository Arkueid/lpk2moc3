import json
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from threading import Thread
import manager
from Core.lpk_loader import LpkLoader

currentThread = None


class Win(tk.Tk):

    def __init__(self):
        super(Win, self).__init__()
        self.title("LPK模型解压工具")
        self._width = 570
        self._height = 450
        self.inputPath = tk.StringVar()
        self.outputPath = tk.StringVar()
        self.configPath = tk.StringVar()
        self.modelNameVar = tk.StringVar()
        self.modelNameVar.set("character")
        self.setupUI()
        manager.Log("使用说明\n"
                    "从Live2DViewerEX导出的模型格式为.wpk格式\n"
                    "先将其拓展名改为rar，解压后得到.lpk文件和config.json文件\n"
                    "如果模型不来自EXViewer则不需要输入config.json路径\n"
                    "模型名称可自定义，支持中文，但最好使用英文")

    def setGeometry(self):
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        self.geometry("%dx%d+%d+%d" % (
            self._width,
            self._height,
            (sw - self._width) / 2,
            (sh - self._height) / 2
        ))

    def setupUI(self):
        self.setGeometry()
        self.resizable(width=False, height=False)
        self.lbl_input = tk.Label(
            self,
            width=10,
            text="lpk文件",
        )
        self.input = tk.Entry(
            self,
            textvariable=self.inputPath,
            width=40
        )
        self.getInput = tk.Button(
            self,
            text="打开文件",
            command=self.getInputPath,
            width=10
        )
        self.lbl_output = tk.Label(
            self,
            width=10,
            text="输出路径",
        )
        self.output = tk.Entry(
            self,
            textvariable=self.outputPath,
            width=40
        )
        self.getOutput = tk.Button(
            self,
            text="打开文件夹",
            command=self.getOutputPath,
            width=10
        )
        self.lbl_config = tk.Label(
            self,
            text="config.json"
        )
        self.config = tk.Entry(
            self,
            textvariable=self.configPath,
            width=40
        )
        self.getConfig = tk.Button(
            self,
            text="选择json文件",
            command=self.getConfigPath,
            width=10,
        )
        self.getUnpack = tk.Button(
            self,
            text="解压",
            command=self.Unpack,
            width=20
        )
        self.lbl_modelName = tk.Label(
            self,
            text="模型名称",
            width=10
        )
        self.modelName = tk.Entry(
            self,
            textvariable=self.modelNameVar,
            width=40
        )
        self.logArea = tk.Text(
            self,
            width=62,
            height=10,
            startline=2,
            font=("微软雅黑", 10, "normal"),
            spacing1=5.0
        )

        manager.LogArea = self.logArea

        self.logArea.config(background='white')

        self.lbl_input.grid(row=0, column=0)
        self.input.grid(column=1, row=0, columnspan=4, padx=5)
        self.getInput.grid(column=5, row=0, columnspan=1)

        self.lbl_config.grid(row=1, column=0)
        self.config.grid(row=1, column=1, padx=5, columnspan=4)
        self.getConfig.grid(row=1, column=5)

        self.lbl_output.grid(row=2, column=0)
        self.output.grid(column=1, row=2, columnspan=4, padx=5)
        self.getOutput.grid(column=5, row=2, columnspan=1)

        self.lbl_modelName.grid(row=3, column=0)
        self.modelName.grid(row=3, column=1, columnspan=4, padx=5)

        self.logArea.grid(row=4, column=0, columnspan=7, pady=10, padx=3)

        self.getUnpack.grid(row=5, column=2, padx=10, pady=5, columnspan=2)

    def getInputPath(self):
        filePath = filedialog.askopenfilename(
            filetypes=[("LPK", ".lpk")]
        )
        if len(filePath) > 0:
            self.inputPath.set(filePath)

    def getOutputPath(self):
        filePath = filedialog.askdirectory()
        if len(filePath) > 0:
            self.outputPath.set(filePath)

    def getConfigPath(self):
        filePath = filedialog.askopenfilename(
            filetypes=[("JSON", ".json")]
        )
        if len(filePath) > 0:
            self.configPath.set(filePath)
            try:
                x = json.load(open(self.config.get(), "r", encoding="utf-8"))
                self.modelNameVar.set(
                    x["title"].replace("\\", "").replace("/", "").replace(":", "").replace("?", "").replace("<",
                                                                                                            "").replace(
                        ">", "").replace("|", ""))
            except Exception as e:
                print(e)

    def Unpack(self):
        global currentThread
        if currentThread is not None:
            messagebox.showwarning("LPK模型解压工具", "解压已在进行，请等待")
            return
        self.logArea.config(state=tk.NORMAL)
        self.logArea.delete("1.0", "end")
        currentThread = Thread(target=self._unpack)
        currentThread.start()

    def _unpack(self):
        global currentThread
        if len(self.output.get()) > 0 and len(self.input.get()) > 0:
            manager.Log(
                "lpk文件: %s\n输出路径: %s"
                % (self.input.get(), self.output.get())
            )
            # try:
            loader = LpkLoader(self.input.get(), self.config.get())
            loader.extract(self.output.get())
            manager.SetupModel(os.path.join(self.outputPath.get(), "character"), self.modelNameVar.get())
            manager.Log("解压完成！")
            messagebox.showinfo("LPK模型解压工具", "解压成功!")
        # except Exception as e:
            messagebox.showerror("LPK模型解压工具", "%s" % str(e))
            manager.Log("发生错误: %s\n解压停止。" % e)
        else:
            messagebox.showerror(
                "LPK模型解压工具", "缺少输入或输出路径"
            )
        currentThread = None


if __name__ == '__main__':
    w = Win()
    w.mainloop()
