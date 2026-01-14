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


def xiezuo(shared_gouyu_count, shared_jinbi_count, lock):
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
                    shared_gouyu_count.value += 1
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
                    shared_jinbi_count.value += 1
                    time.sleep(1)

def main():
    end_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", "end.png")
    fanhui_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", "fanhui.png")
    guanbi_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", "guanbi.png")
    start_path = ""
    shishenlu_path = ""
    xiezhan_path = ""
    choice1 = ""
    choice2 = ""

    choice1 = input("请输入1或2。1：打活动，2：打御魂或御灵副本: ").strip()
    if choice1 == "1":
        choice2 = input("请输入y或n。y：可以点击协战，n：不可以点击协战: ").strip().lower()
        if choice2 == "y":
            start_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", "hd_start.png")
            shishenlu_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", "hd_shishenlu.png")
            xiezhan_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", "hd_xiezhan.png")
            print("当前模式为：打活动副本且可以点击协战界面。请注意：每次打新活动副本前记得更新图标。")
        else:
            start_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", "hd_start.png")
            shishenlu_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", "hd_shishenlu.png")
            print("当前模式为：打活动副本，但是不点击协战界面。请注意：每次打新活动副本前记得更新图标。")
    else:
        start_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", "yu_start.png")
        shishenlu_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", "yu_shishenlu.png")
        print("当前模式为：打御魂或者御灵。")
        
    run_count = 0

    # 启动识别协作子进程，接受勾玉协作，拒绝金币协作
    gouyu_count = Value('i', 0)  # 'i' 表示整型
    jinbi_count = Value('i', 0)
    lock = Lock()
    process = Process(target=xiezuo, args=(gouyu_count, jinbi_count, lock))
    process.daemon = True
    process.start()
    
    try:
        while True:
            if run_count > 10000:
                print("已执行100次，退出", flush=True)
                break
            # 识别start.png
            delay = 0
            while True:
                time.sleep(3)
                start_result = find_image_on_screen(start_path)
                if start_result:
                    # 随机延迟1-3秒内，5%概率点击式神录，5%概率点击协战，10%概率等待5-10秒
                    possible =  random.random()
                    if possible < 0.05:
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
                    break
                else:
                    pass
            # 识别end.png
            try_time = 1
            while True:
                # 由一场战斗时间决定，其基础上加6-10s
                delay = random.uniform(14, 18)
                print(f"第{try_time}次等待{delay:.2f}s", flush=True, end="-->")
                time.sleep(delay)
                end_result = find_image_on_screen(end_path)
                if end_result:
                    end_x, end_y = end_result
                    random_click(end_x, end_y)
                    # time.sleep(3) # 特殊活动，需要间隔点击两次
                    # random_click(end_x, end_y)
                    run_count += 1
                    with lock:
                        current_gouyu_count = gouyu_count.value
                        current_jinbi_count = jinbi_count.value
                    print(f"运行{run_count}次，勾玉{current_gouyu_count}次, 金币{current_jinbi_count}次")
                    break
                else:
                    try_time += 1
                    if try_time > 3:
                        break
    except KeyboardInterrupt:
        print("脚本已停止")

if __name__ == "__main__":
    main()