import cv2
import numpy as np
import pyautogui
import time
import random
import os
from multiprocessing import Process, Value, Lock

# pip install opencv-python numpy pyautogui pillow

def find_image_on_screen(template_path, threshold=0.8):
    """
    在屏幕上查找指定图像
    
    参数:
        template_path: 模板图像路径
        threshold: 匹配阈值，越高要求越精确
        
    返回:
        如果找到，返回(x, y, w, h)，否则返回None
    """
    # 确保模板图像存在
    if not os.path.exists(template_path):
        print(f"模板图像不存在: {template_path}")
        return None
    
    # 读取模板图像，转换为灰度
    template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
    if template is None:
        print(f"无法读取模板图像: {template_path}")
        return None
    
    # 截取屏幕
    screenshot = pyautogui.screenshot()
    screenshot = np.array(screenshot)
    screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2GRAY) # 转换为灰度
    
    # 使用模板匹配
    result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
    
    # 查找匹配位置
    locations = np.where(result >= threshold)
    
    if len(locations[0]) > 0:
        # 获取第一个匹配位置
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        top_left = max_loc
        return (top_left[0], top_left[1])
    
    return None

def random_click(x, y, random_range = 40):
    """
    在指定区域内随机点击
    
    参数:
        x, y: 区域左上角坐标
        width, height: 区域宽高
        random_range: 随机范围，点击位置会在中心点周围random_range像素范围内随机选择
    """
    # 在x+random_range和y+random_range内随机点击
    click_x = x + random.randint(0, random_range)
    click_y = y + random.randint(0, random_range)
    print(f"已点击位置: ({click_x}, {click_y})", flush=True, end="-->")
    # 执行点击
    pyautogui.click(click_x, click_y)


def xiezuo(gouyu_count, lock):
    # 一直监听勾玉协作
    gouyu_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", "gouyu.png")
    jieshou_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", "jieshou.png")
    jujue_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", "jujue.png")
    while True:
        gouyu_result = find_image_on_screen(gouyu_path)
        with lock:
            if gouyu_result:
                jieshou_result = find_image_on_screen(jieshou_path)
                if jieshou_result:
                    # 截图并保存到当前目录下的screenshot/日期目录下
                    now_time = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
                    screenshot = pyautogui.screenshot()
                    screenshot.save(f"screenshot/{now_time}.png")
                    jieshou_x, jieshou_y = jieshou_result
                    random_click(jieshou_x, jieshou_y)
                    gouyu_count.value += 1
                    # 再加上飞书或者钉钉通知操作
                    time.sleep(1)
            else:
                jujue_result = find_image_on_screen(jujue_path)
                if jujue_result:
                    # 截图并保存到当前目录下的screenshot/日期目录下
                    now_time = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
                    screenshot = pyautogui.screenshot()
                    screenshot.save(f"screenshot/{now_time}.png")
                    jujue_x, jujue_y = jujue_result
                    random_click(jujue_x, jujue_y)
                    time.sleep(1)


def huijuan(xiaoHuiJuan_count, zhongHuiJuan_count, daHuiJuan_count, lock):
    # 一直绘卷
    xiaoHuiJuan = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", "xiaoHuiJuan.png")
    zhongHuiJuan = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", "zhongHuiJuan.png")
    daHuiJuan = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", "daHuiJuan.png")
    while True:
        xiaoHuiJuan_result = find_image_on_screen(xiaoHuiJuan)
        zhongHuiJuan_result = find_image_on_screen(zhongHuiJuan)
        daHuiJuan_result = find_image_on_screen(daHuiJuan)
        if xiaoHuiJuan_result or zhongHuiJuan_result or daHuiJuan_result:
            with lock:
                if xiaoHuiJuan_result:
                    xiaoHuiJuan_count.value += 1    
                    time.sleep(5) 
                elif zhongHuiJuan_result:
                    zhongHuiJuan_count.value += 1    
                    time.sleep(5)
                elif daHuiJuan_result:
                    daHuiJuan_count.value += 1    
                    time.sleep(5)


def main():
    end_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", "end.png")
    fanhui_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", "fanhui.png")
    guanbi_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", "guanbi.png")
    start_path = ""
    shishenlu_path = ""
    xiezhan_path = ""
    choice1 = ""
    choice2 = ""
    choice3 = ""
    scan_huijuan = True

    choice1 = input("请输入1或2。1：打活动，2：打御魂或御灵副本: ").strip()
    if choice1 == "1":
        start_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", "hd_start.png")
        scan_huijuan = False
    elif choice1 == "2":
        start_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", "yu_start.png")
    else:
        pass

    choice2 = input("请输入y或n。y：可以点击协战，n：不可以点击协战: ").strip().lower()
    if choice2 == "y":
        xiezhan_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", "hd_xiezhan.png")
    else:
        pass

    choice3 = input("请输入y或n。y：可以点击式神录，n：不可以点击式神录: ").strip().lower()
    if choice3 == "y":
        shishenlu_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", "hd_shishenlu.png")
    else:
        pass
        
    run_count = 0

    # 启动识别协作子进程，接受勾玉协作，拒绝金币协作
    gouyu_count = Value('i', 0)  # 'i' 表示整型
    lock1 = Lock()
    process1 = Process(target=xiezuo, args=(gouyu_count, lock1))
    process1.daemon = True
    process1.start()

    if scan_huijuan:
        xiaoHuiJuan_count = Value('i', 0)  # 'i' 表示整型
        zhongHuiJuan_count = Value('i', 0)
        daHuiJuan_count = Value('i', 0)
        lock2 = Lock()
        process2 = Process(target=huijuan, args=(xiaoHuiJuan_count, zhongHuiJuan_count, daHuiJuan_count, lock2))
        process2.daemon = True
        process2.start()
    
    try:
        while True:
            if run_count > 10000:
                print("已执行10000次，退出", flush=True)
                break
            # 识别start.png
            delay = 0
            start_result = find_image_on_screen(start_path)
            if start_result:
                # 随机延迟1-3秒内，5%概率点击式神录，5%概率点击协战，10%概率等待5-10秒
                possible =  random.random()
                if possible < 0.05 and choice3 == "y":
                    print("触发5%概率, 点击式神录并等待10-15s后返回", flush=True)
                    shishenlu_result = find_image_on_screen(shishenlu_path)
                    if shishenlu_result:
                        shishenlu_x, shishenlu_y = shishenlu_result
                        random_click(shishenlu_x, shishenlu_y)
                    # 等待10-15s并等待页面加载
                    time.sleep(random.uniform(10, 15))
                    # 点击返回
                    fanhui_result = find_image_on_screen(fanhui_path)
                    if fanhui_result:
                        fanhui_x, fanhui_y = fanhui_result
                        random_click(fanhui_x, fanhui_y)
                    # 等待5s页面加载
                    time.sleep(5)
                elif 0.05 <= possible < 0.1 and choice2 == "y":
                    print("触发5%概率, 点击协战并等待10-15s后返回", flush=True)
                    xiezhan_result = find_image_on_screen(xiezhan_path)
                    if xiezhan_result:
                        xiezhan_x, xiezhan_y = xiezhan_result
                        random_click(xiezhan_x, xiezhan_y)
                    # 等待10-15s并等待页面加载
                    time.sleep(random.uniform(10, 15))
                    # 点击返回
                    guanbi_result = find_image_on_screen(guanbi_path, 0.7)
                    if guanbi_result:
                        guanbi_x, guanbi_y = guanbi_result
                        random_click(guanbi_x, guanbi_y)
                    # 等待5s页面加载
                    time.sleep(5)
                elif 0.1 <= possible < 0.2:
                    delay = random.uniform(5, 10)
                    print(f"触发10%概率，等待{delay:.2f}秒", flush=True, end="-->")
                else:
                    delay = random.uniform(1, 3)
                    print(f"等待{delay:.2f}秒", flush=True, end="-->")
                time.sleep(delay)
                x, y = start_result
                random_click(x, y)

                # 识别end.png
                try_time = 1
                while True:
                    # 由一场战斗时间决定，其基础上加12-16s
                    delay = random.uniform(14, 18)
                    print(f"第{try_time}次等待{delay:.2f}s", flush=True, end="-->")
                    time.sleep(delay)
                    end_result = find_image_on_screen(end_path)
                    if end_result:
                        end_x, end_y = end_result
                        random_click(end_x, end_y)
                        time.sleep(0.5) # 防止时间恰好，点击两次
                        random_click(end_x, end_y)
                        run_count += 1
                        with lock1:
                            current_gouyu_count = gouyu_count.value
                        if scan_huijuan:
                            with lock2:
                                current_xiaohuijuan_count = xiaoHuiJuan_count.value
                                current_zhonghuijuan_count = zhongHuiJuan_count.value
                                current_dahuijuan_count = daHuiJuan_count.value
                        if current_gouyu_count > 0:
                            if scan_huijuan:
                                print(f"运行{run_count}次，接到勾协，小绘卷 {current_xiaohuijuan_count} 次, 中绘卷 {current_zhonghuijuan_count} 次, 大绘卷 {current_dahuijuan_count} 次")
                            else:
                                print(f"运行{run_count}次，接到勾协")
                        else:
                            if scan_huijuan:
                                print(f"运行{run_count}次，小绘卷 {current_xiaohuijuan_count} 次, 中绘卷 {current_zhonghuijuan_count} 次, 大绘卷 {current_dahuijuan_count} 次")
                            else:
                                print(f"运行{run_count}次")
                    else:
                        try_time += 1
                        if try_time > 3:
                            break
            else:
                pass
    except KeyboardInterrupt:
        print("脚本已停止")

if __name__ == "__main__":
    main()