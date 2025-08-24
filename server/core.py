import re
import asyncio
import math
import pywintypes
import win32com.client as win32
from typeConversion import (
    listTOFloatVT as listToFloat,
    sentenceTOStringVT as strToString
)
from cutSlope import cut_slope, eye_cut_slope


class CADDrawingCore:
    def __init__(self, send_message_func=None) -> None:
        """
        **初始化程序**\n
        **CAD 初始化参数**\n
        -------------------------------------------------------------\n
        cad_controller :  创建一个 AutoCAD 的 COM 对象\n
        -------------------------------------------------------------\n
        doc :  获取当前活动文档\n
        -------------------------------------------------------------\n
        ven :  获取CAD版本号 <当前活动版本号>\n
        -------------------------------------------------------------\n
        oc :  获取颜色对象\n
        -------------------------------------------------------------\n
        msp :  获取模型空间\n
        -------------------------------------------------------------\n
        **基础参数设置**\n
        -------------------------------------------------------------\n
        center_line_pos_list:  中心线所在坐标列表\n
        position_stack: 绘图主体分段坐标栈\n
        sheet_position_stack: 表格分块坐标栈\n
        -------------------------------------------------------------\n
        **坐标点设置**\n
        -------------------------------------------------------------\n
        pos1 :  计算坐标点 1\n
        pos2 :  计算坐标点 2\n
        pos3 :  计算坐标点 3\n
        pos4 :  计算坐标点 4\n
        pos5 :  计算坐标点 5\n
        -------------------------------------------------------------\n
        **步段绘图参数设置**\n
        -------------------------------------------------------------\n
        self.msp_list_len :  模型空间包含字段数据长度信息\n
        self.msg_part_list_len :  模型空间绘制部位包含字段数据长度信息\n
        self.msg_part_list_len_ori 模型空间绘制部位包含字段数据长度信息 --起点\n
        pre_draw_data :  上一操作段绘图结果数据\n
        self.eye_cut_slope_mark_data : 宕眼剪裁斜率标注记录\n
         - [[上一标注坐标],[标注过的上袖宕眼剪裁斜率]，[标注过的下袖宕眼剪裁斜率]]\n
        -------------------------------------------------------------\n
        **约束设置**\n
        -------------------------------------------------------------\n
        self.cycles :  剪裁斜率循环次数 \n
        drawingConfig :  约束参数字典 \n
        -------------------------------------------------------------\n
        **标注注释设置**\n
        -------------------------------------------------------------\n
        self.cutting_slope_data : 剪裁斜率待标注数据列表\n
        self.eye_cutting_slope_data :  宕眼剪裁斜率待标注数据列表\n
        self.cut_start_to_end_dict : 记录边旁剪裁斜率对应的开剪、续剪、落剪对应所剪目数\n
        self.eye_cut_start_to_end_dict : 记录宕眼剪裁斜率对应的开剪、续剪、落剪对应所剪目数\n
        -------------------------------------------------------------\n
        **外部函数设置**\n
        -------------------------------------------------------------\n
        self.send_to_app :  发送dict数据到APP\n
        -------------------------------------------------------------\n
        :return:
        """
        #  =============================活动页初始化==============================  #
        # self.cad_controller = win32.Dispatch("AutoCAD.Application")
        # 尝试连接到已经运行的 AutoCAD 实例
        try:
            self.cad_controller = win32.GetActiveObject("AutoCAD.Application")
            print("AutoCAD 已经启动")

        except pywintypes.com_error:
            # 如果没有运行的实例，则创建一个新的实例
            print("AutoCAD 未启动，正在启动...")
            self.cad_controller = win32.Dispatch("AutoCAD.Application")
            self.cad_controller.Visible = True  # 使 AutoCAD 可见
        # 现在 acad 变量包含对 AutoCAD 应用程序对象的引用
        pref = self.cad_controller.Preferences
        # 获取文件设置
        files = pref.Files
        registry_data = str(files).split(";")
        template_path = (registry_data[0]
                         .replace("Roaming", "Local")
                         .replace("support", "Template")
                         + r"\acadiso.dwt")
        r'''
        示例
        C:\Users\ChaHaiJiLan\AppData\Roaming\Autodesk\AutoCAD 2025\R25.0\chs\support;
        D:\AppGallery\AutoCAD_\AutoCAD_2025\AutoCAD 2025\support;
        D:\AppGallery\AutoCAD_\AutoCAD_2025\AutoCAD 2025\support\zh-CN;
        D:\AppGallery\AutoCAD_\AutoCAD_2025\AutoCAD 2025\fonts;
        D:\AppGallery\AutoCAD_\AutoCAD_2025\AutoCAD 2025\help;
        D:\AppGallery\AutoCAD_\AutoCAD_2025\AutoCAD 2025\Express;
        D:\AppGallery\AutoCAD_\AutoCAD_2025\AutoCAD 2025\support\color;
        C:\Program Files (x86)\Autodesk\ApplicationPlugins\Autodesk AppManager.bundle\Contents\Windows;
        C:\Program Files (x86)\Autodesk\ApplicationPlugins\Autodesk AppManager.bundle\Contents\Windows\2025;
        C:\Program Files (x86)\Autodesk\ApplicationPlugins\Autodesk FeaturedApps.bundle\Contents\Resources 
        '''
        # print("Files:", registry_data)
        # print("Template Path:", template_path)
        try:
            self.doc = self.cad_controller.ActiveDocument
        except pywintypes.com_error:
            self.doc = self.cad_controller.Documents.Add(template_path)
        self.ven = self.cad_controller.Application.Version[0:2]
        self.oc = self.cad_controller.Application.GetInterfaceObject(F"AutoCAD.AcCmColor.{self.ven}")
        self.msp = self.doc.ModelSpace
        self.doc.Application.Visible = True
        self._set_text_style()  # 设置字体样式改
        self.load_line_type()  # 加载线型
        #  =============================参数设置==============================  #
        self.center_line_pos_list: list[float | int | None] = []
        self.position_stack: list = []
        self.sheet_position_stack = {}
        #  =============================坐标设置==============================  #
        self.pos1: list[float | int | None] = [None, None]
        self.pos2: list[float | int | None] = [None, None]
        self.pos3: list[float | int | None] = [None, None]
        self.pos4: list[float | int | None] = [None, None]
        self.pos5: list[float | int | None] = [None, None]
        #  ===========================步段绘图参数设置==========================  #
        self.msp_list_len: int = 0
        self.msg_part_list_len = 0
        self.msg_part_list_len_ori = 0
        self.pre_draw_data = {}
        self.eye_cut_slope_mark_data = [[], [], []]
        #  =============================约束设置==============================  #
        self.cycles = 0
        self.drawingConfig = {}
        # =============================标注注释设置============================  #
        self.cutting_slope_data = []
        self.eye_cutting_slope_data = []
        self.cut_start_to_end_dict: dict = {"N": 0, "T": 0, "B": 0}
        self.eye_cut_start_to_end_dict: dict = {"N": 0, "T": 0, "B": 0}
        #  =============================外部函数设置============================  #
        self.send_to_app = send_message_func

    def _active_text_style(self, font_name="长仿宋体（工程制图用）", style_name="长仿宋体") -> None:
        """
        创建新样式并设置字体
        :param font_name:  设备字体名称
        :param style_name:  活动文档字体显示名称
        :return:
        """
        new_text_style = self.doc.TextStyles.Add(style_name)
        new_text_style.SetFont(font_name, False, True, 1, 0 or 0)  # CharSet=0, PitchAndFamily=1
        # 激活新样式
        self.doc.ActiveTextStyle = self.doc.TextStyles.Item(style_name)
        self.doc.Regen(True)  # 刷新文档显示更改

    def around_view_msp(self, is_start=False):
        self.msp_list_len = len(list(self.msp))
        if is_start:
            self.msg_part_list_len_ori = self.msp_list_len
        return self.msp_list_len

    def advance_current_msp(self):
        self.msg_part_list_len = self.msp_list_len - self.msg_part_list_len_ori
        return self.msg_part_list_len

    def clean_model(self):
        """
        清除模型空间中的所有对象
        :return:
        """
        # 获取模型空间中的所有对象
        all_objects = list(self.msp)  # 将模型空间中的对象转换为列表
        # 遍历所有对象
        for obj in all_objects:
            try:
                obj.Delete()  # 尝试删除所有对象
            except pywintypes.com_error as e:
                print(e)

                async def send_error():
                    await self.send_to_app({"clean-error": 1})

                try:
                    # 尝试获取当前事件循环
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        # 如果事件循环正在运行，则将任务加入其中
                        loop.create_task(send_error())
                    else:
                        # 否则运行直到完成
                        loop.run_until_complete(send_error())
                except RuntimeError:
                    # 如果没有事件循环，创建一个新的
                    asyncio.run(send_error())

    def clean_pos_cache(self):
        self.pos1 = [None, None]
        self.pos2 = [None, None]
        self.pos3 = [None, None]
        self.pos4 = [None, None]
        self.pos5 = [None, None]

    def drawing(self, args: dict = None) -> int:
        """
        **绘制拖网参数处理函数**

        ------------------------------------------------------\n
        ||          node           ||        绘图节点       ||\n
        -----------------------------------------------------\n
        ||         netType         ||        拖网类型       ||\n
        -----------------------------------------------------\n
        ||         partType        ||      绘制部位类型      ||\n
        -----------------------------------------------------\n
        ||      originPosition     ||        原点坐标       || -> 这里的原点指的是中心对称线所在的点 \n
        -----------------------------------------------------\n
        || CurrentNumberOfSegments ||       当前绘图段数     ||\n
        -----------------------------------------------------\n
        ||     MetricParameters    ||        目大参数       ||\n
        -----------------------------------------------------\n
        ||       VerticalMesh      ||        纵向目数       ||\n
        -----------------------------------------------------\n
        ||      HorizontalMesh     ||        横向目数       ||\n
        ----------------------------------------------------\n
        ||       CuttingSlope      ||        剪裁斜率       ||\n
        ----------------------------------------------------\n
        ||     EyeCuttingSlope     ||      宕眼剪裁斜率      ||\n
        ----------------------------------------------------\n
        ||     EyeCuttingSlope     ||      剪裁斜率比率      ||\n
        ----------------------------------------------------\n
        ||     SymmetrySwitch      ||      是否对称画图      ||\n
        ----------------------------------------------------\n
        ||       MarkSwitch        ||确认是否标注本次剪裁斜率（比率）||\n
        ----------------------------------------------------\n
        ||     MarkSlopeSwitch     || 确认是否标注本次剪裁斜率 ||\n
        ----------------------------------------------------\n
        :param args:  绘图参数

        :return: int

        **返回状态参数**

        -------------------------------\n
        ||  0  ||  正常退出无异常返回   ||\n
        -------------------------------\n
        || -1  ||    严重错误返回      ||\n
        -------------------------------\n
        """

        if not self.center_line_pos_list:
            self.center_line_pos_list.extend(args["originPosition"])
            self.center_line_pos_list.extend([args["originPosition"][0], args["originPosition"][1] + 10000])
        if args["netType"].find("two") != -1:
            self.drawing_two_slices_type(args)
        elif args["netType"].find("four") != -1:
            self.drawing_four_slices_type(args)
        elif args["netType"].find("six") != -1:
            self.drawing_six_slices_type(args)
        else:
            print("接收网具类型错误")

            async def send_error():
                await self.send_to_app({"type-error": 1})

            try:
                # 尝试获取当前事件循环
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # 如果事件循环正在运行，则将任务加入其中
                    loop.create_task(send_error())
                else:
                    # 否则运行直到完成
                    loop.run_until_complete(send_error())
            except RuntimeError:
                # 如果没有事件循环，创建一个新的
                asyncio.run(send_error())

            return -1

        return 0

    def drawing_two_slices_type(self, args: dict = None) -> None:
        """
          **两片式拖网**\n
          注意：使用参数时优先使用封装过的参数
        :param args:
        :return:
        """
        try:
            self.confirm_the_clipping_slope__two(args)
            self.calculate_the_ratio(args)
            if args["CurrentNumberOfSegments"] == 1 and args["partType"] == "wing-body":
                mesh_len = (float(args["HorizontalMesh"])
                            - self.cut_start_to_end_dict["T"]
                            - self.cut_start_to_end_dict["B"]
                            * 2)
                self.pos1 = [
                    self.center_line_pos_list[0]
                    - (
                            float(args["MetricParameters"])  # 目大参数
                            * float(args["HorizontalMesh"])  # 横向目数
                            * self.drawingConfig["SCALE_RATIO"]  # 全局缩放比
                            * self.drawingConfig["HORIZONTAL_SCALE_BAR"]  # 横向缩放标尺
                            * 0.5  # 取长度一半
                    ), self.center_line_pos_list[1]]
                self.pos2 = [
                    - self.pos1[0]
                    , self.pos1[1]]
                self.pos3 = [
                    self.center_line_pos_list[0]
                    + (mesh_len
                       / 2)
                    , self.pos2[1]
                    - (
                            float(args["MetricParameters"])
                            * float(args["VerticalMesh"])
                            * self.drawingConfig["SCALE_RATIO"]
                            * self.drawingConfig["VERTICAL_SCALE_BAR"]
                    )
                ]
                self.pos4 = [-self.pos3[0], self.pos3[1]]
                self.poss_write_to_adoc([self.pos1, self.pos2, self.pos3, self.pos4])
                self.cache_data_four_dots(args)
                self.mark_down(
                    args["HorizontalMesh"],
                    self.pre_draw_data["tilesUpLineMidPoint"],
                    self.drawingConfig["FORM_WORD_HEIGHT"],
                    7,
                    [self.drawingConfig["ANNOTATED_OFFSETS"], 2])
                self.mark_down(
                    str(int(mesh_len)),
                    self.pre_draw_data["tilesDownLineMidPoint"],
                    self.drawingConfig["FORM_WORD_HEIGHT"],
                    1,
                    [self.drawingConfig["ANNOTATED_OFFSETS"], 1])
                self.mark_down(
                    args["CuttingSlope"],
                    self.pre_draw_data["tilesRightLineMidPoint"],
                    self.drawingConfig["WORD_HEIGHT"],
                    7,
                    [self.drawingConfig["ANNOTATED_OFFSETS"], 4],
                    (2, [self.pre_draw_data["tilesHeight"], self.pre_draw_data["tilesRightLineLength"]])
                )
                self.mult_mark_down(
                    self.cutting_slope_data,
                    self.pre_draw_data["tilesRightLineMidPoint"][:],
                    self.drawingConfig["WORD_HEIGHT"],
                    9,
                    [self.drawingConfig["ANNOTATED_OFFSETS"] * 4, 4])
                self.draw_sheet_two(args)
                self.around_view_msp(is_start=True)
                self.cut_start_to_end_dict = {"N": 0, "T": 0, "B": 0}
            elif args["partType"] == "wing-body":
                self.pos1 = self.pre_draw_data["tilesPoss"][3]
                self.pos2 = self.pre_draw_data["tilesPoss"][2]
                mesh_len = ""
                if args["CuttingSlope"][0] == args["CuttingSlope"][-1]:
                    self.pos3 = [
                        self.pos2[0]
                        , self.pos2[1] - (
                                float(args["MetricParameters"])
                                * float(args["VerticalMesh"])
                                * self.drawingConfig["SCALE_RATIO"]
                                * self.drawingConfig["VERTICAL_SCALE_BAR"]
                        )
                    ]
                    self.pos4 = [self.pos1[0], self.pos3[1]]
                    self.cut_start_to_end_dict = {"N": 0, "T": 0, "B": 0}
                else:
                    mesh_len = (float(args["HorizontalMesh"])
                                - self.cut_start_to_end_dict["T"]
                                - (self.cut_start_to_end_dict["B"]
                                   * 2))  # 计算 计算后的横向目数
                    mesh_len_ratio = mesh_len / float(args["HorizontalMesh"])  # 计算横向目数比 <1
                    self.pos3 = [
                        self.center_line_pos_list[0]
                        + (
                            ((
                                     self.pre_draw_data["tilesDownLineLength"] * mesh_len_ratio
                             )
                             / 2).__ceil__()
                        )
                        , self.pos2[1]
                        - (
                                float(args["MetricParameters"])
                                * float(args["VerticalMesh"])
                                * self.drawingConfig["SCALE_RATIO"]
                                * self.drawingConfig["VERTICAL_SCALE_BAR"]
                        )
                    ]
                    self.pos4 = [-self.pos3[0], self.pos3[1]]
                self.poss_write_to_adoc([self.pos1, self.pos2, self.pos3, self.pos4])
                self.cache_data_four_dots(args)
                if mesh_len != "":
                    self.mark_down(
                        args["HorizontalMesh"],
                        self.pre_draw_data["tilesUpLineMidPoint"],
                        self.drawingConfig["FORM_WORD_HEIGHT"],
                        7,
                        [self.drawingConfig["ANNOTATED_OFFSETS"], 2])

                    self.mark_down(
                        str(int(mesh_len)),
                        self.pre_draw_data["tilesDownLineMidPoint"],
                        self.drawingConfig["FORM_WORD_HEIGHT"],
                        1,
                        [self.drawingConfig["ANNOTATED_OFFSETS"], 1])
                    self.mark_down(
                        args["CuttingSlope"],
                        self.pre_draw_data["tilesRightLineMidPoint"],
                        self.drawingConfig["WORD_HEIGHT"],
                        7,
                        [self.drawingConfig["ANNOTATED_OFFSETS"], 4],
                        (2, [self.pre_draw_data["tilesHeight"], self.pre_draw_data["tilesRightLineLength"]])
                    )
                    self.mult_mark_down(
                        self.cutting_slope_data,
                        self.pre_draw_data["tilesRightLineMidPoint"],
                        self.drawingConfig["WORD_HEIGHT"],
                        9,
                        [self.drawingConfig["ANNOTATED_OFFSETS"] * 4, 4])
                self.draw_sheet_two(args)
                self.around_view_msp()  # 更新视图参数信息
                self.advance_current_msp()
                self.cut_start_to_end_dict = {"N": 0, "T": 0, "B": 0}

            elif args["CurrentNumberOfSegments"] == 1 and args["partType"] == "wing-left":
                mesh_len = float(self.position_stack[0]["args"]["HorizontalMesh"])
                mesh_len_ratio = float(args["HorizontalMesh"]) / mesh_len  # 计算横向目数比 >1
                self.pos4 = self.position_stack[0]["tilesPoss"][0]
                self.pos3 = self.center_line_pos_list[0:2]
                self.pos1 = [
                    self.center_line_pos_list[0]
                    - (
                            (mesh_len_ratio * self.position_stack[0]["tilesUpLineLength"]) / 2
                    )
                    , self.center_line_pos_list[1]
                    + (
                            float(args["MetricParameters"])
                            * float(args["VerticalMesh"])
                            * self.drawingConfig["SCALE_RATIO"]
                            * self.drawingConfig["VERTICAL_SCALE_BAR"]
                    )
                ]
                self.pos2 = [self.center_line_pos_list[0], self.pos1[1]]
                print("网口段， self.pos1", self.pos1)
                print("网口段， self.pos4", self.pos4)
                print("左边线中点， self.pos4", self.midpoint_(self.pos1, self.pos4))
                self.poss_write_to_adoc([self.pos1, self.pos2, self.pos3, self.pos4])
                self.cache_data_four_dots(args)
                self.mark_down(
                    args["HorizontalMesh"],
                    self.pre_draw_data["tilesUpLineMidPoint"],
                    self.drawingConfig["FORM_WORD_HEIGHT"],
                    7,
                    [self.drawingConfig["ANNOTATED_OFFSETS"], 2])
                self.mark_down(
                    str(int(mesh_len)),
                    self.pre_draw_data["tilesDownLineMidPoint"],
                    self.drawingConfig["FORM_WORD_HEIGHT"],
                    1,
                    [self.drawingConfig["ANNOTATED_OFFSETS"], 1])
                if args["MarkSwitch"]:
                    self.mark_down(
                        args["CuttingSlope"],
                        self.pre_draw_data["tilesLeftLineMidPoint"],
                        self.drawingConfig["WORD_HEIGHT"],
                        7,
                        [self.drawingConfig["ANNOTATED_OFFSETS"], 3],
                        (1, [self.pre_draw_data["tilesHeight"], self.pre_draw_data["tilesLeftLineLength"]])
                    )
                self.mult_mark_down(
                    self.cutting_slope_data,
                    self.pre_draw_data["tilesLeftLineMidPoint"][:],
                    self.drawingConfig["WORD_HEIGHT"],
                    9,
                    [self.drawingConfig["ANNOTATED_OFFSETS"] * 12, 3])
                self.draw_sheet_two(args)
                self.around_view_msp(is_start=True)
                self.cut_start_to_end_dict = {"N": 0, "T": 0, "B": 0}
            elif args["partType"] == "wing-left":
                self.confirm_the_eye_clipping_slope__two(args)
                self.calculate_the_eye_ratio(args)
                mesh_len = (float(args["HorizontalMesh"])
                            + self.cut_start_to_end_dict["T"]
                            + self.cut_start_to_end_dict["B"]
                            - self.eye_cut_start_to_end_dict["T"]
                            - self.eye_cut_start_to_end_dict["B"])  # 计算 计算后的横向目数
                print("网翼计算结果目大")
                mesh_len_ratio = mesh_len / float(args["HorizontalMesh"])  # 计算横向目数比 <1
                self.pos4 = self.pre_draw_data["tilesPoss"][0]
                if args["CurrentNumberOfSegments"] == 2:
                    self.pos3 = [
                        self.pos4[0]
                        + (
                                (float(args["HorizontalMesh"]) / (
                                        float(self.pre_draw_data["args"]["HorizontalMesh"]) / 2))  # 横向目数比 < 1
                                * self.pre_draw_data["tilesUpLineLength"]
                        )
                        , self.pos4[1]
                    ]
                else:
                    self.pos3 = self.pre_draw_data["tilesPoss"][1]
                if args["CuttingSlope"][0] != args["CuttingSlope"][-1]:
                    self.pos1 = [
                        self.pos4[0]
                        - (
                                (float(args["VerticalMesh"]) / float(args["CuttingSlope"][0])) * float(
                            args["CuttingSlope"][-1])
                        )
                        , self.pos4[1]
                        + (
                                float(args["MetricParameters"])
                                * float(args["VerticalMesh"])
                                * self.drawingConfig["SCALE_RATIO"]
                                * self.drawingConfig["VERTICAL_SCALE_BAR"]
                        )
                    ]
                    self.pos2 = [
                        self.pos1[0] + (
                                mesh_len_ratio * (self.pos3[0] - self.pos4[0])
                        )
                        , self.pos1[1]
                    ]
                else:
                    mesh_len = (float(args["HorizontalMesh"])
                                - self.eye_cut_start_to_end_dict["T"]
                                - (self.eye_cut_start_to_end_dict["B"]) * 2)
                    mesh_len_ratio = mesh_len / float(args["HorizontalMesh"])
                    self.pos1 = [
                        self.pos4[0]
                        + ((float(args["HorizontalMesh"]) - mesh_len) / 2)
                        , self.pos4[1]
                        + (
                                float(args["MetricParameters"])
                                * float(args["VerticalMesh"])
                                * self.drawingConfig["SCALE_RATIO"]
                                * self.drawingConfig["VERTICAL_SCALE_BAR"]
                        )
                    ]
                    self.pos2 = [
                        self.pos1[0] + (
                                mesh_len_ratio * self.pre_draw_data["tilesUpLineLength"]
                        )
                        , self.pos1[1]
                    ]
                self.poss_write_to_adoc([self.pos1, self.pos2, self.pos3, self.pos4])
                self.cache_data_four_dots(args)
                self.mark_down(
                    args["HorizontalMesh"],
                    self.pre_draw_data["tilesDownLineMidPoint"],
                    self.drawingConfig["FORM_WORD_HEIGHT"],
                    1,
                    [self.drawingConfig["ANNOTATED_OFFSETS"], 1])
                if args["CuttingSlope"][0] != args["CuttingSlope"][-1]:
                    self.mark_down(
                        str(int(mesh_len)),
                        self.pre_draw_data["tilesUpLineMidPoint"],
                        self.drawingConfig["FORM_WORD_HEIGHT"],
                        7,
                        [self.drawingConfig["ANNOTATED_OFFSETS"], 2])
                else:
                    self.mark_down(
                        str(int(mesh_len)),
                        self.pre_draw_data["tilesUpLineMidPoint"],
                        self.drawingConfig["FORM_WORD_HEIGHT"],
                        1,
                        [self.drawingConfig["ANNOTATED_OFFSETS"], 1])
                self.mark_down(
                    args["EyeCuttingSlope"],
                    self.pre_draw_data["tilesRightLineMidPoint"],
                    self.drawingConfig["WORD_HEIGHT"],
                    7,
                    [self.drawingConfig["ANNOTATED_OFFSETS"] * 2, 4],
                    (1, [self.pre_draw_data["tilesHeight"], self.pre_draw_data["tilesRightLineLength"]])
                )
                if args["MarkSwitch"]:
                    self.mark_down(
                        args["CuttingSlope"],
                        self.pre_draw_data["tilesLeftLineMidPoint"],
                        self.drawingConfig["WORD_HEIGHT"],
                        7,
                        [self.drawingConfig["ANNOTATED_OFFSETS"] * 2, 3],
                        (1, [self.pre_draw_data["tilesHeight"], self.pre_draw_data["tilesLeftLineLength"]])
                    )
                if args["MarkSlopeSwitch"]:
                    self.mult_mark_down(
                        self.cutting_slope_data,
                        self.pre_draw_data["tilesLeftLineMidPoint"][:],
                        self.drawingConfig["WORD_HEIGHT"],
                        9,
                        [self.drawingConfig["ANNOTATED_OFFSETS"] * 12, 3])
                self.draw_sheet_two(args)
                self.around_view_msp()
                self.cut_start_to_end_dict = {"N": 0, "T": 0, "B": 0}
                self.eye_cut_start_to_end_dict = {"N": 0, "T": 0, "B": 0}
            elif args["CurrentNumberOfSegments"] == 1 and args["partType"] == "wing-right":
                self.confirm_the_eye_clipping_slope__two(args)
                self.calculate_the_eye_ratio(args)
                mesh_len = (float(args["HorizontalMesh"])
                            + self.cut_start_to_end_dict["T"]
                            + self.cut_start_to_end_dict["B"]
                            - self.eye_cut_start_to_end_dict["T"]
                            - self.eye_cut_start_to_end_dict["B"])  # 计算 计算后的横向目数
                mesh_len_ratio = mesh_len / float(args["HorizontalMesh"])  # 计算横向目数比 <1
                self.pos3 = self.position_stack[0]["tilesPoss"][1]
                self.pos4 = [
                    self.pos3[0]
                    - (
                            ((float(args["HorizontalMesh"]) / (
                                    float(self.position_stack[0]["args"]["HorizontalMesh"]) / 2))  # 横向目数比 < 1
                             * self.position_stack[0]["tilesUpLineLength"]) / 2
                    )
                    , self.pos3[1]
                ]
                self.pos2 = [
                    self.pos3[0]
                    + (
                            (float(args["VerticalMesh"]) / float(args["CuttingSlope"][0])) * float(
                        args["CuttingSlope"][-1])
                    )
                    , self.pos3[1]
                    + (
                            float(args["MetricParameters"])
                            * float(args["VerticalMesh"])
                            * self.drawingConfig["SCALE_RATIO"]
                            * self.drawingConfig["VERTICAL_SCALE_BAR"]
                    )
                ]
                self.pos1 = [
                    self.pos2[0]
                    - (
                            mesh_len_ratio * (self.pos3[0] - self.pos4[0])
                    )
                    , self.pos2[1]
                ]
                self.poss_write_to_adoc([self.pos1, self.pos2, self.pos3, self.pos4])
                self.cache_data_four_dots(args)
                self.mark_down(
                    F"({args['HorizontalMesh']})",
                    self.pre_draw_data["tilesDownLineMidPoint"],
                    self.drawingConfig["FORM_WORD_HEIGHT"],
                    1,
                    [self.drawingConfig["ANNOTATED_OFFSETS"], 1])
                self.mark_down(
                    str(int(mesh_len)),
                    self.pre_draw_data["tilesUpLineMidPoint"],
                    self.drawingConfig["FORM_WORD_HEIGHT"],
                    7,
                    [self.drawingConfig["ANNOTATED_OFFSETS"], 2])
                self.mark_down(
                    args["EyeCuttingSlope"],
                    self.pre_draw_data["tilesLeftLineMidPoint"],
                    self.drawingConfig["WORD_HEIGHT"],
                    7,
                    [self.drawingConfig["ANNOTATED_OFFSETS"] * 2, 3],
                    (2, [self.pre_draw_data["tilesHeight"], self.pre_draw_data["tilesLeftLineLength"]])
                )
                if args["MarkSwitch"]:
                    self.mark_down(
                        args["CuttingSlope"],
                        self.pre_draw_data["tilesRightLineMidPoint"],
                        self.drawingConfig["WORD_HEIGHT"],
                        7,
                        [self.drawingConfig["ANNOTATED_OFFSETS"] * 2, 3],
                        (2, [self.pre_draw_data["tilesHeight"], self.pre_draw_data["tilesRightLineLength"]])
                    )
                if args["MarkSlopeSwitch"]:
                    self.mult_mark_down(
                        self.cutting_slope_data,
                        self.pre_draw_data["tilesRightLineMidPoint"][:],
                        self.drawingConfig["WORD_HEIGHT"],
                        9,
                        [self.drawingConfig["ANNOTATED_OFFSETS"] * 12, 3])
                self.draw_sheet_two(args, left_sheet=False)
                self.around_view_msp(is_start=True)
                self.cut_start_to_end_dict = {"N": 0, "T": 0, "B": 0}
                self.eye_cut_start_to_end_dict = {"N": 0, "T": 0, "B": 0}
            elif args["partType"] == "wing-right":
                self.confirm_the_eye_clipping_slope__two(args)
                self.calculate_the_eye_ratio(args)
                mesh_len = (float(args["HorizontalMesh"])
                            + self.cut_start_to_end_dict["T"]
                            + self.cut_start_to_end_dict["B"]
                            - self.eye_cut_start_to_end_dict["T"]
                            - self.eye_cut_start_to_end_dict["B"])  # 计算 计算后的横向目数
                mesh_len_ratio = mesh_len / float(args["HorizontalMesh"])  # 计算横向目数比 <1
                self.pos4 = self.pre_draw_data["tilesPoss"][0]
                self.pos3 = self.pre_draw_data["tilesPoss"][1]
                if args["CuttingSlope"][0] != args["CuttingSlope"][-1]:
                    self.pos2 = [
                        self.pos3[0]
                        + (
                                (float(args["VerticalMesh"]) / float(args["CuttingSlope"][0])) * float(
                            args["CuttingSlope"][-1])
                        )
                        , self.pos3[1]
                        + (
                                float(args["MetricParameters"])
                                * float(args["VerticalMesh"])
                                * self.drawingConfig["SCALE_RATIO"]
                                * self.drawingConfig["VERTICAL_SCALE_BAR"]
                        )
                    ]
                    self.pos1 = [
                        self.pos2[0]
                        - (
                                mesh_len_ratio * self.pre_draw_data["tilesUpLineLength"]
                        )
                        , self.pos2[1]
                    ]
                else:
                    mesh_len = (float(args["HorizontalMesh"])
                                - self.eye_cut_start_to_end_dict["T"]
                                - (self.eye_cut_start_to_end_dict["B"]) * 2)
                    mesh_len_ratio = mesh_len / float(args["HorizontalMesh"])
                    self.pos2 = [
                        self.pos3[0]
                        - ((float(args["HorizontalMesh"]) - mesh_len) / 2)
                        , self.pos3[1]
                        + (
                                float(args["MetricParameters"])
                                * float(args["VerticalMesh"])
                                * self.drawingConfig["SCALE_RATIO"]
                                * self.drawingConfig["VERTICAL_SCALE_BAR"]
                        )
                    ]
                    self.pos1 = [
                        self.pos2[0] - (
                                mesh_len_ratio * self.pre_draw_data["tilesUpLineLength"]
                        )
                        , self.pos2[1]
                    ]
                self.poss_write_to_adoc([self.pos1, self.pos2, self.pos3, self.pos4])
                self.cache_data_four_dots(args)
                self.mark_down(
                    args['HorizontalMesh'],
                    self.pre_draw_data["tilesDownLineMidPoint"],
                    self.drawingConfig["FORM_WORD_HEIGHT"],
                    1,
                    [self.drawingConfig["ANNOTATED_OFFSETS"], 1])
                if args["CuttingSlope"][0] != args["CuttingSlope"][-1]:
                    self.mark_down(
                        str(int(mesh_len)),
                        self.pre_draw_data["tilesUpLineMidPoint"],
                        self.drawingConfig["FORM_WORD_HEIGHT"],
                        7,
                        [self.drawingConfig["ANNOTATED_OFFSETS"], 2])
                else:
                    self.mark_down(
                        str(int(mesh_len)),
                        self.pre_draw_data["tilesUpLineMidPoint"],
                        self.drawingConfig["FORM_WORD_HEIGHT"],
                        1,
                        [self.drawingConfig["ANNOTATED_OFFSETS"], 1])
                self.mark_down(
                    args["EyeCuttingSlope"],
                    self.pre_draw_data["tilesLeftLineMidPoint"],
                    self.drawingConfig["WORD_HEIGHT"],
                    7,
                    [self.drawingConfig["ANNOTATED_OFFSETS"] * 2, 3],
                    (1, [self.pre_draw_data["tilesHeight"], self.pre_draw_data["tilesLeftLineLength"]])
                )
                if args["MarkSwitch"]:
                    self.mark_down(
                        args["CuttingSlope"],
                        self.pre_draw_data["tilesRightLineMidPoint"],
                        self.drawingConfig["WORD_HEIGHT"],
                        7,
                        [self.drawingConfig["ANNOTATED_OFFSETS"] * 2, 4],
                        (2, [self.pre_draw_data["tilesHeight"], self.pre_draw_data["tilesRightLineLength"]])
                    )
                if args["MarkSlopeSwitch"]:
                    self.mult_mark_down(
                        self.cutting_slope_data,
                        self.pre_draw_data["tilesRightLineMidPoint"][:],
                        self.drawingConfig["WORD_HEIGHT"],
                        9,
                        [self.drawingConfig["ANNOTATED_OFFSETS"] * 12, 4])
                self.draw_sheet_two(args, left_sheet=False)
                self.around_view_msp()
                self.cut_start_to_end_dict = {"N": 0, "T": 0, "B": 0}
                self.eye_cut_start_to_end_dict = {"N": 0, "T": 0, "B": 0}
        finally:
            self.clean_pos_cache()

    def drawing_four_slices_type(self, args: dict = None) -> None:
        pass

    def drawing_six_slices_type(self, args: dict = None) -> None:
        pass

    def draw_sheet_two(self, args: dict = None, left_sheet=True):
        # self.doc.ActiveLayer.LineType = "ByLayer"
        if left_sheet:
            mark_start_pos = [
                self.center_line_pos_list[0] - (1.5 * self.drawingConfig["TABLE_OFFSET"]),
                self.pre_draw_data["tilesLeftLineMidPoint"][1]
            ]
            self.mark_down(
                args["MetricParameters"],
                mark_start_pos,
                self.drawingConfig["FORM_WORD_HEIGHT"],
                3,
            )
            if args["partType"] == "wing-left" and args["CuttingSlope"][0] == args["CuttingSlope"][-1]:
                self.mark_down(
                    "2a",
                    [mark_start_pos[0], self.pre_draw_data["tilesPoss"][0][1]],
                    self.drawingConfig["FORM_WORD_HEIGHT"],
                    3,
                    [self.drawingConfig["WORD_HEIGHT"], 1]

                )
                line1 = self.msp.AddLightWeightPolyline(listToFloat([
                    self.pre_draw_data["tilesPoss"][2][0] + (0.5 * self.drawingConfig["TABLE_OFFSET"]),
                    self.pre_draw_data["tilesPoss"][2][1],  # 0
                    self.pre_draw_data["tilesPoss"][2][0] + (0.5 * self.drawingConfig["TABLE_OFFSET"]),
                    self.pre_draw_data["tilesPoss"][2][1] + ((float(self.pre_draw_data["tilesHeight"]) / 3) * 2),  # 1
                    self.pre_draw_data["tilesPoss"][2][0] + (0.5 * self.drawingConfig["TABLE_OFFSET"]),
                    self.pre_draw_data["tilesPoss"][2][1] + float(self.pre_draw_data["tilesHeight"]),  # 2
                    self.pre_draw_data["tilesPoss"][2][0] + (0.4 * self.drawingConfig["TABLE_OFFSET"]),
                    self.pre_draw_data["tilesPoss"][2][1] + float(self.pre_draw_data["tilesHeight"]),  # 3
                    self.pre_draw_data["tilesPoss"][2][0] + (0.6 * self.drawingConfig["TABLE_OFFSET"]),
                    self.pre_draw_data["tilesPoss"][2][1] + float(self.pre_draw_data["tilesHeight"]),  # 4
                ]))
                line1.SetWidth(1, 2.0, 0.1)
                self.mark_down("长度1",
                               [
                                   self.pre_draw_data["tilesPoss"][2][0] + (0.5 * self.drawingConfig["TABLE_OFFSET"]),
                                   self.pre_draw_data["tilesPoss"][2][1] + float(self.pre_draw_data["tilesHeight"])
                               ],
                               self.drawingConfig["FORM_WORD_HEIGHT"],
                               1)
            mark_start_pos[0] -= 0.25 * self.drawingConfig["TABLE_OFFSET"]
            self.mark_down(
                self.drawingConfig["MATERIAL"],
                mark_start_pos,
                self.drawingConfig["FORM_WORD_HEIGHT"],
                3,
            )
            if args["partType"] == "wing-left" and args["CuttingSlope"][0] == args["CuttingSlope"][-1]:
                self.mark_down(
                    "MAT",
                    [mark_start_pos[0], self.pre_draw_data["tilesPoss"][0][1]],
                    self.drawingConfig["FORM_WORD_HEIGHT"],
                    3,
                    [self.drawingConfig["WORD_HEIGHT"], 1]

                )
            mark_start_pos[0] -= 0.25 * self.drawingConfig["TABLE_OFFSET"]
            self.mark_down(
                self.pre_draw_data["tilesHeight"] / 10,
                mark_start_pos,
                self.drawingConfig["FORM_WORD_HEIGHT"],
                3,
            )
            if args["partType"] == "wing-left" and args["CuttingSlope"][0] == args["CuttingSlope"][-1]:
                self.mark_down(
                    "NL",
                    [mark_start_pos[0], self.pre_draw_data["tilesPoss"][0][1]],
                    self.drawingConfig["FORM_WORD_HEIGHT"],
                    3,
                    [self.drawingConfig["WORD_HEIGHT"], 1]
                )
            mark_start_pos[0] -= 0.25 * self.drawingConfig["TABLE_OFFSET"]
            self.mark_down(
                args["VerticalMesh"],
                mark_start_pos,
                self.drawingConfig["FORM_WORD_HEIGHT"],
                3,
            )
            if args["partType"] == "wing-left" and args["CuttingSlope"][0] == args["CuttingSlope"][-1]:
                point = self.msp.AddPoint(listToFloat(
                    [mark_start_pos[0], self.pre_draw_data["tilesPoss"][0][1] + self.drawingConfig["WORD_HEIGHT"], 0]))
                point.Rotate(listToFloat(
                    [mark_start_pos[0], self.pre_draw_data["tilesPoss"][0][1] + self.drawingConfig["WORD_HEIGHT"], 0]),
                    55)
                self.doc.SetVariable("PDMODE", 65)
                self.doc.SetVariable("PDSIZE", 2)

            self.doc.ActiveLayer.LineType = "Continuous"
            ori_layer = self.doc.ActiveLayer
            dot_layer = self.doc.Layers.Add("DottedLineLayer")
            self.doc.ActiveLayer = dot_layer
            self.doc.ActiveLayer.LineType = "ACAD_ISO04W100"
            self.msp.AddLightWeightPolyline(listToFloat([
                self.pre_draw_data["tilesPoss"][0][0] - (0.5 * self.drawingConfig["TABLE_OFFSET"]),
                self.pre_draw_data["tilesPoss"][0][1],
                self.center_line_pos_list[0] - (2.25 * self.drawingConfig["TABLE_OFFSET"]),
                self.pre_draw_data["tilesPoss"][0][1]
            ]))
            cutting_slope_list = re.findall(r'\d+\.\d+|\d+', args["CuttingSlope"])
            if cutting_slope_list[0] == cutting_slope_list[1]:
                self.msp.AddLightWeightPolyline(listToFloat([
                    self.pre_draw_data["tilesPoss"][3][0] - (0.5 * self.drawingConfig["TABLE_OFFSET"]),
                    self.pre_draw_data["tilesPoss"][3][1],
                    self.center_line_pos_list[0] - (2.25 * self.drawingConfig["TABLE_OFFSET"]),
                    self.pre_draw_data["tilesPoss"][3][1]
                ]))
            self.doc.ActiveLayer = ori_layer
            self.msp.AddLightWeightPolyline(listToFloat([
                self.center_line_pos_list[0] - (2.125 * self.drawingConfig["TABLE_OFFSET"]),
                self.pre_draw_data["tilesPoss"][0][1],
                self.center_line_pos_list[0] - (2.125 * self.drawingConfig["TABLE_OFFSET"]),
                self.pre_draw_data["tilesPoss"][3][1],
            ]))
            if args["partType"] == "wing-left" and args["EyeCuttingSlope"][0] != args["EyeCuttingSlope"][-1] and args[
                "EyeCuttingSlope"] not in self.eye_cut_slope_mark_data[1]:
                if not self.eye_cut_slope_mark_data[0]:
                    self.eye_cut_slope_mark_data[0] = [
                        self.center_line_pos_list[0] + (1.75 * self.drawingConfig["TABLE_OFFSET"]),
                        self.center_line_pos_list[1] - self.drawingConfig["FORM_WORD_HEIGHT"]
                    ]
                self.eye_cutting_slope_data.insert(0, args["EyeCuttingSlope"])
                self.eye_cutting_slope_data.insert(0, "上袖")
                self.mult_eye_mark_down(
                    self.eye_cutting_slope_data,
                    self.eye_cut_slope_mark_data[0],
                    self.drawingConfig["WORD_HEIGHT"],
                    9,
                )
                self.eye_cut_slope_mark_data[1].append(args["EyeCuttingSlope"])
        else:
            mark_start_pos = [
                self.center_line_pos_list[0] + (1.5 * self.drawingConfig["TABLE_OFFSET"]),
                self.pre_draw_data["tilesRightLineMidPoint"][1]
            ]
            self.mark_down(
                self.drawingConfig["MATERIAL"],
                mark_start_pos,
                self.drawingConfig["FORM_WORD_HEIGHT"],
                3,
            )
            if args["partType"] == "wing-right" and args["CuttingSlope"][0] == args["CuttingSlope"][-1]:
                self.mark_down(
                    "MAT",
                    [mark_start_pos[0], self.pre_draw_data["tilesPoss"][0][1]],
                    self.drawingConfig["FORM_WORD_HEIGHT"],
                    3,
                    [self.drawingConfig["WORD_HEIGHT"], 1]

                )
                line1 = self.msp.AddLightWeightPolyline(listToFloat([
                    self.pre_draw_data["tilesPoss"][1][0] - (0.5 * self.drawingConfig["TABLE_OFFSET"]),
                    self.pre_draw_data["tilesPoss"][1][1],  # 0
                    self.pre_draw_data["tilesPoss"][1][0] - (0.5 * self.drawingConfig["TABLE_OFFSET"]),
                    self.pre_draw_data["tilesPoss"][1][1] - ((float(self.pre_draw_data["tilesHeight"]) / 3) * 2),  # 1
                    self.pre_draw_data["tilesPoss"][1][0] - (0.5 * self.drawingConfig["TABLE_OFFSET"]),
                    self.pre_draw_data["tilesPoss"][1][1] - float(self.pre_draw_data["tilesHeight"]),  # 2
                    self.pre_draw_data["tilesPoss"][1][0] - (0.4 * self.drawingConfig["TABLE_OFFSET"]),
                    self.pre_draw_data["tilesPoss"][1][1] - float(self.pre_draw_data["tilesHeight"]),  # 3
                    self.pre_draw_data["tilesPoss"][1][0] - (0.6 * self.drawingConfig["TABLE_OFFSET"]),
                    self.pre_draw_data["tilesPoss"][1][1] - float(self.pre_draw_data["tilesHeight"]),  # 4
                ]))
                line1.SetWidth(1, 2.0, 0.1)
                self.mark_down("长度2",
                               [
                                   self.pre_draw_data["tilesPoss"][1][0] - (0.5 * self.drawingConfig["TABLE_OFFSET"]),
                                   self.pre_draw_data["tilesPoss"][1][1] - float(self.pre_draw_data["tilesHeight"])
                               ],
                               self.drawingConfig["FORM_WORD_HEIGHT"],
                               7)
            mark_start_pos[0] += 0.25 * self.drawingConfig["TABLE_OFFSET"]
            self.mark_down(
                self.pre_draw_data["tilesHeight"] / 10,
                mark_start_pos,
                self.drawingConfig["FORM_WORD_HEIGHT"],
                3,
            )
            if args["partType"] == "wing-right" and args["CuttingSlope"][0] == args["CuttingSlope"][-1]:
                self.mark_down(
                    "NL",
                    [mark_start_pos[0], self.pre_draw_data["tilesPoss"][0][1]],
                    self.drawingConfig["FORM_WORD_HEIGHT"],
                    3,
                    [self.drawingConfig["WORD_HEIGHT"], 1]

                )
            mark_start_pos[0] += 0.25 * self.drawingConfig["TABLE_OFFSET"]
            self.mark_down(
                args["VerticalMesh"],
                mark_start_pos,
                self.drawingConfig["FORM_WORD_HEIGHT"],
                3,
            )
            if args["partType"] == "wing-right" and args["CuttingSlope"][0] == args["CuttingSlope"][-1]:
                point = self.msp.AddPoint(listToFloat(
                    [mark_start_pos[0], self.pre_draw_data["tilesPoss"][0][1] + self.drawingConfig["WORD_HEIGHT"], 0]))
                point.Rotate(listToFloat(
                    [mark_start_pos[0], self.pre_draw_data["tilesPoss"][0][1] + self.drawingConfig["WORD_HEIGHT"], 0]),
                    55)
                self.doc.SetVariable("PDMODE", 65)
                self.doc.SetVariable("PDSIZE", 2)

            self.doc.ActiveLayer.LineType = "Continuous"
            ori_layer = self.doc.ActiveLayer
            dot_layer = self.doc.Layers.Add("DottedLineLayer")
            self.doc.ActiveLayer = dot_layer
            self.doc.ActiveLayer.LineType = "ACAD_ISO04W100"
            self.msp.AddLightWeightPolyline(listToFloat([
                self.pre_draw_data["tilesPoss"][1][0] + (0.5 * self.drawingConfig["TABLE_OFFSET"]),
                self.pre_draw_data["tilesPoss"][1][1],
                self.center_line_pos_list[0] + (2.25 * self.drawingConfig["TABLE_OFFSET"]),
                self.pre_draw_data["tilesPoss"][1][1]
            ]))
            if int(args["CurrentNumberOfSegments"]) == 1:
                self.msp.AddLightWeightPolyline(listToFloat([
                    self.pre_draw_data["tilesPoss"][2][0] + (0.5 * self.drawingConfig["TABLE_OFFSET"]),
                    self.pre_draw_data["tilesPoss"][2][1],
                    self.center_line_pos_list[0] + (2.25 * self.drawingConfig["TABLE_OFFSET"]),
                    self.pre_draw_data["tilesPoss"][2][1]
                ]))
            self.doc.ActiveLayer = ori_layer
            self.msp.AddLightWeightPolyline(listToFloat([
                self.center_line_pos_list[0] + (1.875 * self.drawingConfig["TABLE_OFFSET"]),
                self.pre_draw_data["tilesPoss"][0][1],
                self.center_line_pos_list[0] + (1.875 * self.drawingConfig["TABLE_OFFSET"]),
                self.pre_draw_data["tilesPoss"][3][1],
            ]))
            if args["partType"] == "wing-right" and args["EyeCuttingSlope"][0] != args["EyeCuttingSlope"][-1] and args[
                "EyeCuttingSlope"] not in self.eye_cut_slope_mark_data[2]:
                if not self.eye_cut_slope_mark_data[0]:
                    self.eye_cut_slope_mark_data[0] = [
                        self.center_line_pos_list[0] + (1.75 * self.drawingConfig["TABLE_OFFSET"]),
                        self.center_line_pos_list[1] - self.drawingConfig["FORM_WORD_HEIGHT"]
                    ]
                self.eye_cutting_slope_data.insert(0, args["EyeCuttingSlope"])
                self.eye_cutting_slope_data.insert(0, "下袖")
                self.mult_eye_mark_down(
                    self.eye_cutting_slope_data,
                    self.eye_cut_slope_mark_data[0],
                    self.drawingConfig["WORD_HEIGHT"],
                    9,
                )
                self.eye_cut_slope_mark_data[2].append(args["EyeCuttingSlope"])

    def confirm_the_clipping_slope__two(self, args: dict = None) -> None:
        temp_slope_data_1 = int(args["CuttingSlope"][0])
        temp_slope_data_2 = int(args["CuttingSlope"][-1])
        self.cutting_slope_data = []
        match temp_slope_data_1:
            case 1:
                self.cutting_slope_data = cut_slope["1-1"]["1"]["NAN"][:]
            case 2:
                if float(args["VerticalMesh"]) % temp_slope_data_1 <= 0.5:
                    self.cutting_slope_data = cut_slope["2-1"]["2"]["0.5"][:]
                elif float(args["VerticalMesh"]) % temp_slope_data_1 <= 1.5:
                    self.cutting_slope_data = cut_slope["2-1"]["2"]["1.5"][:]
                else:
                    self.cutting_slope_data = ["null"]
            case 3:
                if temp_slope_data_2 == 1:
                    if float(args["VerticalMesh"]) % temp_slope_data_1 <= 0.5:
                        self.cutting_slope_data = cut_slope["3-1"]["3"]["0.5"][:]
                    elif float(args["VerticalMesh"]) % temp_slope_data_1 <= 1.5:
                        self.cutting_slope_data = cut_slope["3-1"]["3"]["1.5"][:]
                    elif float(args["VerticalMesh"]) % temp_slope_data_1 <= 2.5:
                        self.cutting_slope_data = cut_slope["3-1"]["3"]["2.5"][:]
                    else:
                        self.cutting_slope_data = ["null"]
                elif temp_slope_data_2 == 2:
                    if float(args["VerticalMesh"]) % temp_slope_data_1 <= 0.5:
                        self.cutting_slope_data = cut_slope["3-2"]["3"]["0.5"][:]
                    elif float(args["VerticalMesh"]) % temp_slope_data_1 <= 1.5:
                        self.cutting_slope_data = cut_slope["3-2"]["3"]["1.5"][:]
                    elif float(args["VerticalMesh"]) % temp_slope_data_1 <= 2.5:
                        self.cutting_slope_data = cut_slope["3-2"]["3"]["2.5"][:]
                    else:
                        self.cutting_slope_data = ["null"]
                else:
                    print("暂不支持该剪切斜率")
            case 4:
                if temp_slope_data_2 == 1:
                    if float(args["VerticalMesh"]) % temp_slope_data_1 <= 0.5:
                        self.cutting_slope_data = cut_slope["4-1"]["4"]["0.5"][:]
                    elif float(args["VerticalMesh"]) % temp_slope_data_1 <= 1.5:
                        self.cutting_slope_data = cut_slope["4-1"]["4"]["1.5"][:]
                    elif float(args["VerticalMesh"]) % temp_slope_data_1 <= 2.5:
                        self.cutting_slope_data = cut_slope["4-1"]["4"]["2.5"][:]
                    elif float(args["VerticalMesh"]) % temp_slope_data_1 <= 3.5:
                        self.cutting_slope_data = cut_slope["4-1"]["4"]["3.5"][:]
                    else:
                        self.cutting_slope_data = ["null"]

                elif temp_slope_data_2 == 3:
                    if float(args["VerticalMesh"]) % temp_slope_data_1 <= 0.5:
                        self.cutting_slope_data = cut_slope["4-3"]["4"]["0.5"][:]
                    elif float(args["VerticalMesh"]) % temp_slope_data_1 <= 1.5:
                        self.cutting_slope_data = cut_slope["4-3"]["4"]["1.5"][:]
                    elif float(args["VerticalMesh"]) % temp_slope_data_1 <= 2.5:
                        self.cutting_slope_data = cut_slope["4-3"]["4"]["2.5"][:]
                    elif float(args["VerticalMesh"]) % temp_slope_data_1 <= 3.5:
                        self.cutting_slope_data = cut_slope["4-3"]["4"]["3.5"][:]
                    else:
                        self.cutting_slope_data = ["null"]
                else:
                    print("暂不支持该剪切斜率")
            case 5:
                if temp_slope_data_2 == 1:
                    if float(args["VerticalMesh"]) % temp_slope_data_1 <= 0.5:
                        self.cutting_slope_data = cut_slope["5-1"]["5"]["0.5"][:]
                    elif float(args["VerticalMesh"]) % temp_slope_data_1 <= 1.5:
                        self.cutting_slope_data = cut_slope["5-1"]["5"]["1.5"][:]
                    elif float(args["VerticalMesh"]) % temp_slope_data_1 <= 2.5:
                        self.cutting_slope_data = cut_slope["5-1"]["5"]["2.5"][:]
                    elif float(args["VerticalMesh"]) % temp_slope_data_1 <= 3.5:
                        self.cutting_slope_data = cut_slope["5-1"]["5"]["3.5"][:]
                    elif float(args["VerticalMesh"]) % temp_slope_data_1 <= 4.5:
                        self.cutting_slope_data = cut_slope["5-1"]["5"]["4.5"][:]
                    else:
                        self.cutting_slope_data = ["null"]
                elif temp_slope_data_2 == 3:
                    if float(args["VerticalMesh"]) % temp_slope_data_1 <= 0.5:
                        self.cutting_slope_data = cut_slope["5-3"]["5"]["0.5"][:]
                    elif float(args["VerticalMesh"]) % temp_slope_data_1 <= 1.5:
                        self.cutting_slope_data = cut_slope["5-3"]["5"]["1.5"][:]
                    elif float(args["VerticalMesh"]) % temp_slope_data_1 <= 2.5:
                        self.cutting_slope_data = cut_slope["5-3"]["5"]["2.5"][:]
                    elif float(args["VerticalMesh"]) % temp_slope_data_1 <= 3.5:
                        self.cutting_slope_data = cut_slope["5-3"]["5"]["3.5"][:]
                    elif float(args["VerticalMesh"]) % temp_slope_data_1 <= 4.5:
                        self.cutting_slope_data = cut_slope["5-3"]["5"]["4.5"][:]
                    else:
                        self.cutting_slope_data = ["null"]
            case 7:
                if temp_slope_data_2 == 1:
                    if float(args["VerticalMesh"]) % temp_slope_data_1 <= 0.5:
                        self.cutting_slope_data = cut_slope["7-1"]["7"]["0.5"][:]
                    elif float(args["VerticalMesh"]) % temp_slope_data_1 <= 1.5:
                        self.cutting_slope_data = cut_slope["7-1"]["7"]["1.5"][:]
                    elif float(args["VerticalMesh"]) % temp_slope_data_1 <= 2.5:
                        self.cutting_slope_data = cut_slope["7-1"]["7"]["2.5"][:]
                    elif float(args["VerticalMesh"]) % temp_slope_data_1 <= 3.5:
                        self.cutting_slope_data = cut_slope["7-1"]["7"]["3.5"][:]
                    elif float(args["VerticalMesh"]) % temp_slope_data_1 <= 4.5:
                        self.cutting_slope_data = cut_slope["7-1"]["7"]["4.5"][:]
                    elif float(args["VerticalMesh"]) % temp_slope_data_1 <= 5.5:
                        self.cutting_slope_data = cut_slope["7-1"]["7"]["5.5"][:]
                    elif float(args["VerticalMesh"]) % temp_slope_data_1 <= 6.5:
                        self.cutting_slope_data = cut_slope["7-1"]["7"]["6.5"][:]
                    else:
                        self.cutting_slope_data = ["null"]

            case 8:
                if temp_slope_data_2 == 1:
                    if float(args["VerticalMesh"]) % temp_slope_data_1 <= 0.5:
                        self.cutting_slope_data = cut_slope["8-1"]["8"]["0.5"][:]
                    elif float(args["VerticalMesh"]) % temp_slope_data_1 <= 1.5:
                        self.cutting_slope_data = cut_slope["8-1"]["8"]["1.5"][:]
                    elif float(args["VerticalMesh"]) % temp_slope_data_1 <= 2.5:
                        self.cutting_slope_data = cut_slope["8-1"]["8"]["2.5"][:]
                    elif float(args["VerticalMesh"]) % temp_slope_data_1 <= 3.5:
                        self.cutting_slope_data = cut_slope["8-1"]["8"]["3.5"][:]
                    elif float(args["VerticalMesh"]) % temp_slope_data_1 <= 4.5:
                        self.cutting_slope_data = cut_slope["8-1"]["8"]["4.5"][:]
                    elif float(args["VerticalMesh"]) % temp_slope_data_1 <= 5.5:
                        self.cutting_slope_data = cut_slope["8-1"]["8"]["5.5"][:]
                    elif float(args["VerticalMesh"]) % temp_slope_data_1 <= 6.5:
                        self.cutting_slope_data = cut_slope["8-1"]["8"]["6.5"][:]
                    elif float(args["VerticalMesh"]) % temp_slope_data_1 <= 7.5:
                        self.cutting_slope_data = cut_slope["8-1"]["8"]["7.5"][:]
                    else:
                        self.cutting_slope_data = ["null"]

    def confirm_the_eye_clipping_slope__two(self, args: dict = None) -> None:
        temp_slope_data_1 = int(args["EyeCuttingSlope"][0])
        temp_slope_data_2 = int(args["EyeCuttingSlope"][-1])
        match temp_slope_data_1:
            case 1:
                if temp_slope_data_2 == 1:
                    self.eye_cutting_slope_data = eye_cut_slope["1-1"]["1"]["NAN"][:]
                elif temp_slope_data_2 == 2:
                    if float(args["VerticalMesh"]) % temp_slope_data_1 <= 0.5:
                        self.eye_cutting_slope_data = eye_cut_slope["1-2"]["1"]["0.5"][:]
                    else:
                        self.eye_cutting_slope_data = ["null"]
                        print("self.eye_cutting_slope_data = ['null']")
                elif temp_slope_data_2 == 3:
                    if float(args["VerticalMesh"]) % temp_slope_data_1 <= 0.5:
                        self.eye_cutting_slope_data = eye_cut_slope["1-3"]["1"]["0.5"][:]
                    else:
                        self.eye_cutting_slope_data = ["null"]
                        print("self.eye_cutting_slope_data = ['null']")

            case 2:
                if float(args["VerticalMesh"]) % temp_slope_data_1 <= 0.5:
                    self.eye_cutting_slope_data = eye_cut_slope["2-3"]["2"]["0.5"][:]
                elif float(args["VerticalMesh"]) % temp_slope_data_1 <= 1.5:
                    self.eye_cutting_slope_data = eye_cut_slope["2-3"]["2"]["1.5"][:]
                else:
                    self.eye_cutting_slope_data = ["null"]
                    print("self.eye_cutting_slope_data = ['null']")

    def calculate_the_ratio(self, args):
        # 计算起剪数据
        if isinstance(self.cutting_slope_data[0], str):
            number_list = re.findall(r'\d+\.\d+|\d+', self.cutting_slope_data[0])
            if "N" in self.cutting_slope_data[0]:
                self.cut_start_to_end_dict["N"] += float(number_list[0])
            if "T" in self.cutting_slope_data[0]:
                self.cut_start_to_end_dict["T"] += float(number_list[0])
            if "B" in self.cutting_slope_data[0]:
                self.cut_start_to_end_dict["B"] += float(number_list[1]) / 2
                self.cut_start_to_end_dict["N"] += float(number_list[1]) / 2
        elif isinstance(self.cutting_slope_data[0], list):
            for cut_slope_obj in self.cutting_slope_data[0]:
                if isinstance(cut_slope_obj, str):
                    number_list = re.findall(r'\d+\.\d+|\d+', cut_slope_obj)
                    if "N" in cut_slope_obj:
                        self.cut_start_to_end_dict["N"] += float(number_list[0])
                    if "T" in cut_slope_obj:
                        self.cut_start_to_end_dict["T"] += float(number_list[0])
                    if "B" in cut_slope_obj:
                        self.cut_start_to_end_dict["B"] += float(number_list[1]) / 2
                        self.cut_start_to_end_dict["N"] += float(number_list[1]) / 2
        # 计算落剪数据
        if isinstance(self.cutting_slope_data[2], str) and len(self.cutting_slope_data[2]) > 2:
            number_list = re.findall(r'\d+\.\d+|\d+', self.cutting_slope_data[2])
            if "N" in self.cutting_slope_data[2]:
                self.cut_start_to_end_dict["N"] += float(number_list[0])
            if "T" in self.cutting_slope_data[2]:
                self.cut_start_to_end_dict["T"] += float(number_list[0])
            if "B" in self.cutting_slope_data[2]:
                self.cut_start_to_end_dict["B"] += float(number_list[1]) / 2
                self.cut_start_to_end_dict["N"] += float(number_list[1]) / 2
        elif isinstance(self.cutting_slope_data[2], str) and len(self.cutting_slope_data[2]) <= 2:
            number_list = re.findall(r'\d+\.\d+|\d+', self.cutting_slope_data[2])
            if "N" in self.cutting_slope_data[2]:
                self.cut_start_to_end_dict["N"] += float(number_list[0])
            if "T" in self.cutting_slope_data[2]:
                self.cut_start_to_end_dict["T"] += float(number_list[0])
            if "B" in self.cutting_slope_data[2]:
                self.cut_start_to_end_dict["B"] += float(number_list[0]) / 2
                self.cut_start_to_end_dict["N"] += float(number_list[0]) / 2
        elif isinstance(self.cutting_slope_data[2], list):
            for cut_slope_obj in self.cutting_slope_data[2]:
                if isinstance(cut_slope_obj, str):
                    number_list = re.findall(r'\d+\.\d+|\d+', cut_slope_obj)
                    if "N" in cut_slope_obj:
                        self.cut_start_to_end_dict["N"] += float(number_list[0])
                    if "T" in cut_slope_obj:
                        self.cut_start_to_end_dict["T"] += float(number_list[0])
                    if "B" in cut_slope_obj:
                        self.cut_start_to_end_dict["B"] += float(number_list[1]) / 2
                        self.cut_start_to_end_dict["N"] += float(number_list[1]) / 2
                    self.cycles += 1
        # 计算续剪数据
        cycles_total_len = (float(args["VerticalMesh"])
                            - self.cut_start_to_end_dict["N"])
        if isinstance(self.cutting_slope_data[1], str) and len(self.cutting_slope_data[1]) > 2:
            self.cycles = 0
            temp_one_cycles_len = 0
            number_list = re.findall(r'\d+\.\d+|\d+', self.cutting_slope_data[1])
            while True:
                if "N" in self.cutting_slope_data[1]:
                    self.cut_start_to_end_dict["N"] += float(number_list[0])
                    temp_one_cycles_len += float(number_list[0])
                if "T" in self.cutting_slope_data[1]:
                    self.cut_start_to_end_dict["T"] += float(number_list[0])
                if "B" in self.cutting_slope_data[1]:
                    self.cut_start_to_end_dict["B"] += (float(number_list[1]) / 2)
                    self.cut_start_to_end_dict["N"] += (float(number_list[1]) / 2)
                    temp_one_cycles_len += (float(number_list[1]) / 2)
                self.cycles += 1
                if temp_one_cycles_len >= cycles_total_len:
                    break

            self.cutting_slope_data[1] += F"({self.cycles})"
            self.cycles = 0
        elif isinstance(self.cutting_slope_data[1], str) and len(self.cutting_slope_data[1]) <= 2:
            self.cycles = 0
            temp_one_cycles_len = 0
            number_list = re.findall(r'\d+\.\d+|\d+', self.cutting_slope_data[1])
            while True:
                if "N" in self.cutting_slope_data[1]:
                    self.cut_start_to_end_dict["N"] += float(number_list[0])
                    temp_one_cycles_len += float(number_list[0])
                if "T" in self.cutting_slope_data[1]:
                    self.cut_start_to_end_dict["T"] += float(number_list[0])
                if "B" in self.cutting_slope_data[1]:
                    self.cut_start_to_end_dict["B"] += (float(number_list[0]) / 2)
                    self.cut_start_to_end_dict["N"] += (float(number_list[0]) / 2)
                    temp_one_cycles_len += (float(number_list[0]) / 2)
                self.cycles += 1
                if temp_one_cycles_len >= cycles_total_len:
                    break
            self.cutting_slope_data[1] += F"({self.cycles})"
            self.cycles = 0
        elif isinstance(self.cutting_slope_data[1], list):
            self.cycles = 0
            temp_one_cycles_len = 0
            while True:
                for cut_slope_obj in self.cutting_slope_data[1]:
                    if isinstance(cut_slope_obj, str):
                        number_list = re.findall(r'\d+\.\d+|\d+', cut_slope_obj)
                        if "N" in cut_slope_obj:
                            self.cut_start_to_end_dict["N"] += float(number_list[0])
                            temp_one_cycles_len += float(number_list[0])
                        if "T" in cut_slope_obj:
                            self.cut_start_to_end_dict["T"] += float(number_list[0])
                        if "B" in cut_slope_obj:
                            self.cut_start_to_end_dict["B"] += float(number_list[1]) / 2
                            self.cut_start_to_end_dict["N"] += float(number_list[1]) / 2
                            temp_one_cycles_len += float(number_list[1]) / 2.
                self.cycles += 1
                if temp_one_cycles_len >= cycles_total_len:
                    break
            self.cutting_slope_data[1][-1] += F"({self.cycles})"

    def calculate_the_eye_ratio(self, args):
        if isinstance(self.eye_cutting_slope_data[0], str):
            number_list = re.findall(r'\d+\.\d+|\d+', self.eye_cutting_slope_data[0])
            if "N" in self.eye_cutting_slope_data[0]:
                self.eye_cut_start_to_end_dict["N"] += float(number_list[0])
            if "T" in self.eye_cutting_slope_data[0]:
                self.eye_cut_start_to_end_dict["T"] += float(number_list[0])
            if "B" in self.eye_cutting_slope_data[0]:
                self.eye_cut_start_to_end_dict["B"] += float(number_list[1]) / 2
                self.eye_cut_start_to_end_dict["N"] += float(number_list[1]) / 2
        else:
            print("宕眼剪裁斜率参数错误1")
        if isinstance(self.eye_cutting_slope_data[2], str) and len(self.eye_cutting_slope_data[2]) > 2:
            number_list = re.findall(r'\d+\.\d+|\d+', self.eye_cutting_slope_data[2])
            if "N" in self.eye_cutting_slope_data[2]:
                self.eye_cut_start_to_end_dict["N"] += float(number_list[0])
            if "T" in self.eye_cutting_slope_data[2]:
                self.eye_cut_start_to_end_dict["T"] += float(number_list[0])
            if "B" in self.eye_cutting_slope_data[2]:
                self.eye_cut_start_to_end_dict["B"] += float(number_list[1]) / 2
                self.eye_cut_start_to_end_dict["N"] += float(number_list[1]) / 2
        elif isinstance(self.eye_cutting_slope_data[2], str) and len(self.eye_cutting_slope_data[2]) <= 2:
            number_list = re.findall(r'\d+\.\d+|\d+', self.eye_cutting_slope_data[2])
            if "N" in self.eye_cutting_slope_data[2]:
                self.eye_cut_start_to_end_dict["N"] += float(number_list[0])
            if "T" in self.eye_cutting_slope_data[2]:
                self.eye_cut_start_to_end_dict["T"] += float(number_list[0])
            if "B" in self.eye_cutting_slope_data[2]:
                self.eye_cut_start_to_end_dict["B"] += float(number_list[0]) / 2
                self.eye_cut_start_to_end_dict["N"] += float(number_list[0]) / 2
        else:
            print("宕眼剪裁斜率参数错误2")
        cycles_total_len = (float(args["VerticalMesh"])
                            - self.eye_cut_start_to_end_dict["N"])
        if isinstance(self.eye_cutting_slope_data[1], str) and len(self.eye_cutting_slope_data[1]) > 2:
            self.cycles = 0
            temp_one_cycles_len = 0
            number_list = re.findall(r'\d+\.\d+|\d+', self.eye_cutting_slope_data[1])
            while True:
                if "N" in self.eye_cutting_slope_data[1]:
                    self.eye_cut_start_to_end_dict["N"] += float(number_list[0])
                    temp_one_cycles_len += float(number_list[0])
                if "T" in self.eye_cutting_slope_data[1]:
                    self.eye_cut_start_to_end_dict["T"] += float(number_list[0])
                if "B" in self.eye_cutting_slope_data[1]:
                    self.eye_cut_start_to_end_dict["B"] += (float(number_list[1]) / 2)
                    self.eye_cut_start_to_end_dict["N"] += (float(number_list[1]) / 2)
                    temp_one_cycles_len += (float(number_list[1]) / 2)
                self.cycles += 1
                if temp_one_cycles_len >= cycles_total_len:
                    break
            if self.eye_cutting_slope_data[1] == self.eye_cutting_slope_data[-1]:
                self.cycles += 1
                del self.eye_cutting_slope_data[-1]
            self.eye_cutting_slope_data[1] += F"({self.cycles})"
            self.cycles = 0
        elif isinstance(self.eye_cutting_slope_data[1], str) and len(self.eye_cutting_slope_data[1]) <= 2:
            self.cycles = 0
            temp_one_cycles_len = 0
            number_list = re.findall(r'\d+\.\d+|\d+', self.eye_cutting_slope_data[1])
            while True:
                if "N" in self.eye_cutting_slope_data[1]:
                    self.eye_cut_start_to_end_dict["N"] += float(number_list[0])
                    temp_one_cycles_len += float(number_list[0])
                if "T" in self.eye_cutting_slope_data[1]:
                    self.eye_cut_start_to_end_dict["T"] += float(number_list[0])
                if "B" in self.eye_cutting_slope_data[1]:
                    self.eye_cut_start_to_end_dict["B"] += (float(number_list[0]) / 2)
                    self.eye_cut_start_to_end_dict["N"] += (float(number_list[0]) / 2)
                    temp_one_cycles_len += (float(number_list[0]) / 2)
                self.cycles += 1
                if temp_one_cycles_len >= cycles_total_len:
                    break
            if self.eye_cutting_slope_data[1] == self.eye_cutting_slope_data[-1]:
                self.cycles += 1
                del self.eye_cutting_slope_data[-1]
            self.eye_cutting_slope_data[1] += F"({self.cycles})"
            self.cycles = 0
        else:
            print("宕眼剪裁斜率参数错误3")

    def get_core_config(self, core_config_dict: dict):
        """
        **获取绘图中心约束参数**

        ------------------------------------------------------------------------------\n
        ||  SCALE_RATIO          ||  整体绘图缩放比 <default>:: 1:100                 ||\n
        ------------------------------------------------------------------------------\n
        ||  TABLE_OFFSET         ||  表格边框偏移量 <default>:: 100                   ||\n
        ------------------------------------------------------------------------------\n
        ||  HORIZONTAL_SCALE_BAR ||  水平标尺 <default>:: 0.5                        ||\n
        ------------------------------------------------------------------------------\n
        ||  VERTICAL_SCALE_BAR   ||  垂直标尺 <default>:: 1.0                        ||\n
        ------------------------------------------------------------------------------\n
        ||  WORD_HEIGHT          ||  单词高度暨字体大小 <default>:: 3，5               ||\n
        ------------------------------------------------------------------------------\n
        ||  FORM_WORD_HEIGHT     ||  表格单词高度暨表格字体大小 <default>:: 7           ||\n
        ------------------------------------------------------------------------------\n
        ||  ANNOTATED_OFFSETS    ||  标注偏移量 <default>:: 2                        ||\n
        ------------------------------------------------------------------------------\n
        ||       MATERIAL        ||  拖网编织材料 <default>:: PA6                     ||\n
        ------------------------------------------------------------------------------\n
        :param core_config_dict: 核心绘图功能约束参数
        :return: None
        """
        self.drawingConfig = core_config_dict["--core-cfg"]

    def load_line_type(self):
        print(self.doc.ActiveLayer.name)
        try:
            self.doc.Linetypes.load("ACAD_ISO04W100", "acadiso.lin")
        except pywintypes.com_error:
            pass

    def redo(self, part=True) -> None:
        if part:
            if self.msp_list_len - self.msg_part_list_len_ori > 0:
                self.doc.SendCommand(f"_.undo\n{1}\n")
            else:
                async def send_error():
                    await self.send_to_app({"operation-error": 1})

                try:
                    # 尝试获取当前事件循环
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        # 如果事件循环正在运行，则将任务加入其中
                        loop.create_task(send_error())
                    else:
                        # 否则运行直到完成
                        loop.run_until_complete(send_error())
                except RuntimeError:
                    # 如果没有事件循环，创建一个新的
                    asyncio.run(send_error())
        else:
            if self.msp_list_len > 0:
                self.doc.SendCommand(f"_.undo\n{1}\n")
            else:
                async def send_error():
                    await self.send_to_app({"operation-error": 2})

                try:
                    # 尝试获取当前事件循环
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        # 如果事件循环正在运行，则将任务加入其中
                        loop.create_task(send_error())
                    else:
                        # 否则运行直到完成
                        loop.run_until_complete(send_error())
                except RuntimeError:
                    # 如果没有事件循环，创建一个新的
                    asyncio.run(send_error())

    def todo(self, part=True) -> None:
        self.doc.SendCommand(f"_.redo\n{1}\n")

    def _set_text_style(self) -> None:
        """
        配置绘图使用的字体
        :return: None
        """
        try:
            self._active_text_style()
        except pywintypes.com_error:
            try:
                self._active_text_style("汉仪长仿宋体", "长仿宋体")
            except pywintypes.com_error:
                self._active_text_style("仿宋", "仿宋体")

    def cache_data_four_dots(self, args: dict = None) -> None:
        """
        tilesPoss：上一段坐标列表
        tilesHeight：上一段高度
        tilesWidth：上一段最宽位置宽度
        tilesUpLineLength：上一段顶部宽度
        tilesDownLineLength：上一段底部宽度
        tilesLeftLineLength：上一段左侧高度
        tilesRightLineLength：上一段右侧侧高度
        tilesUpLineMidPoint：上一段顶部中心点位置
        tilesDownLineMidPoint：上一段底部中心点位置
        tilesLeftLineMidPoint：上一段左侧中心点位置
        tilesRightLineMidPoint：上一段右侧中心点位置
        tilesUpLineAngle：上一段顶部线段斜率度数
        tilesDownLineAngle：上一段底部线段斜率度数
        tilesLeftLineAngle：上一段左侧线段斜率度数
        tilesRightLineAngle：上一段右侧线段斜率度数
        """
        self.pre_draw_data = {
            "tilesPoss": [self.pos1, self.pos2, self.pos3, self.pos4]
            , "tilesHeight": abs(self.pos3[1] - self.pos1[1])
            , "tilesWidth": max(abs(self.pos2[0] - self.pos1[0]), abs(self.pos4[0] - self.pos3[0]))
            , "tilesUpLineLength": abs(self.pos2[0] - self.pos1[0])
            , "tilesDownLineLength": abs(self.pos4[0] - self.pos3[0])
            , "tilesLeftLineLength": math.dist(tuple(self.pos1), tuple(self.pos4))
            , "tilesRightLineLength": math.dist(tuple(self.pos2), tuple(self.pos3))
            , "tilesUpLineMidPoint": self.midpoint_(self.pos1, self.pos2)
            , "tilesDownLineMidPoint": self.midpoint_(self.pos3, self.pos4)
            , "tilesLeftLineMidPoint": self.midpoint_(self.pos1, self.pos4)
            , "tilesRightLineMidPoint": self.midpoint_(self.pos2, self.pos3)
            , "tilesUpLineAngle": math.degrees(
                math.atan(abs(self.pos2[1] - self.pos1[1]) / abs(self.pos2[0] - self.pos1[0])))
            , "tilesDownLineAngle": math.degrees(
                math.atan(abs(self.pos4[1] - self.pos3[1]) / abs(self.pos4[0] - self.pos3[0])))
            , "tilesLeftLineAngle": (math.degrees(
                math.atan(abs(self.pos1[1] - self.pos4[1]) / abs(self.pos1[0] - self.pos4[0])))
                                     if self.pos1[0] != self.pos4[0] else 0)
            , "tilesRightLineAngle": (math.degrees(
                math.atan(abs(self.pos2[1] - self.pos3[1]) / abs(self.pos2[0] - self.pos3[0])))
                                      if self.pos2[0] != self.pos3[0] else 0)
            , "args": args
        }
        self.position_stack.append(self.pre_draw_data)

    def poss_write_to_adoc(self, poss_list: list, close_flag: bool = True):
        list_date = self.organize_prepare_write_data(poss_list)
        rectangle = self.msp.AddLightWeightPolyline(listToFloat(list_date))
        if close_flag:
            rectangle.Closed = True

    def mult_mark_down(self, content: str | list, position: list, word_height: float = None,
                       insert_mode: int = 0, label_offset: list | None = None, rotary: tuple = (0, []),
                       mirror=(0, [])):
        if type(content) is str:
            self.mark_down(content, position, word_height, insert_mode, label_offset, rotary, mirror)
        elif type(content) is list:
            temp_x_pos = 0
            loop = -1
            for i in content:
                if loop == -1:
                    loop += 1
                    if isinstance(i, str):
                        self.mark_down(i, position, word_height, insert_mode, label_offset, rotary, mirror)
                        temp_x_pos = position[0]
                        position[1] -= word_height
                    elif isinstance(i, list):
                        line_loop = -1
                        for one_piece in i:
                            if line_loop == -1:

                                self.mark_down(one_piece, position, word_height, insert_mode, label_offset, rotary,
                                               mirror)
                                line_loop = len(one_piece)
                                temp_x_pos = position[0]
                            else:
                                self.mark_down(one_piece, position, word_height, insert_mode,
                                               [line_loop * 2, label_offset[1]], rotary,
                                               mirror)
                                line_loop = len(one_piece)
                        position[1] -= word_height
                else:
                    if isinstance(i, str):
                        position[0] = temp_x_pos
                        self.mark_down(i, position, word_height, insert_mode, None, rotary, mirror)
                        position[1] -= word_height
                    elif isinstance(i, list):
                        line_loop = -1
                        for one_piece in i:
                            if line_loop == -1:
                                position[0] = temp_x_pos
                                self.mark_down(one_piece, position, word_height, insert_mode,
                                               None, rotary,
                                               mirror)
                                line_loop = len(one_piece)
                            else:
                                self.mark_down(one_piece, position, word_height, insert_mode,
                                               [line_loop * 2, label_offset[1]], rotary, mirror)
                                line_loop = len(one_piece)
                        position[1] -= word_height

    def mult_eye_mark_down(self, content: str | list, position: list, word_height: float = None,
                           insert_mode: int = 0, label_offset: list | None = None, rotary: tuple = (0, []),
                           mirror=(0, [])):
        if type(content) is str:
            self.mark_down(content, position, word_height, insert_mode, label_offset, rotary, mirror)
        elif type(content) is list:
            temp_x_pos = 0
            loop = -1
            for i in content:
                if loop == -1:
                    loop += 1
                    if isinstance(i, str):
                        self.mark_down(i, position, word_height, insert_mode, label_offset, rotary, mirror)
                        temp_x_pos = position[0]
                        position[1] -= word_height + self.drawingConfig["ANNOTATED_OFFSETS"]
                    elif isinstance(i, list):
                        line_loop = -1
                        for one_piece in i:
                            if line_loop == -1:

                                self.mark_down(one_piece, position, word_height, insert_mode, label_offset, rotary,
                                               mirror)
                                line_loop = len(one_piece)
                                temp_x_pos = position[0]
                            else:
                                self.mark_down(one_piece, position, word_height, insert_mode,
                                               [line_loop * 2, label_offset[1]], rotary,
                                               mirror)
                                line_loop = len(one_piece)
                        position[1] -= word_height + self.drawingConfig["ANNOTATED_OFFSETS"]
                else:
                    if isinstance(i, str):
                        position[0] = temp_x_pos
                        self.mark_down(i, position, word_height, insert_mode, None, rotary, mirror)
                        position[1] -= word_height + self.drawingConfig["ANNOTATED_OFFSETS"]
                    elif isinstance(i, list):
                        line_loop = -1
                        for one_piece in i:
                            if line_loop == -1:
                                position[0] = temp_x_pos
                                self.mark_down(one_piece, position, word_height, insert_mode,
                                               None, rotary,
                                               mirror)
                                line_loop = len(one_piece)
                            else:
                                self.mark_down(one_piece, position, word_height, insert_mode,
                                               [line_loop * 2, label_offset[1]], rotary, mirror)
                                line_loop = len(one_piece)
                        position[1] -= word_height + self.drawingConfig["ANNOTATED_OFFSETS"]
            self.eye_cut_slope_mark_data[0] = position
            self.eye_cut_slope_mark_data[0][1] -= 2 * self.drawingConfig["FORM_WORD_HEIGHT"]

    def mark_down(self, content: str, position: list, word_height: float = None,
                  insert_mode: int = 0, label_offset: list | None = None, rotary: tuple = (0, []),
                  mirror=(0, [])):
        """
        进行文本标注
        :param content: 标注内容
        :param position: 标注位置
        :param word_height: 标注字高
        :param insert_mode: 标注模式
         0：左下对齐     1：中下对齐
         2：右下对齐     3：正中对齐
         4：中心对齐     5：顶部居中对齐
         6：左上对齐     7：中上对齐
         8：右上对齐     9：左中对齐
         10：中心对齐    11：右中对齐
         12：左下对齐
        :param label_offset: 标注偏移量 -- 默认不偏移
        [
        arg 1 : 偏移的距离 mm
        rag 2 ： 偏移的方向 1：上偏  2：下偏  3：左偏  4：右偏
        ]
        :param rotary: 是否旋转文字
        0：不旋转
        1：按剪裁斜率缺角度旋转  --常用
        2：按剪裁斜率 补角 度旋转  --不常用
        []: 包含模块 高度 和 右侧两点距离用于计算 tan值
        :param mirror: 是否将标注镜像 传入 带有 模式 与一个坐标向量的元组例如 (1,[10, 10])
        0：不镜像
        1：镜像但不删除原文字对象
        2：镜像并且删除原文字对象
        :return:
        """
        if len(position) == 2:
            position.append(0)

        print("初始position", position, end="  ")
        if label_offset is not None:
            if label_offset[1] == 1:
                position[1] += label_offset[0]
            elif label_offset[1] == 2:
                position[1] -= label_offset[0]
            elif label_offset[1] == 3:
                position[0] -= label_offset[0]
            elif label_offset[1] == 4:
                position[0] += label_offset[0]
        # 设置文本插入点
        print("偏移后position", position, end="  ")
        insert_pos = listToFloat(position)
        # 设置字高
        if word_height is None:
            try:
                print("字高不存在，正在获取保留字高")
                word_height = self.drawingConfig["WORD_HEIGHT"]
            except pywintypes.com_error:
                word_height = 2.5
        print("当前使用的为字高", word_height)
        text_obj = self.msp.AddText(content, insert_pos, word_height)
        text_obj.Height = word_height
        match insert_mode:
            case 0:  # 左下对齐
                text_obj.Alignment = 0
                text_obj.TextAlignmentPoint = insert_pos  # 如果不是默认位置 需要重新设置标注插入位置
            case 1:  # 中下对齐
                text_obj.Alignment = 1
                text_obj.TextAlignmentPoint = insert_pos
            case 2:  # 右下对齐
                text_obj.Alignment = 2
                text_obj.TextAlignmentPoint = insert_pos
            case 3:  #
                text_obj.Alignment = 3
                text_obj.TextAlignmentPoint = insert_pos
            case 4:  #
                text_obj.Alignment = 4
                text_obj.TextAlignmentPoint = insert_pos
            case 5:  #
                text_obj.Alignment = 5
                text_obj.TextAlignmentPoint = insert_pos
            case 6:  #
                text_obj.Alignment = 6
                text_obj.TextAlignmentPoint = insert_pos
            case 7:  # 中上对齐
                text_obj.Alignment = 7
                text_obj.TextAlignmentPoint = insert_pos
            case 8:  #
                text_obj.Alignment = 8
                text_obj.TextAlignmentPoint = insert_pos
            case 9:  #
                text_obj.Alignment = 9
                text_obj.TextAlignmentPoint = insert_pos
            case 10:  #
                text_obj.Alignment = 10
                text_obj.TextAlignmentPoint = insert_pos
            case 11:  #
                text_obj.Alignment = 11
                text_obj.TextAlignmentPoint = insert_pos
            case 12:  #
                text_obj.Alignment = 12
                text_obj.TextAlignmentPoint = insert_pos
            case _:
                pass
        match rotary[0]:
            case 1:  # 按剪裁斜率缺角度旋转
                radians = 0
                if isinstance(rotary[1], list):
                    radians = math.atan(rotary[1][0] / rotary[1][1])
                elif isinstance(rotary[1], float):
                    radians = rotary[1]
                rotation_angle = math.radians(90 - radians)
                text_obj.Rotate(insert_pos, rotation_angle)
            case 2:  # 按剪裁斜率补 角度旋转
                radians = 0
                if isinstance(rotary[1], list):
                    radians = math.atan(rotary[1][0] / rotary[1][1])
                elif isinstance(rotary[1], float):
                    radians = rotary[1]
                rotation_angle = math.radians(90 + radians)
                text_obj.Rotate(insert_pos, rotation_angle)
            case 3:  # 按剪裁斜率补 角度 翻转旋转
                radians = 0
                if isinstance(rotary[1], list):
                    radians = math.atan(rotary[1][0] / rotary[1][1])
                elif isinstance(rotary[1], float):
                    radians = rotary[1]
                rotation_angle = math.radians(90 + radians + 180)
                text_obj.Rotate(insert_pos, rotation_angle)
            case _:
                pass

        match mirror[0]:  # Copy的时候，要注意不要出现浅拷贝问题。
            case 1:  # 镜像文字对象但不删除原文字对象
                if len(mirror[1]) == 2:
                    mirror[1].append(0)
                mid_temp: list = mirror[1][:]
                mid_temp[1] += 10
                text_obj.Mirror(listToFloat(mirror[1]), listToFloat(mid_temp))
            case 2:  # 镜像文字对象后删除原文字对象
                if len(mirror[1]) == 2:
                    mirror[1].append(0)
                mid_temp: list = mirror[1][:]
                mid_temp[1] += 10
                text_obj.Mirror(listToFloat(mirror[1]), listToFloat(mid_temp))
                text_obj.Delete()
            case _:
                pass

    @staticmethod
    def midpoint(x1: float, y1: float, x2: float, y2: float):
        """
        **计算两点间的中点**

        :param x1: x1
        :param y1: y1
        :param x2: x2
        :param y2: y2
        :return: 中点坐标
        """
        mid_x = (x1 + x2) / 2
        mid_y = (y1 + y2) / 2
        return [mid_x, mid_y, 0]

    @staticmethod
    def midpoint_(x: list | tuple, y: list | tuple):
        """
        **计算两点间的中点**

        :param x: 坐标点1
        :param y: 坐标点2
        :return: 中点坐标
        """
        mid_x = (x[0] + y[0]) / 2
        mid_y = (x[1] + y[1]) / 2
        return [mid_x, mid_y, 0]

    @staticmethod
    def organize_prepare_write_data(data: list | tuple):
        """
         使用迭代方式将多层嵌套的list或tuple展开

         Args:
             data: 嵌套的list或tuple

         Returns:
             list: 展开后的一维列表
         """
        result = []
        stack = list(data)

        while stack:
            item = stack.pop(0)
            if isinstance(item, (list, tuple)):
                # 将嵌套元素插入到栈的前面，保持原始顺序
                stack = list(item) + stack
            else:
                result.append(item)
        print("解包数据", result)
        return result


if __name__ == '__main__':
    cad_controller_test = CADDrawingCore()
    cad_controller_test.drawing()
