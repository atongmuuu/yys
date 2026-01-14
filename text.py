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
    gouyu_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", "guanbi.png")
    start_time = time.time()
    res = find_image_on_screen(gouyu_path)
    print(time.time() - start_time)
    print(res)