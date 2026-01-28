import cv2
import numpy as np
import pyautogui
import os

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
    template = cv2.imread(template_path)
    if template is None:
        print(f"无法读取模板图像: {template_path}")
        return None
    
    # 截取屏幕
    screenshot = pyautogui.screenshot()
    screenshot = np.array(screenshot)
    screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
    
    
    # 使用模板匹配
    result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
    
    # 查找匹配位置
    locations = np.where(result >= threshold)
    
    if len(locations[0]) > 0:
        # 获取第一个匹配位置
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        top_left = max_loc
        x = top_left[0]
        y = top_left[1]
        print(x,y)
        cv2.rectangle(screenshot, (x-180, y), (x + 220, y-400), (0, 0, 255), 2)
        # 显示处理后的图像（可选）
        cv2.imshow('Detected Image', screenshot)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    
    return None

gouyu_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", "kun28_damo.png")
find_image_on_screen(gouyu_path)
