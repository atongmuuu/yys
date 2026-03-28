import cv2
import numpy as np
import pyautogui
import time
import random
import os
import sys
from multiprocessing import Process, Value, Lock
import requests
from collections import deque
import time


def send_feishu_webhook(message, name = "李子豪"):
    # 替换为你的飞书 Webhook URL
    webhook_url = "https://open.feishu.cn/open-apis/bot/v2/hook/f1fe9e02-592b-42c0-bc82-c5b896c132cb"
    
    # 构造 Webhook 消息体
    webhook_message = {
        "msg_type": "text",
        "content": {
            "text": name + "\n" + message
        }
    }
    
    # 发送 POST 请求到飞书 Webhook
    response = requests.post(webhook_url, json=webhook_message)
    
    # 检查请求是否成功
    if response.status_code == 200:
        pass
    else:
        print(f"\n消息发送失败，状态码: {response.status_code}, 响应内容: {response.text}")


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


def find_button_in_roi(roi_bgr, template_bgr, threshold=0.8):
    if roi_bgr.size == 0 or template_bgr.size == 0:
        return None, 0.0
    
    template_h, template_w = template_bgr.shape[:2]
    result = cv2.matchTemplate(roi_bgr, template_bgr, cv2.TM_CCOEFF_NORMED)
    
    # 找到所有超过阈值的匹配
    locations = np.where(result >= threshold)
    
    if len(locations[0]) == 0:
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        return None, max_val
    
    # 直接找到Y坐标最大的（最靠下的）
    max_y = -1
    best_pt = None
    best_confidence = 0
    
    for pt in zip(*locations[::-1]):  # 遍历所有匹配点
        y = pt[1]  # Y坐标
        confidence = result[pt[1], pt[0]]
        
        # 找最靠下的（Y坐标最大的）
        if y > max_y:
            max_y = y
            best_pt = pt
            best_confidence = confidence
    
    return best_pt, best_confidence


def find_image_on_region(template_path, pk_template_path, threshold=0.8):
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
    
    # 读取模板图像，转换为灰度
    pk_template = cv2.imread(pk_template_path, cv2.IMREAD_GRAYSCALE)
    if pk_template is None:
        print(f"无法读取模板图像: {pk_template_path}")
        return None

    # 截取屏幕
    screenshot = pyautogui.screenshot()
    screenshot = np.array(screenshot)
    screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2GRAY) # 转换为灰度
    # screenshot_bgr = cv2.cvtColor(screenshot, cv2.COLOR_RGB2GRAY)
    
    # 使用模板匹配
    result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
    
    # 查找匹配位置
    locations = np.where(result >= threshold)
    
    if len(locations[0]) > 0:
        # 获取第一个匹配位置
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        x, y = max_loc[0], max_loc[1]
        roi_top = y-400
        roi_bottom = y
        roi_left = x-180
        roi_right = x + 220
        roi = screenshot[roi_top:roi_bottom, roi_left:roi_right]
        # 把这一部分截图保存到screenshot目录下
        # now_time = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
        # cv2.imwrite(f"screenshot/{now_time}.png", roi)
        match_loc, confidence = find_button_in_roi(roi, pk_template)
        return match_loc, roi_left, roi_top
    
    return None

def random_click(x, y, name = "ok", random_min = 0, random_max = 40):
    """
    在指定区域内随机点击
    
    参数:
        x, y: 区域左上角坐标
        width, height: 区域宽高
        
        random_min: 随机范围，点击位置会在中心点周围random_min像素范围内随机选择
        random_max: 随机范围，点击位置会在中心点周围random_max像素范围内随机选择
    """
    # 在x+random_range和y+random_range内随机点击
    click_x = x + random.randint(random_min, random_max)
    click_y = y + random.randint(random_min, random_max)
    print(f"已点击位置: ({click_x}, {click_y}), {name}")
    # 执行点击
    pyautogui.click(click_x, click_y)


def detect_xiezuo(gouyu_count, lock):
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
                    random_click(jieshou_x, jieshou_y, jieshou_path)
                    gouyu_count.value += 1
                    # 再加上飞书或者钉钉通知操作
                    send_feishu_webhook("接收到勾协啦！！！")
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


def detect_huijuan(xiaoHuiJuan_count, zhongHuiJuan_count, daHuiJuan_count,  lock):
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
                    if xiaoHuiJuan_count.value % 10 == 0:
                        send_feishu_webhook(f"已得 {xiaoHuiJuan_count.value} 次小绘卷")
                elif zhongHuiJuan_result:
                    zhongHuiJuan_count.value += 1    
                    if zhongHuiJuan_count.value % 5 == 0:
                        send_feishu_webhook(f"已得 {zhongHuiJuan_count.value} 次中绘卷")
                elif daHuiJuan_result:
                    daHuiJuan_count.value += 1
                    send_feishu_webhook(f"已得 {daHuiJuan_count.value} 次大绘卷")
            time.sleep(4)


def detect_end_png(run_count, lock, total_count):
    # 一直检测并点击end.png
    end_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", "end.png")
    while True:
        end_result = find_image_on_screen(end_path)
        if end_result:
            time.sleep(3)
            # 保证end.png触底
            end_result = find_image_on_screen(end_path)
            if end_result:
                end_x, end_y = end_result
                random_click(end_x, end_y, end_path)
                with lock:
                    run_count.value += 1
                    if run_count.value % 50 == 0:
                        send_feishu_webhook(f"已执行 {run_count.value} 次")
                    # 如果run_count.value大于total_count，退出脚本
                    if run_count.value > total_count:
                        print(f"已执行 {run_count.value} 次，超过设定的 {total_count} 次，退出脚本")
                        send_feishu_webhook(f"已执行 {run_count.value} 次，超过设定的 {total_count} 次，脚本已退出")
                        os._exit(0)
        

def detect_shishenlu_png(png_name):
    # 一直检测并点击shishenlu.png
    shishenlu_png = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", png_name)
    fanhui_png = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", "fanhui.png")
    while True:
        time.sleep(1)
        shishenlu_result = find_image_on_screen(shishenlu_png)
        if shishenlu_result and random.random() < 0.05:
            print("进入式神录")
            shishenlu_x, shishenlu_y = shishenlu_result
            random_click(shishenlu_x, shishenlu_y, shishenlu_png)
            time.sleep(random.uniform(10, 15))
            fanhui_result = find_image_on_screen(fanhui_png)
            if fanhui_result:
                fanhui_x, fanhui_y = fanhui_result
                random_click(fanhui_x, fanhui_y, fanhui_png)
                time.sleep(random.uniform(1, 3))


def detect_png(png_name):
    # 记录最近20秒内的点击时间
    click_times = deque()
    png_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", png_name)
    while True:
        time.sleep(2)
        png_result = find_image_on_screen(png_path)
        if png_result:
            png_x, png_y = png_result
            random_click(png_x, png_y, png_path)
            now = time.time()
            # 记录本次点击时间
            click_times.append(now)
            # 移除20秒前的记录
            if click_times and click_times[0] < now - 20:
                click_times.popleft()
            # 如果20秒内点击次数>=6，终止脚本
            if len(click_times) >= 6:
                print("20秒内点击次数超过6次，终止脚本")
                send_feishu_webhook("20秒内点击次数超过6次，门票用光，终止脚本")
                os._exit(0)


def detect_tupo_zero(tupo_zero_value, lock):
    # 0个突破卷
    tupo_zero_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", "tupo_zero.png")
    tupo_guanbi_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", "kun28_guanbi.png")
    while True:
        zero_result = find_image_on_screen(tupo_zero_path, 0.95)
        if zero_result:
            time.sleep(1)
            tupo_guanbi_result = find_image_on_screen(tupo_guanbi_path)
            if tupo_guanbi_result:
                tupo_guanbi_x, tupo_guanbi_y = tupo_guanbi_result
                random_click(tupo_guanbi_x, tupo_guanbi_y, tupo_guanbi_path)
                with lock:
                    tupo_zero_value.value = 1
                time.sleep(1)
        

def main():
    # 启动识别勾玉子进程，接受勾玉协作，拒绝金币协作
    gouyu_count = Value('i', 0)  # 'i' 表示整型
    lock1 = Lock()
    detect_gouyu_process = Process(target=detect_xiezuo, args=(gouyu_count, lock1))
    detect_gouyu_process.daemon = True
    detect_gouyu_process.start()

    # 启动识别end.png子进程，点击end.png
    run_count = Value('i', 0)  # 'i' 表示整型
    lock2 = Lock()
    
    fanhui_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", "fanhui.png")
    choice = input("请输入1或2或3或4。1：打活动，2：打御灵，3：打御魂，4：打困28: ").strip()
    total_count = int(input("请输入要执行的次数: "))
    
    detect_end_process = Process(target=detect_end_png, args=(run_count, lock2, total_count))
    detect_end_process.daemon = True
    detect_end_process.start()

    # 启动识别end2.png子进程，点击end2.png。用于没有end.png时，点击end2.png返回主界面
    detect_end2_process = Process(target=detect_png, args=("end2.png",))
    detect_end2_process.daemon = True
    detect_end2_process.start()

    # 启动失败子进程，点击fanhui.png返回主界面
    detect_shibai_process = Process(target=detect_png, args=("tupo_shibai.png",))
    detect_shibai_process.daemon = True
    detect_shibai_process.start()

    if choice == "1":
        start_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", "huodong_start.png")
        shishenlu_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", "huodong_shishenlu.png")
    elif choice == "2":
        start_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", "yuling_start.png")
        shishenlu_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", "yuling_shishenlu.png")

        # 启动绘卷进程
        xiaoHuiJuan_count = Value('i', 0)  # 'i' 表示整型
        zhongHuiJuan_count = Value('i', 0)
        daHuiJuan_count = Value('i', 0)
        lock3 = Lock()
        detect_huijuan_process = Process(target=detect_huijuan, args=(xiaoHuiJuan_count, zhongHuiJuan_count, daHuiJuan_count, lock3))
        detect_huijuan_process.daemon = True
        detect_huijuan_process.start()
    elif choice == "3":
        start_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", "yuhun_start.png")
        shishenlu_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", "yuhun_shishenlu.png")
    elif choice == "4":
        tupo_all_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", "tupo_all.png")
        tupo_start_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", "tupo_start.png")
        tupo_youshangjiao_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", "tupo_youshangjiao.png")
        tupo_jingong_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", "tupo_jingong.png")
        tupo_shuaxin_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", "tupo_shuaxin.png")
        tupo_queding_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", "tupo_queding.png")
        kun28_baoxiang_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", "kun28_baoxiang.png")
        kun28_guanbi_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", "kun28_guanbi.png")
        kun28_ershiba_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", "kun28_ershiba.png")
        kun28_tansuo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", "kun28_tansuo.png")
        kun28_mianju_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", "kun28_mianju.png")
        kun28_wuyan_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", "kun28_wuyan.png")
        kun28_damo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", "kun28_damo.png")
        kun28_damo2_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", "kun28_damo2.png")
        kun28_start_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", "kun28_start.png")
        kun28_queren_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", "kun28_queren.png")
        kun28_boss_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", "kun28_boss.png")
        kun28_jiangli_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", "kun28_jiangli.png")
        shishenlu_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", "kun28_shishenlu.png")

        # 启动绘卷进程
        xiaoHuiJuan_count = Value('i', 0)  # 'i' 表示整型
        zhongHuiJuan_count = Value('i', 0)
        daHuiJuan_count = Value('i', 0)
        lock3 = Lock()
        detect_huijuan_process = Process(target=detect_huijuan, args=(xiaoHuiJuan_count, zhongHuiJuan_count, daHuiJuan_count, lock3))
        detect_huijuan_process.daemon = True
        detect_huijuan_process.start()
    else:
        print("请输入1，2，3，4")
        sys.exit()

    if choice in ["1", "2", "3"]:
        detect_start_process = Process(target=detect_png, args=(start_path,))
        detect_start_process.daemon = True
        detect_start_process.start()

        while True:
            # 保持不退出
            time.sleep(1)
    else:
        # 启动突破0个进程
        tupo_zero_value = Value('i', 0)
        lock5 = Lock()
        detect_tupo_zero_process = Process(target=detect_tupo_zero, args=(tupo_zero_value, lock5))
        detect_tupo_zero_process.daemon = True
        detect_tupo_zero_process.start()

        while True:
            in_tupo = False
            time.sleep(2)
            # 识别关闭
            kun28_guanbi_result = find_image_on_screen(kun28_guanbi_path)
            if kun28_guanbi_result:
                kun28_guanbi_x, kun28_guanbi_y = kun28_guanbi_result
                random_click(kun28_guanbi_x, kun28_guanbi_y, kun28_guanbi_path)
                time.sleep(2)
            # 识别宝箱
            for i in range(3):
                kun28_baoxiang_result = find_image_on_screen(kun28_baoxiang_path)
                if kun28_baoxiang_result:
                    kun28_baoxiang_x, kun28_baoxiang_y = kun28_baoxiang_result
                    random_click(kun28_baoxiang_x, kun28_baoxiang_y, kun28_baoxiang_path)
                    time.sleep(3)
            # 识别突破
            tupo_all_result = find_image_on_screen(tupo_all_path, 0.95)
            if tupo_all_result:
                in_tupo = True
                tupo_start_result = find_image_on_screen(tupo_start_path)
                if tupo_start_result:
                    tupo_start_x, tupo_start_y = tupo_start_result
                    random_click(tupo_start_x, tupo_start_y, tupo_start_path)
                    time.sleep(2)
                    while True:
                        tupo_youshangjiao_result = find_image_on_screen(tupo_youshangjiao_path, 0.95)
                        # 突破卷为零的时候
                        with lock5:
                            current_tupo_zero_value = tupo_zero_value.value
                            if current_tupo_zero_value == 1:
                                print("突破卷为零")
                                break
                        if tupo_youshangjiao_result:
                            tupo_youshangjiao_x, tupo_youshangjiao_y = tupo_youshangjiao_result
                            random_click(tupo_youshangjiao_x, tupo_youshangjiao_y, tupo_youshangjiao_path, 20, 40)
                            time.sleep(1)
                            tupo_jingong_result = find_image_on_screen(tupo_jingong_path)
                            if tupo_jingong_result:
                                tupo_jingong_x, tupo_jingong_y = tupo_jingong_result
                                random_click(tupo_jingong_x, tupo_jingong_y, tupo_jingong_path)
                        else:
                            tupo_shuaxin_result = find_image_on_screen(tupo_shuaxin_path)
                            if tupo_shuaxin_result:
                                tupo_shuaxin_x, tupo_shuaxin_y = tupo_shuaxin_result
                                random_click(tupo_shuaxin_x, tupo_shuaxin_y, tupo_shuaxin_path)
                                time.sleep(1)
                                tupo_queding_result = find_image_on_screen(tupo_queding_path)
                                if tupo_queding_result:
                                    tupo_queding_x, tupo_queding_y = tupo_queding_result
                                    random_click(tupo_queding_x, tupo_queding_y, tupo_queding_path)
                                    time.sleep(1)
                    with lock5:
                        tupo_zero_value.value = 0
            time.sleep(5)
            # 识别kun28_ershiba.png
            ershiba_result = find_image_on_screen(kun28_ershiba_path)
            if ershiba_result:
                ershiba_x, ershiba_y = ershiba_result
                random_click(ershiba_x, ershiba_y, kun28_ershiba_path)
                time.sleep(5)
            # 识别kun28_tansuo.png
            tansuo_result = find_image_on_screen(kun28_tansuo_path)
            if tansuo_result:
                tansuo_x, tansuo_y = tansuo_result
                random_click(tansuo_x, tansuo_y, kun28_tansuo_path)
                time.sleep(2)
            # 识别kun28_damo.png和kun28_start.png
            print("识别kun28_damo.png和kun28_start.png")
            start_time = time.time()
            times = 1
            while True and not in_tupo:
                print(time.time() - start_time, times)
                if time.time() - start_time > 10:
                    if times == 1:
                        drag_path = kun28_mianju_path
                    else:
                        drag_path = kun28_wuyan_path
                    kun28_drag_result = find_image_on_screen(drag_path)
                    if kun28_drag_result:
                        kun28_drag_x, kun28_drag_y = kun28_drag_result
                        # 鼠标点击kun28_drag_x, kun28_drag_y位置将向左移动700个像素
                        pyautogui.FAILSAFE = True
                        # 点击并按住不放
                        pyautogui.mouseDown(x=kun28_drag_x, y=kun28_drag_y)
                        # 向左移动700像素
                        pyautogui.moveRel(-700, 0, duration=1)  # duration控制移动速度
                        # 松开鼠标
                        pyautogui.mouseUp()
                        time.sleep(1)
                    start_time = time.time()
                    times += 1
                elif times > 3:
                    fanhui_result = find_image_on_screen(fanhui_path)
                    if fanhui_result:
                        fanhui_x, fanhui_y = fanhui_result
                        random_click(fanhui_x, fanhui_y, fanhui_path)
                        time.sleep(1)
                        kun28_queren_result = find_image_on_screen(kun28_queren_path)
                        if kun28_queren_result:
                            kun28_queren_x, kun28_queren_y = kun28_queren_result
                            random_click(kun28_queren_x, kun28_queren_y, kun28_queren_path)
                            break
                else:
                    pass
                start_result = find_image_on_region(kun28_damo_path, kun28_start_path)
                if start_result:
                    match_loc, roi_left, roi_top = start_result
                    if match_loc:
                        # 匹配成功！计算按钮在全屏的中心坐标
                        (bx, by) = match_loc  # 这是在ROI内的坐标
                        start_x = roi_left + bx
                        start_y = roi_top + by
                        random_click(start_x, start_y, kun28_start_path)
                        time.sleep(15)
                        start_time = time.time()
                start_result = find_image_on_region(kun28_damo2_path, kun28_start_path)
                if start_result:
                    match_loc, roi_left, roi_top = start_result
                    if match_loc:
                        # 匹配成功！计算按钮在全屏的中心坐标
                        (bx, by) = match_loc  # 这是在ROI内的坐标
                        start_x = roi_left + bx
                        start_y = roi_top + by
                        random_click(start_x, start_y, kun28_start_path)
                        time.sleep(15)
                        start_time = time.time()
                boss_result = find_image_on_screen(kun28_boss_path)
                if boss_result:
                    boss_x, boss_y = boss_result
                    random_click(boss_x, boss_y, kun28_boss_path)
                    time.sleep(15)
                    the_time = time.time()
                    while True:
                        print(time.time() - the_time)
                        if time.time() - the_time < 12:
                            jiangli_result = find_image_on_screen(kun28_jiangli_path)
                            if jiangli_result:
                                jiangli_x, jiangli_y = jiangli_result
                                random_click(jiangli_x, jiangli_y, kun28_jiangli_path)
                                time.sleep(1)
                                shishenlu_result = find_image_on_screen(shishenlu_path)
                                if shishenlu_result:
                                    shishenlu_x, shishenlu_y = shishenlu_result
                                    random_click(shishenlu_x, shishenlu_y, shishenlu_path)
                                    time.sleep(1)
                                print("点击奖励")
                        else:
                            break
                    break

if __name__ == "__main__":
    main()
