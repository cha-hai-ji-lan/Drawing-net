import asyncio
import websockets
import json
from core import CADDrawingCore

"""
APP 与 AutoCAD绘图Core 数据沟通
===================================
||       keys       ||   values  ||
===================================
||      --exit      ||     0     || => 断开连接
===================================
||      --exit      ||    -1     || => 结束服务
===================================
||      --exit      ||     1     || => 待机
===================================
||    --core-cfg    ||   dict{}  || => CAD绘画全剧约束设置
===================================
||    --todo-step   ||     1     || => 局部绘画前进一步
===================================
||    --redo-step   ||     1     || => 局部绘画后退一步
===================================
||      --todo      ||     1     || => 全局绘画前进一步
===================================
||      --redo      ||     1     || => 全局绘画后退一步
===================================
||--give-up-drawing ||     1     || =>  放弃本次绘画
===================================

AutoCAD绘图Core 与 APP 数据沟通 --服务端返回响应指令
===============================
operation-error
-------------------------------
||   1   || 局部绘制操作撤销失败 --已撤消完局部绘图的第一步操作
------------------------------
||   2   || 全局绘制操作撤销失败 --已撤消完全局绘图的第一步操作
------------------------------

===============================
type-error
-------------------------------
||   1   || 接收网具类型错误
-------------------------------

===============================
clean-error
-------------------------------
||   1   || 模型空间清理失败
-------------------------------

===============================
"""

running = True  # 控制服务运行状态的全局变量
CAD_OBJ = None
track_data = {"--track-data": []}


async def handler(connection):
    async def send_message(message_dict):
        str_data = str(message_dict)
        await connection.send(str_data)

    print("\033[34m有客户端已连接\033[0m")
    global CAD_OBJ
    if CAD_OBJ is None:
        pass
        CAD_OBJ = CADDrawingCore(send_message_func=send_message)  # 初始化CAD绘图对象
    try:
        async for message in connection:
            global track_data
            client_message: dict = json.loads(message)
            # TODO: 测试程序用于打印接收到的数据，在release时停用
            print(f"\033[36m客户端信息：{message}\033[0m")
            await connection.send("{server-response: 0}")
            if "--exit" in client_message and client_message["--exit"] == 0:
                print("收到退出指令，正在断开连接...")
                await connection.send("服务端已断开连接.")
                await connection.close()
                track_data = {"--track-data": []}
                print("\033[33m服务器已断开连接\033[0m")
            elif "--exit" in client_message and client_message["--exit"] == -1:
                print("\033[33m收到退出指令，正在断开连接，并停止服务...\033[0m")
                global running
                running = False
                await connection.send("服务端已断开连接.")
                await connection.close()
            elif "--core-cfg" in client_message:
                track_data["--track-data"].append(client_message)
                CAD_OBJ.get_core_config(client_message)
            elif "--todo-step" in client_message:
                track_data["--track-data"].append(client_message)
                CAD_OBJ.todo(True)
            elif "--redo-step" in client_message:
                track_data["--track-data"].append(client_message)
                CAD_OBJ.redo(True)
            elif "--todo" in client_message:
                track_data["--track-data"].append(client_message)
                CAD_OBJ.todo(False)
            elif "--redo" in client_message:
                track_data["--track-data"].append(client_message)
                CAD_OBJ.redo(False)
            elif "--give-up-drawing" in client_message:
                track_data["--track-data"].append(client_message)
                CAD_OBJ.clean_model()
            elif "node" in client_message:
                track_data["--track-data"].append(client_message)
                CAD_OBJ.drawing(client_message)
    except websockets.exceptions.ConnectionClosed:
        print("\033[33m客户端已断开连接\033[0m")


async def main():
    async with websockets.serve(
            handler,
            "127.0.0.1",
            8080
    ):
        print("\033[32mWebSocket 服务端已启动，等待连接...\033[0m")
        # await asyncio.Future()  # 永久运行
        while running:
            await asyncio.sleep(1)  # 避免CPU空转


asyncio.run(main())



