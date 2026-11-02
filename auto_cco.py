import cv2
import mss
import numpy as np
import pyautogui
import time
import os

# --- CẤU HÌNH ---
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.2 
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

def find_and_click(template, monitor_region, threshold=0.8):
    with mss.mss() as sct:
        img = np.array(sct.grab(monitor_region))
        frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR) if img.shape[2] == 4 else img
        temp = cv2.cvtColor(template, cv2.COLOR_BGRA2BGR) if template.shape[2] == 4 else template
            
        result = cv2.matchTemplate(frame, temp, cv2.TM_CCOEFF_NORMED)
        loc = np.where(result >= threshold)
        
        for pt in zip(*loc[::-1]):
            h, w = temp.shape[:2]
            center_x = monitor_region["left"] + pt[0] + w // 2
            center_y = monitor_region["top"] + pt[1] + h // 2
            pyautogui.click(x=center_x, y=center_y)
            return True
    return False

def check_exists(template, monitor_region, threshold=0.8):
    """Quét xem ảnh có tồn tại trên màn hình không (KHÔNG CLICK)"""
    with mss.mss() as sct:
        img = np.array(sct.grab(monitor_region))
        frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR) if img.shape[2] == 4 else img
        temp = cv2.cvtColor(template, cv2.COLOR_BGRA2BGR) if template.shape[2] == 4 else template
            
        result = cv2.matchTemplate(frame, temp, cv2.TM_CCOEFF_NORMED)
        loc = np.where(result >= threshold)
        if len(loc[0]) > 0:
            return True
    return False

def wait_and_click_step(template, monitor_region, step_name, timeout=5):
    start_time = time.time()
    while time.time() - start_time < timeout:
        if find_and_click(template, monitor_region, threshold=THRESHOLD):
            print(f"[{time.strftime('%H:%M:%S')}] [>] Đã hoàn thành bước: {step_name}")
            return True
        time.sleep(0.3)
    print(f"[{time.strftime('%H:%M:%S')}] [!] Thất bại, không tìm thấy: {step_name}")
    return False

def main():
    print("="*40)
    print("    TOOL AUTO CYBERCODE ONLINE (CCO)")
    print("="*40)
    print("1. Thu Thập AFK")
    print("2. Triển Khai Bot Nông XP")
    print("3. Tái Chế Tự Động (1000)")
    print("0. Thoát")
    print("-" * 40)
    
    choice = input("Nhập lựa chọn (0/1/2/3): ").strip()
    
    claim_img = load_image('claim_btn.png')
    full_img = load_image('inventory_full.png') # Ảnh báo lỗi
    
    last_refresh_time = 0 
    
    if choice == '1':
        task_img = load_image('scav_btn.png')
        confirm_img = load_image('start_btn.png')
        input_box = load_image('input_box.png')
        refresh_img = load_image('refresh_btn.png')
        task_name = "Thu Thập AFK"
        
    elif choice == '2':
        task_img = load_image('botfarm_btn.png')
        confirm_img = load_image('start_btn.png')
        refresh_img = load_image('refresh_btn.png')
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
            # Ưu tiên 0: Lấy tất cả và Kiểm tra Rương
            if find_and_click(claim_img, MONITOR, threshold=THRESHOLD):
                print(f"[{time.strftime('%H:%M:%S')}] [+] Đã bấm nhận thưởng, đang kiểm tra...")
                time.sleep(0.5) # Đợi game hiển thị thông báo lỗi (nếu có)
                
                # Quét màn hình tìm dòng chữ báo rương đầy
                if check_exists(full_img, MONITOR, threshold=THRESHOLD):
                    print("\n" + "!"*50)
                    print(f"[{time.strftime('%H:%M:%S')}] [!!!] BÁO ĐỘNG: ĐÃ MAX THÀNH PHẨM (RƯƠNG ĐẦY)!")
                    print("[!] Đang tự động ngắt tool để bảo vệ an toàn...")
                    print("!"*50 + "\n")
                    
                    import winsound
                    winsound.Beep(1000, 1500) # Kêu Bíp 1.5s
                    break # Thoát hoàn toàn tool
                
                time.sleep(1.5) # Nhận thưởng thành công thì chờ tiếp
            
            # XỬ LÝ CHẾ ĐỘ 1 & 2
            if choice in ['1', '2']:
                if find_and_click(confirm_img, MONITOR, threshold=THRESHOLD):
                    print(f"[{time.strftime('%H:%M:%S')}] [>] Đã bấm BẮT ĐẦU!")
                    time.sleep(2)
                elif find_and_click(task_img, MONITOR, threshold=THRESHOLD):
                    print(f"[{time.strftime('%H:%M:%S')}] [>] Mở bảng tác vụ...")
                    time.sleep(1.5)
                    
                    if choice == '1': 
                        if find_and_click(input_box, MONITOR, threshold=THRESHOLD):
                            time.sleep(0.5)
                            pyautogui.hotkey('ctrl', 'a')
                            time.sleep(0.1)
                            pyautogui.press('backspace')
                            pyautogui.write('10')
                            time.sleep(0.5)
                            
                elif time.time() - last_refresh_time > 60:
                    if find_and_click(refresh_img, MONITOR, threshold=THRESHOLD):
                        print(f"[{time.strftime('%H:%M:%S')}] [*] Đã bấm Làm mới thủ công (chống kẹt).")
                        last_refresh_time = time.time()
                        time.sleep(1)

            # XỬ LÝ CHẾ ĐỘ 3
            elif choice == '3':
                if find_and_click(tc_auto, MONITOR, threshold=THRESHOLD):
                    print(f"\n[{time.strftime('%H:%M:%S')}] [*] Kích hoạt chuỗi Tái Chế...")
                    time.sleep(1)
                    if wait_and_click_step(tc_plus, MONITOR, "Dấu +", timeout=4):
                        time.sleep(0.5)
                        if wait_and_click_step(tc_vattu, MONITOR, "Vật Tư Y Tế", timeout=4):
                            time.sleep(1)
                            if wait_and_click_step(tc_input, MONITOR, "Ô nhập số lượng", timeout=4):
                                time.sleep(0.5)
                                pyautogui.hotkey('ctrl', 'a')
                                time.sleep(0.1)
                                pyautogui.press('backspace')
                                pyautogui.write('1000') 
                                print(f"[{time.strftime('%H:%M:%S')}] [>] Đã gõ: 1000")
                                time.sleep(0.5)
                                if wait_and_click_step(tc_xacnhan, MONITOR, "Xác Nhận", timeout=4):
                                    time.sleep(1)
                                    wait_and_click_step(tc_confirm, MONITOR, "Tái Chế Cuối", timeout=4)
                                    print(f"[{time.strftime('%H:%M:%S')}] [V] HOÀN THÀNH 1 VÒNG TÁI CHẾ!\n")
            
            time.sleep(1)
            
        except pyautogui.FailSafeException:
            print(f"\n[{time.strftime('%H:%M:%S')}] [!] Đã ngắt Tool bằng chuột!")
            break

if __name__ == "__main__":
    main()