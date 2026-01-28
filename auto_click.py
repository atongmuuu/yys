import cv2
import numpy as np
import pyautogui
import time
import random
import os
import sys
from multiprocessing import Process, Value, Lock
import requests

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
    """简化版：如果不需要去重处理，使用这个版本"""
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
        now_time = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
        cv2.imwrite(f"screenshot/{now_time}.png", roi)
        match_loc, confidence = find_button_in_roi(roi, pk_template)
        return match_loc, roi_left, roi_top
    
    return None

def random_click(x, y, name = "ok", random_range = 40):
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
    print(f"已点击位置: ({click_x}, {click_y}), {name}")
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

def tansuo_end(go_time, current_time, lock):
    # 一直监听勾玉协作
    shuju_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", "kun28_shuju.png")
    end_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", "end.png")
    while True:
        shuju_result = find_image_on_screen(shuju_path)
        if shuju_result:
            shuju_x, shuju_y = shuju_result
            random_click(shuju_x + random.randint(50, 200), shuju_y + random.randint(60, 200))
            time.sleep(1)
            end_result = find_image_on_screen(end_path)
            if end_result:
                end_x, end_y = end_result
                random_click(end_x, end_y)
                with lock:
                    go_time.value = 1
                    current_time.value = time.time()


def huijuan(xiaoHuiJuan_count, zhongHuiJuan_count, daHuiJuan_count, control_count,  lock):
    # 一直绘卷
    xiaoHuiJuan = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", "xiaoHuiJuan.png")
    zhongHuiJuan = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", "zhongHuiJuan.png")
    daHuiJuan = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", "daHuiJuan.png")
    while True:
        with lock:
            current_control_count = control_count.value
        if current_control_count:
            xiaoHuiJuan_result = find_image_on_screen(xiaoHuiJuan)
            zhongHuiJuan_result = find_image_on_screen(zhongHuiJuan)
            daHuiJuan_result = find_image_on_screen(daHuiJuan)
            if xiaoHuiJuan_result or zhongHuiJuan_result or daHuiJuan_result:
                with lock:
                    if xiaoHuiJuan_result:
                        xiaoHuiJuan_count.value += 1    
                    elif zhongHuiJuan_result:
                        zhongHuiJuan_count.value += 1    
                    elif daHuiJuan_result:
                        daHuiJuan_count.value += 1
                    control_count.value = 0


def main():
    end_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", "end.png")
    fanhui_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", "fanhui.png")
    guanbi_path = ""
    kun28_start_path = ""
    shishenlu_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", "yu_shishenlu.png")
    xiezhan_path = ""
    choice1 = ""
    choice2 = ""
    choice3 = ""
    choice4 = ""
    scan_huijuan = True


    choice1 = input("请输入1或2或3或4。1：打活动，2：打御灵副本，3：打组队御魂，4：打困28: ").strip()
    if choice1 == "1":
        kun28_start_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", "hd_start.png")
        scan_huijuan = False
        choice2 = input("请输入y或n。y：可以点击协战，n：不可以点击协战: ").strip().lower()
        if choice2 == "y":
            xiezhan_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", "hd_xiezhan.png")
            guanbi_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", "guanbi.png")
        else:
            pass
    elif choice1 == "2":
        kun28_start_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", "yu_start.png")
    elif choice1 == "3":
        choice4 = input("请输入1或2或3。1：一台电脑组队，2：两台电脑组队的房主，3：两台电脑组队的队员: ").strip()
        if choice4 == "1":
            pass
        elif choice4 == "2":
            pass
        elif choice4 == "3":
            pass
    elif choice1 == "4":
        tupo_all_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", "tupo_all.png")
        tupo_start_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", "tupo_start.png")
        tupo_youshangjiao_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", "tupo_youshangjiao.png")
        tupo_jingong_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", "tupo_jingong.png")
        kun28_baoxiang_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", "kun28_baoxiang.png")
        kun28_guanbi_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", "kun28_guanbi.png")
        kun28_ershiba_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", "kun28_ershiba.png")
        kun28_tansuo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", "kun28_tansuo.png")
        kun28_mianju_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", "kun28_mianju.png")
        kun28_wuyan_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", "kun28_wuyan.png")
        kun28_damo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", "kun28_damo.png")
        kun28_damo2_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", "kun28_damo2.png")
        kun28_start_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", "kun28_start.png")
        kun28_queding_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", "kun28_queding.png")
        kun28_boss_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", "kun28_boss.png")
        kun28_jiangli_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", "kun28_jiangli.png")
    else:
        # 退出并打印
        print("请正确选择1，2，3")
        sys.exit()


    choice3 = input("请输入y或n。y：可以点击式神录，n：不可以点击式神录: ").strip().lower()
    if choice3 == "y":
        if choice1 == "1":
            shishenlu_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", "hd_shishenlu.png")
        else:
            shishenlu_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", "yu_shishenlu.png")
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
        control_scan = Value('i', 0) 
        lock2 = Lock()
        process2 = Process(target=huijuan, args=(xiaoHuiJuan_count, zhongHuiJuan_count, daHuiJuan_count, control_scan, lock2))
        process2.daemon = True
        process2.start()

    if choice4 == "3":
        while True:
            end_result = find_image_on_screen(end_path)
            if end_result:
                end_x, end_y = end_result
                random_click(end_x, end_y)
                time.sleep(1) 

    while True and choice4 != "3" and choice1 != "4":
        if run_count > 10000:
            print("已执行10000次，退出", flush=True)
            break
        # 识别start.png
        delay = 0
        start_result = find_image_on_screen(kun28_start_path)
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
            if scan_huijuan:
                with lock1:
                    control_scan.value = 1
            # 识别end.png
            try_time = 1
            while True:
                # 由一场战斗时间决定，其基础上加12-16s
                message = ""
                delay = random.uniform(24, 28)
                print(f"第{try_time}次等待{delay:.2f}s", flush=True, end="-->")
                time.sleep(delay)
                end_result = find_image_on_screen(end_path)
                if end_result:
                    end_x, end_y = end_result
                    random_click(end_x, end_y)
                    # time.sleep(0.5) # 防止时间恰好，点击两次
                    # random_click(end_x, end_y)
                    time.sleep(1)
                    if choice4 == "1":
                        end_result = find_image_on_screen(end_path)
                        if end_result:
                            end_x, end_y = end_result
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
                            message = f"运行{run_count}次，接到勾协，小绘卷 {current_xiaohuijuan_count} 次, 中绘卷 {current_zhonghuijuan_count} 次, 大绘卷 {current_dahuijuan_count} 次"
                        else:
                            message = f"运行{run_count}次，接到勾协"
                    else:
                        if scan_huijuan:
                            message = f"运行{run_count}次，小绘卷 {current_xiaohuijuan_count} 次, 中绘卷 {current_zhonghuijuan_count} 次, 大绘卷 {current_dahuijuan_count} 次"
                        else:
                            message = f"运行{run_count}次"
                    if run_count % 100 == 0:
                        send_feishu_webhook(message)
                        print(message)
                    else:
                        print(message)
                    break
                else:
                    try_time += 1
                    if try_time > 3:
                        break
        else:
            pass

    if choice1 == "4":
        # 启动识别探索结束，然后点击end.png
        go_time = Value('i', 1)  # 'i' 表示整型
        current_time = Value('f', 0) # 使用浮点型
        lock3 = Lock()
        process3 = Process(target=tansuo_end, args=(go_time, current_time, lock3))
        process3.daemon = True
        process3.start()

    while True and choice1 == "4":
        in_tupo = False
        time.sleep(2)
        # 识别关闭
        kun28_guanbi_result = find_image_on_screen(kun28_guanbi_path)
        if kun28_guanbi_result:
            kun28_guanbi_x, kun28_guanbi_y = kun28_guanbi_result
            random_click(kun28_guanbi_x, kun28_guanbi_y)
            time.sleep(2)
        # 识别宝箱
        for i in range(3):
            kun28_baoxiang_result = find_image_on_screen(kun28_baoxiang_path)
            if kun28_baoxiang_result:
                kun28_baoxiang_x, kun28_baoxiang_y = kun28_baoxiang_result
                random_click(kun28_baoxiang_x, kun28_baoxiang_y)
                time.sleep(2)
        # 识别突破
        tupo_all_result = find_image_on_screen(tupo_all_path)
        if 1:
            in_tupo = True
            tupo_start_result = find_image_on_screen(tupo_start_path)
            if tupo_start_result:
                tupo_start_x, tupo_start_y = tupo_start_result
                random_click(tupo_start_x, tupo_start_y, tupo_start_path)
                time.sleep(2)
                while True:
                    tupo_youshangjiao_result = find_image_on_screen(tupo_youshangjiao_path, 0.9)
                    if tupo_youshangjiao_result:
                        tupo_youshangjiao_x, tupo_youshangjiao_y = tupo_youshangjiao_result
                        random_click(tupo_youshangjiao_x, tupo_youshangjiao_y, tupo_youshangjiao_path)
                        time.sleep(1)
                        tupo_jingong_result = find_image_on_screen(tupo_jingong_path)
                        if tupo_jingong_result:
                            tupo_jingong_x, tupo_jingong_y = tupo_jingong_result
                            random_click(tupo_jingong_x, tupo_jingong_y, tupo_jingong_path)
                            time.sleep(2)
                    # tupo_0_result = find_image_on_screen(tupo_0_path)
        # 识别kun28_ershiba.png
        ershiba_result = find_image_on_screen(kun28_ershiba_path)
        if ershiba_result:
            ershiba_x, ershiba_y = ershiba_result
            random_click(ershiba_x, ershiba_y)
            time.sleep(5)
        # 识别kun28_tansuo.png
        tansuo_result = find_image_on_screen(kun28_tansuo_path)
        if tansuo_result:
            tansuo_x, tansuo_y = tansuo_result
            random_click(tansuo_x, tansuo_y)
            time.sleep(5)
        # 识别kun28_damo.png和kun28_start.png
        start_time = time.time()
        times = 1 
        while True and not in_tupo:
            with lock3:
                current_go_time = go_time.value
                start_time = max(current_time.value, start_time)
            if current_go_time and times <=2 :
                print(current_go_time, time.time() - start_time)
                if time.time() - start_time > 8:
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
            elif times > 2:
                fanhui_result = find_image_on_screen(fanhui_path)
                if fanhui_result:
                    fanhui_x, fanhui_y = fanhui_result
                    random_click(fanhui_x, fanhui_y)
                    time.sleep(1)
                    kun28_queding_result = find_image_on_screen(kun28_queding_path)
                    if kun28_queding_result:
                        kun28_queding_x, kun28_queding_y = kun28_queding_result
                        random_click(kun28_queding_x, kun28_queding_y)
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
                    random_click(start_x, start_y)
                    with lock3:
                        go_time.value = 0
            start_result = find_image_on_region(kun28_damo2_path, kun28_start_path)
            if start_result:
                match_loc, roi_left, roi_top = start_result
                if match_loc:
                    # 匹配成功！计算按钮在全屏的中心坐标
                    (bx, by) = match_loc  # 这是在ROI内的坐标
                    start_x = roi_left + bx
                    start_y = roi_top + by
                    random_click(start_x, start_y)
                    time.sleep(15)
            boss_result = find_image_on_screen(kun28_boss_path)
            if boss_result:
                boss_x, boss_y = boss_result
                random_click(boss_x, boss_y)
                while True:
                    jiangli_result = find_image_on_screen(kun28_jiangli_path)
                    if jiangli_result:
                        jiangli_x, jiangli_y = jiangli_result
                        random_click(jiangli_x, jiangli_y)
                        time.sleep(1)
                        shishenlu_result = find_image_on_screen(shishenlu_path)
                        if shishenlu_result:
                            shishenlu_x, shishenlu_y = shishenlu_result
                            random_click(shishenlu_x, shishenlu_y)
                            time.sleep(1)
                        print("点击奖励")
                    else:
                        break
                break

if __name__ == "__main__":
    main()