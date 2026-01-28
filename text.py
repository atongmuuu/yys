import cv2
import numpy as np
import pyautogui
import time
import random
import os

# pip install opencv-python numpy pyautogui pillow

def find_image_on_screen(template_path, threshold=0.7):
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
    
    # 读取模板图像
    template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
    if template is None:
        print(f"无法读取模板图像: {template_path}")
        return None
    
    # 截取屏幕
    screenshot = pyautogui.screenshot()
    screenshot = np.array(screenshot)
    screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2GRAY)
    
    # 使用模板匹配
    result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
    print(f"最大匹配值：{np.max(result)}")
    print(result)
    
    # 查找匹配位置
    locations = np.where(result >= threshold)
    
    if len(locations[0]) > 0:
        # 获取第一个匹配位置
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        top_left = max_loc
        return (top_left[0], top_left[1])
    
    return None

if __name__ == "__main__":
    kun28_mianju_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", "kun28_mianju.png")
    kun28_wuyan_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", "kun28_wuyan.png")
    kun28_mianju_result = find_image_on_screen(kun28_mianju_path)
    if kun28_mianju_result:
        kun28_mianju_x, kun28_mianju_y = kun28_mianju_result
        # 鼠标点击kun28_mianju_x, kun28_mianju_y位置并且不松开，然后向左移动700个像素
        # 确保鼠标不会跑到屏幕外导致异常
        pyautogui.FAILSAFE = True

        # 点击并按住不放
        pyautogui.mouseDown(x=kun28_mianju_x, y=kun28_mianju_y)


        # 向左移动700像素
        pyautogui.moveRel(-700, 0, duration=1)  # duration控制移动速度

        # 松开鼠标
        pyautogui.mouseUp()

    kun28_mianju_result = find_image_on_screen(kun28_wuyan_path)
    if kun28_mianju_result:
        kun28_mianju_x, kun28_mianju_y = kun28_mianju_result
        # 鼠标点击kun28_mianju_x, kun28_mianju_y位置并且不松开，然后向左移动700个像素
        # 确保鼠标不会跑到屏幕外导致异常
        pyautogui.FAILSAFE = True
        # 点击并按住不放
        pyautogui.mouseDown(x=kun28_mianju_x, y=kun28_mianju_y)
        # 向左移动700像素
        pyautogui.moveRel(-700, 0, duration=1)  # duration控制移动速度

        # 松开鼠标
        pyautogui.mouseUp()