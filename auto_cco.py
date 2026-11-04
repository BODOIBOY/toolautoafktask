import cv2
import mss
import numpy as np
import pyautogui
import time
import os
import random

# --- CẤU HÌNH BẢO MẬT & TỐC ĐỘ ---
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.05  # Giảm độ trễ mặc định của PyAutoGUI xuống tối đa
THRESHOLD = 0.85 

MONITOR = {"top": 0, "left": 0, "width": 1920, "height": 1080}

def load_image(filename):
    if not os.path.exists(filename):
        print(f"[!] LỖI: Không tìm thấy file '{filename}'.")
        exit(1)
    img = cv2.imread(filename, cv2.IMREAD_UNCHANGED)
    if img is None:
        print(f"[!] LỖI: Không thể đọc dữ liệu file '{filename}'.")
        exit(1)
    return img

def move_mouse_bezier(dest_x, dest_y, duration=0.25):
    """Đường cong Bezier tối ưu tốc độ (Chỉ 12 steps để tránh lag Windows)"""
    start_x, start_y = pyautogui.position()
    
    distance = ((dest_x - start_x)**2 + (dest_y - start_y)**2)**0.5
    if distance < 15:
        pyautogui.moveTo(dest_x, dest_y, _pause=False)
        return

    offset = int(distance * 0.2)
    cp1_x = start_x + (dest_x - start_x) * 0.3 + random.randint(-offset, offset)
    cp1_y = start_y + (dest_y - start_y) * 0.3 + random.randint(-offset, offset)
    cp2_x = start_x + (dest_x - start_x) * 0.7 + random.randint(-offset, offset)
    cp2_y = start_y + (dest_y - start_y) * 0.7 + random.randint(-offset, offset)
    
    steps = 12 # Tối ưu: 12 bước giúp di chuyển siêu nhanh mà vẫn giữ độ cong
    sleep_time = duration / steps
    
    for i in range(1, steps + 1):
        t = i / steps
        x = (1-t)**3 * start_x + 3*(1-t)**2 * t * cp1_x + 3*(1-t) * t**2 * cp2_x + t**3 * dest_x
        y = (1-t)**3 * start_y + 3*(1-t)**2 * t * cp1_y + 3*(1-t) * t**2 * cp2_y + t**3 * dest_y
        pyautogui.moveTo(int(x), int(y), _pause=False)
        time.sleep(sleep_time)
        
    pyautogui.moveTo(dest_x, dest_y, _pause=False)

def find_and_click(template, monitor_region, threshold=0.85):
    with mss.mss() as sct:
        img = np.array(sct.grab(monitor_region))
        frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR) if img.shape[2] == 4 else img
        temp = cv2.cvtColor(template, cv2.COLOR_BGRA2BGR) if template.shape[2] == 4 else template
            
        result = cv2.matchTemplate(frame, temp, cv2.TM_CCOEFF_NORMED)
        loc = np.where(result >= threshold)
        
        for pt in zip(*loc[::-1]):
            h, w = temp.shape[:2]
            
            # Sai số tâm điểm
            offset_x = random.randint(-w // 4, w // 4)
            offset_y = random.randint(-h // 4, h // 4)
            target_x = monitor_region["left"] + pt[0] + (w // 2) + offset_x
            target_y = monitor_region["top"] + pt[1] + (h // 2) + offset_y
            
            # Rê chuột đường cong tốc độ cao (0.15 - 0.25s)
            move_mouse_bezier(target_x, target_y, duration=random.uniform(0.15, 0.25))
            time.sleep(random.uniform(0.02, 0.05))
            
            # Click kèm rung nhẹ chống Anti-Bot
            pyautogui.mouseDown(_pause=False)
            rung_x = random.choice([-1, 1])
            rung_y = random.choice([-1, 1])
            pyautogui.moveTo(target_x + rung_x, target_y + rung_y, duration=0.02, _pause=False)
            pyautogui.mouseUp(_pause=False)
            
            return True
    return False

def check_exists(template, monitor_region, threshold=0.85):
    """Quét siêu tốc xem ảnh có tồn tại trên màn hình không (KHÔNG CLICK)"""
    with mss.mss() as sct:
        img = np.array(sct.grab(monitor_region))
        frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR) if img.shape[2] == 4 else img
        temp = cv2.cvtColor(template, cv2.COLOR_BGRA2BGR) if template.shape[2] == 4 else template
            
        result = cv2.matchTemplate(frame, temp, cv2.TM_CCOEFF_NORMED)
        loc = np.where(result >= threshold)
        if len(loc[0]) > 0:
            return True
    return False

def wait_and_click_step(template, monitor_region, step_name, timeout=3):
    start_time = time.time()
    while time.time() - start_time < timeout:
        if find_and_click(template, monitor_region, threshold=THRESHOLD):
            print(f"[{time.strftime('%H:%M:%S')}] [>] Đã hoàn thành bước: {step_name}")
            return True
        time.sleep(0.15)
    print(f"[{time.strftime('%H:%M:%S')}] [!] Thất bại, không tìm thấy: {step_name}")
    return False

def main():
    print("="*40)
    print("    TOOL AUTO CYBERCODE ONLINE (SIÊU TỐC)")
    print("="*40)
    print("1. Thu Thập AFK")
    print("2. Triển Khai Bot Nông XP")
    print("3. Tái Chế Tự Động (1000)")
    print("0. Thoát")
    print("-" * 40)
    
    choice = input("Nhập lựa chọn (0/1/2/3): ").strip()
    
    claim_img = load_image('claim_btn.png')
    full_img = load_image('inventory_full.png')
    refresh_img = load_image('refresh_btn.png')
    
    last_refresh_time = 0 
    
    if choice == '1':
        task_img = load_image('scav_btn.png')
        confirm_img = load_image('start_btn.png')
        input_box = load_image('input_box.png')
        task_name = "Thu Thập AFK"
        
    elif choice == '2':
        task_img = load_image('botfarm_btn.png')
        confirm_img = load_image('start_btn.png')
        task_name = "Triển Khai Bot"
        
    elif choice == '3':
        tc_auto = load_image('taiche_auto.png')
        tc_plus = load_image('plus_btn.png')
        tc_vattu = load_image('vattu_yte.png')
        tc_input = load_image('input_box_1.png')
        tc_xacnhan = load_image('xac_nhan.png')
        tc_confirm = load_image('taiche_confirm.png')
        task_name = "Chuỗi Tái Chế Tự Động"
        
    elif choice == '0':
        exit(0)
    else:
        exit(1)

    print(f"\n>>> BẮT ĐẦU: {task_name.upper()} <<<")
    print("ÉP GÓC CHUỘT ĐỂ DỪNG KHẨN CẤP!\n")

    while True:
        try:
            # --- ƯU TIÊN 0: Lấy tất cả & Kiểm tra rương đầy ---
            if find_and_click(claim_img, MONITOR, threshold=THRESHOLD):
                print(f"[{time.strftime('%H:%M:%S')}] [+] Đã bấm nhận thưởng, đang kiểm tra...")
                time.sleep(0.3) 
                
                if check_exists(full_img, MONITOR, threshold=THRESHOLD):
                    print("\n" + "!"*50)
                    print(f"[{time.strftime('%H:%M:%S')}] [!!!] BÁO ĐỘNG: ĐÃ MAX THÀNH PHẨM (RƯƠNG ĐẦY)!")
                    print("[!] Đang tự động ngắt tool để bảo vệ an toàn...")
                    print("!"*50 + "\n")
                    import winsound
                    winsound.Beep(1000, 1500) 
                    break 
                
                time.sleep(0.8) 

            # --- ƯU TIÊN 1: Làm mới thủ công (60s Cooldown) ---
            if time.time() - last_refresh_time > 60:
                if find_and_click(refresh_img, MONITOR, threshold=THRESHOLD):
                    print(f"[{time.strftime('%H:%M:%S')}] [*] Đã bấm Làm mới thủ công (chống kẹt).")
                    last_refresh_time = time.time()
                    time.sleep(0.5)
                    continue 

            # --- XỬ LÝ CHẾ ĐỘ 1 & 2 ---
            if choice in ['1', '2']:
                if find_and_click(confirm_img, MONITOR, threshold=THRESHOLD):
                    print(f"[{time.strftime('%H:%M:%S')}] [>] Đã bấm BẮT ĐẦU!")
                    time.sleep(1.2)
                elif find_and_click(task_img, MONITOR, threshold=THRESHOLD):
                    print(f"[{time.strftime('%H:%M:%S')}] [>] Mở bảng tác vụ...")
                    time.sleep(0.8)
                    
                    if choice == '1': 
                        if find_and_click(input_box, MONITOR, threshold=THRESHOLD):
                            time.sleep(0.2)
                            pyautogui.hotkey('ctrl', 'a')
                            time.sleep(0.05)
                            pyautogui.press('backspace')
                            pyautogui.write('10')
                            time.sleep(0.3)

            # --- XỬ LÝ CHẾ ĐỘ 3 ---
            elif choice == '3':
                if find_and_click(tc_auto, MONITOR, threshold=THRESHOLD):
                    print(f"\n[{time.strftime('%H:%M:%S')}] [*] Kích hoạt chuỗi Tái Chế...")
                    time.sleep(0.5)
                    if wait_and_click_step(tc_plus, MONITOR, "Dấu +", timeout=3):
                        time.sleep(0.3)
                        if wait_and_click_step(tc_vattu, MONITOR, "Vật Tư Y Tế", timeout=3):
                            time.sleep(0.5)
                            if wait_and_click_step(tc_input, MONITOR, "Ô nhập số lượng", timeout=3):
                                time.sleep(0.2)
                                pyautogui.hotkey('ctrl', 'a')
                                time.sleep(0.05)
                                pyautogui.press('backspace')
                                pyautogui.write('1000') 
                                print(f"[{time.strftime('%H:%M:%S')}] [>] Đã gõ: 1000")
                                time.sleep(0.3)
                                if wait_and_click_step(tc_xacnhan, MONITOR, "Xác Nhận", timeout=3):
                                    time.sleep(0.5)
                                    wait_and_click_step(tc_confirm, MONITOR, "Tái Chế Cuối", timeout=3)
                                    print(f"[{time.strftime('%H:%M:%S')}] [V] HOÀN THÀNH 1 VÒNG TÁI CHẾ!\n")
            
            time.sleep(0.3)
            
        except pyautogui.FailSafeException:
            print(f"\n[{time.strftime('%H:%M:%S')}] [!] Đã ngắt Tool bằng chuột!")
            break

if __name__ == "__main__":
    main()