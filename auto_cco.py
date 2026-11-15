import cv2
import mss
import numpy as np
import pyautogui
import time
import os
import random
import keyboard
import winsound

# --- CẤU HÌNH BẢO MẬT & TỐC ĐỘ ---
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.05  
THRESHOLD = 0.85 

MONITOR = {"top": 0, "left": 0, "width": 1920, "height": 1080}

# --- BIẾN TRẠNG THÁI TẠM DỪNG ---
is_paused = False

def toggle_pause():
    """Hàm bật/tắt trạng thái tạm dừng khi nhấn F9"""
    global is_paused
    is_paused = not is_paused
    if is_paused:
        print(f"\n[{time.strftime('%H:%M:%S')}] [II] ĐÃ TẠM DỪNG TOOL! (Nhấn F9 để chạy tiếp)")
    else:
        print(f"\n[{time.strftime('%H:%M:%S')}] [>] TIẾP TỤC CHẠY!")

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
    """Đường cong Bezier tối ưu tốc độ (12 steps)"""
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
    
    steps = 12 
    sleep_time = duration / steps
    
    for i in range(1, steps + 1):
        t = i / steps
        x = (1-t)**3 * start_x + 3*(1-t)**2 * t * cp1_x + 3*(1-t) * t**2 * cp2_x + t**3 * dest_x
        y = (1-t)**3 * start_y + 3*(1-t)**2 * t * cp1_y + 3*(1-t) * t**2 * cp2_y + t**3 * dest_y
        pyautogui.moveTo(int(x), int(y), _pause=False)
        time.sleep(sleep_time)
        
    pyautogui.moveTo(dest_x, dest_y, _pause=False)

def unhover_mouse():
    """Dời chuột ra lề trống an toàn để tránh hiệu ứng :hover làm đổi màu nút Claim"""
    safe_x = MONITOR["left"] + random.randint(60, 120)
    safe_y = MONITOR["top"] + random.randint(250, 420)
    move_mouse_bezier(safe_x, safe_y, duration=0.15)

def human_scroll(scroll_amount=-500):
    """Giả lập lăn chuột người thật"""
    center_x = MONITOR["left"] + MONITOR["width"] // 2
    center_y = MONITOR["top"] + MONITOR["height"] // 2
    move_mouse_bezier(center_x, center_y, duration=0.2)
    time.sleep(random.uniform(0.1, 0.2))
    
    steps = random.randint(4, 7)
    step_scroll = scroll_amount // steps
    
    for _ in range(steps):
        pyautogui.scroll(step_scroll)
        time.sleep(random.uniform(0.05, 0.15))

def find_and_click(template, monitor_region, threshold=0.85):
    with mss.mss() as sct:
        img = np.array(sct.grab(monitor_region))
        frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR) if img.shape[2] == 4 else img
        temp = cv2.cvtColor(template, cv2.COLOR_BGRA2BGR) if template.shape[2] == 4 else template
            
        result = cv2.matchTemplate(frame, temp, cv2.TM_CCOEFF_NORMED)
        loc = np.where(result >= threshold)
        
        for pt in zip(*loc[::-1]):
            h, w = temp.shape[:2]
            
            offset_x = random.randint(-w // 4, w // 4)
            offset_y = random.randint(-h // 4, h // 4)
            target_x = monitor_region["left"] + pt[0] + (w // 2) + offset_x
            target_y = monitor_region["top"] + pt[1] + (h // 2) + offset_y
            
            move_mouse_bezier(target_x, target_y, duration=random.uniform(0.15, 0.25))
            time.sleep(random.uniform(0.02, 0.05))
            
            pyautogui.mouseDown(_pause=False)
            rung_x = random.choice([-1, 1])
            rung_y = random.choice([-1, 1])
            pyautogui.moveTo(target_x + rung_x, target_y + rung_y, duration=0.02, _pause=False)
            pyautogui.mouseUp(_pause=False)
            
            return True
    return False

def find_and_click_with_rect(template, monitor_region, threshold=0.85):
    """Tìm, click vào ảnh và trả về kèm tọa độ khung (x, y, w, h) trên màn hình."""
    with mss.mss() as sct:
        img = np.array(sct.grab(monitor_region))
        frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR) if img.shape[2] == 4 else img
        temp = cv2.cvtColor(template, cv2.COLOR_BGRA2BGR) if template.shape[2] == 4 else template
            
        result = cv2.matchTemplate(frame, temp, cv2.TM_CCOEFF_NORMED)
        loc = np.where(result >= threshold)
        
        for pt in zip(*loc[::-1]):
            h, w = temp.shape[:2]
            screen_x = monitor_region["left"] + pt[0]
            screen_y = monitor_region["top"] + pt[1]
            
            offset_x = random.randint(-w // 4, w // 4)
            offset_y = random.randint(-h // 4, h // 4)
            target_x = screen_x + (w // 2) + offset_x
            target_y = screen_y + (h // 2) + offset_y
            
            move_mouse_bezier(target_x, target_y, duration=random.uniform(0.15, 0.25))
            time.sleep(random.uniform(0.02, 0.05))
            
            pyautogui.mouseDown(_pause=False)
            rung_x = random.choice([-1, 1])
            rung_y = random.choice([-1, 1])
            pyautogui.moveTo(target_x + rung_x, target_y + rung_y, duration=0.02, _pause=False)
            pyautogui.mouseUp(_pause=False)
            
            return True, (screen_x, screen_y, w, h)
    return False, None

def check_exists(template, monitor_region, threshold=0.85):
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
        if is_paused:
            return False
            
        if find_and_click(template, monitor_region, threshold=THRESHOLD):
            print(f"[{time.strftime('%H:%M:%S')}] [>] Đã hoàn thành bước: {step_name}")
            return True
        time.sleep(0.15)
    print(f"[{time.strftime('%H:%M:%S')}] [!] Thất bại, không tìm thấy: {step_name}")
    return False

def ensure_tab_active(bright_template, dark_template, tab_name, monitor_region, threshold=0.82):
    """Kiểm tra trạng thái nút tab (Chế tạo / Material): sáng thì bỏ qua, tối thì mới bấm."""
    with mss.mss() as sct:
        img = np.array(sct.grab(monitor_region))
        frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR) if img.shape[2] == 4 else img

    bright_bgr = cv2.cvtColor(bright_template, cv2.COLOR_BGRA2BGR) if bright_template.shape[2] == 4 else bright_template
    dark_bgr = cv2.cvtColor(dark_template, cv2.COLOR_BGRA2BGR) if dark_template.shape[2] == 4 else dark_template

    res_dark = cv2.matchTemplate(frame, dark_bgr, cv2.TM_CCOEFF_NORMED)
    _, max_val_dark, _, max_loc_dark = cv2.minMaxLoc(res_dark)

    res_bright = cv2.matchTemplate(frame, bright_bgr, cv2.TM_CCOEFF_NORMED)
    _, max_val_bright, _, max_loc_bright = cv2.minMaxLoc(res_bright)

    if max(max_val_dark, max_val_bright) < threshold:
        print(f"[{time.strftime('%H:%M:%S')}] [!] Không tìm thấy nút {tab_name} trên màn hình.")
        return False

    if max_val_dark >= max_val_bright:
        pt = max_loc_dark
        h, w = dark_bgr.shape[:2]
    else:
        pt = max_loc_bright
        h, w = bright_bgr.shape[:2]

    roi_gray = cv2.cvtColor(frame[pt[1]:pt[1]+h, pt[0]:pt[0]+w], cv2.COLOR_BGR2GRAY)
    bright_gray = cv2.cvtColor(bright_bgr, cv2.COLOR_BGR2GRAY)
    dark_gray = cv2.cvtColor(dark_bgr, cv2.COLOR_BGR2GRAY)

    current_text_lum = np.percentile(roi_gray, 90)
    bright_ref_lum = np.percentile(bright_gray, 90)
    dark_ref_lum = np.percentile(dark_gray, 90)

    if abs(current_text_lum - bright_ref_lum) <= abs(current_text_lum - dark_ref_lum):
        print(f"[{time.strftime('%H:%M:%S')}] [>] Nút {tab_name} đang SÁNG sẵn, không cần bấm.")
        return True
    else:
        print(f"[{time.strftime('%H:%M:%S')}] [*] Nút {tab_name} đang TỐI, tiến hành bấm...")
        offset_x = random.randint(-w // 4, w // 4)
        offset_y = random.randint(-h // 4, h // 4)
        target_x = monitor_region["left"] + pt[0] + (w // 2) + offset_x
        target_y = monitor_region["top"] + pt[1] + (h // 2) + offset_y

        move_mouse_bezier(target_x, target_y, duration=random.uniform(0.15, 0.25))
        time.sleep(random.uniform(0.02, 0.05))
        pyautogui.mouseDown(_pause=False)
        pyautogui.moveTo(target_x + random.choice([-1, 1]), target_y + random.choice([-1, 1]), duration=0.02, _pause=False)
        pyautogui.mouseUp(_pause=False)
        print(f"[{time.strftime('%H:%M:%S')}] [>] Đã bấm chọn tab {tab_name}.")
        time.sleep(0.4)
        return True

# --- HÀM THỰC THI ĐƠN LẺ CHO RÃ, CRAFT BALO & CHUYỂN VÒNG ---
def execute_recycle_once(tc_auto, tc_plus, tc_vattu, tc_input, tc_xacnhan, tc_confirm):
    """Thực hiện 1 lượt Tái chế (1000). Trả về True nếu kích hoạt thành công."""
    if find_and_click(tc_auto, MONITOR, threshold=THRESHOLD):
        print(f"\n[{time.strftime('%H:%M:%S')}] [*] Kích hoạt chuỗi Tái Chế...")
        time.sleep(0.5)
        if wait_and_click_step(tc_plus, MONITOR, "Dấu +", timeout=3):
            time.sleep(0.3)
            if wait_and_click_step(tc_vattu, MONITOR, "Vật Tư Y Tế (Rã)", timeout=3):
                time.sleep(0.5)
                if wait_and_click_step(tc_input, MONITOR, "Ô nhập số lượng", timeout=3):
                    time.sleep(0.2)
                    pyautogui.hotkey('ctrl', 'a')
                    time.sleep(0.05)
                    pyautogui.press('backspace')
                    pyautogui.write('1000')
                    time.sleep(0.3)
                    if wait_and_click_step(tc_xacnhan, MONITOR, "Xác Nhận", timeout=3):
                        time.sleep(0.5)
                        if wait_and_click_step(tc_confirm, MONITOR, "Tái Chế Cuối", timeout=3):
                            unhover_mouse()
                            return True
    return False

def execute_craft_bag_once(lee_shop_img, old_bag_img, confirm_img):
    """Thực hiện 1 lượt Craft Túi cũ. Trả về True nếu kích hoạt thành công."""
    if find_and_click(lee_shop_img, MONITOR, threshold=THRESHOLD):
        print(f"\n[{time.strftime('%H:%M:%S')}] [*] Mở Cửa hàng Lee...")
        time.sleep(0.5)
        if wait_and_click_step(old_bag_img, MONITOR, "Chọn Túi cũ", timeout=3):
            time.sleep(0.3)
            if wait_and_click_step(confirm_img, MONITOR, "Xác nhận Start", timeout=3):
                unhover_mouse()
                return True
    elif find_and_click(old_bag_img, MONITOR, threshold=THRESHOLD):
        print(f"\n[{time.strftime('%H:%M:%S')}] [*] Chọn Túi cũ...")
        time.sleep(0.3)
        if wait_and_click_step(confirm_img, MONITOR, "Xác nhận Start", timeout=3):
            unhover_mouse()
            return True
    return False

def execute_post_craft_sequence(inventory_img, che_tao_bright_img, che_tao_dark_img, material_bright_img, material_dark_img, craft_vattu_img, hide_uncraftable_img, craft_input_box, max_btn_img, confirm_img, map_img, tap_doan_img):
    """Chuỗi sau 4 lần Craft: Túi đồ (Inventory) -> Chế tạo -> Material -> Vật tư y tế (Set 8) -> Bắt đầu -> Bản đồ -> Tập đoàn"""
    print(f"\n[{time.strftime('%H:%M:%S')}] [*] Chạy tiến trình sau 4 lần Craft...")
    if wait_and_click_step(inventory_img, MONITOR, "Túi đồ (Inventory)", timeout=4):
        time.sleep(0.5)
        if ensure_tab_active(che_tao_bright_img, che_tao_dark_img, "Chế tạo", MONITOR):
            time.sleep(0.3)
            if ensure_tab_active(material_bright_img, material_dark_img, "Material", MONITOR):
                time.sleep(0.3)
                if find_and_click(craft_vattu_img, MONITOR, threshold=THRESHOLD):
                    print(f"[{time.strftime('%H:%M:%S')}] [>] Đã chọn: Vật tư y tế (Craft)")
                else:
                    print(f"[{time.strftime('%H:%M:%S')}] [*] Chưa thấy Vật tư y tế, bấm Ẩn công thức không thể chế tạo...")
                    if wait_and_click_step(hide_uncraftable_img, MONITOR, "Ẩn công thức không thể chế tạo", timeout=3):
                        time.sleep(0.4)
                        wait_and_click_step(craft_vattu_img, MONITOR, "Vật tư y tế (Craft)", timeout=3)
                
                time.sleep(0.4)
                # Bước Set 8: Nếu số mặc định không khớp craft_input_box thì bấm nút TỐI ĐA rồi nhập lại 8
                if find_and_click(craft_input_box, MONITOR, threshold=THRESHOLD):
                    print(f"[{time.strftime('%H:%M:%S')}] [>] Đã chọn ô nhập số lượng mặc định, nhập 8...")
                    time.sleep(0.2)
                    pyautogui.hotkey('ctrl', 'a')
                    time.sleep(0.05)
                    pyautogui.press('backspace')
                    pyautogui.write('8')
                    time.sleep(0.3)
                else:
                    print(f"[{time.strftime('%H:%M:%S')}] [*] Số mặc định khác mẫu, bấm nút TỐI ĐA...")
                    clicked_max, max_rect = find_and_click_with_rect(max_btn_img, MONITOR, threshold=THRESHOLD)
                    if clicked_max:
                        print(f"[{time.strftime('%H:%M:%S')}] [>] Đã bấm TỐI ĐA, tiến hành nhập lại 8...")
                        time.sleep(0.25)
                        mx, my, mw, mh = max_rect
                        input_x = max(10, mx - 45 + random.randint(-10, 10))
                        input_y = my + (mh // 2) + random.randint(-mh // 4, mh // 4)
                        
                        move_mouse_bezier(input_x, input_y, duration=random.uniform(0.15, 0.25))
                        time.sleep(random.uniform(0.02, 0.05))
                        pyautogui.mouseDown(_pause=False)
                        pyautogui.moveTo(input_x + random.choice([-1, 1]), input_y + random.choice([-1, 1]), duration=0.02, _pause=False)
                        pyautogui.mouseUp(_pause=False)
                        
                        time.sleep(0.2)
                        pyautogui.hotkey('ctrl', 'a')
                        time.sleep(0.05)
                        pyautogui.press('backspace')
                        pyautogui.write('8')
                        time.sleep(0.3)
                    else:
                        print(f"[{time.strftime('%H:%M:%S')}] [!] Không tìm thấy ô nhập số lẫn nút TỐI ĐA.")

                if wait_and_click_step(confirm_img, MONITOR, "Nút bắt đầu", timeout=3):
                    time.sleep(0.6)
                    if wait_and_click_step(map_img, MONITOR, "Bản đồ", timeout=4):
                        time.sleep(0.8)
                        if not check_exists(tap_doan_img, MONITOR, threshold=THRESHOLD):
                            human_scroll(-800)
                            time.sleep(0.5)
                        wait_and_click_step(tap_doan_img, MONITOR, "Nút Tập đoàn", timeout=4)
                        time.sleep(0.8)
                        print(f"[{time.strftime('%H:%M:%S')}] [V] Hoàn tất chuyển vòng! Tiếp tục chu kỳ Rã mới...\n")

def main():
    global is_paused

    print("="*48)
    print("         TOOL AUTO CYBERCODE ONLINE")
    print("="*48)
    print("1.  Thu Thập AFK")
    print("2.  Triển Khai Bot Nông XP")
    print("3.  Tái Chế Tự Động (1000)")
    print("4.  Mở Khóa Container (Hòm)")
    print("5.  Chạy EGMS (Có lăn chuột)")
    print("6.  AFK EXP Kĩ Thuật In")
    print("7.  AFK EXP Y Học")
    print("8.  AFK EXP Chế Tạo Đạn")
    print("9.  Craft Bag (Cửa hàng Lee -> Túi cũ)")
    print("10. Combo Liên Hoàn: Rã (8) -> Craft (4) -> Túi đồ (Set 8) -> Lặp lại")
    print("0.  Thoát")
    print("-" * 48)
    
    choice = input("Nhập lựa chọn (0-10): ").strip()
    
    # --- TẢI ẢNH CHUNG ---
    claim_img = load_image('claim_btn.png')
    full_img = load_image('inventory_full.png')
    refresh_img = load_image('refresh_btn.png')
    
    last_refresh_time = 0 
    
    # --- BIẾN TRẠNG THÁI CHO CHẾ ĐỘ 10 (COMBO) ---
    combo_stage = "RECYCLE"
    combo_count = 0
    RECYCLE_TARGET = 8
    CRAFT_TARGET = 4
    waiting_for_claim = False
    back_after_claim = False
    post_craft_after_claim = False
    need_enter_tapdoan = True
    
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
    elif choice == '4':
        print("\n" + "-"*30)
        print(" CHỌN LOẠI HÒM CẦN MỞ TỰ ĐỘNG:")
        print(" 1. Hòm Đồ Bị Khóa (Thường)")
        print(" 2. Hòm Đồ Bị Khóa - Hiếm")
        print(" 3. Hòm Đồ Bị Khóa - Huyền Thoại")
        print("-" * 30)
        
        sub_choice = input("Nhập loại hòm (1/2/3): ").strip()
        c_dashboard = load_image('dashboard_btn.png')
        c_menu = load_image('unlock_container_menu.png')
        c_select = load_image('select_chest_btn.png')
        
        if sub_choice == '1':
            c_option = load_image('hom_thuong.png')
            task_name = "Mở Hòm Thường"
        elif sub_choice == '2':
            c_option = load_image('hom_hiem.png')
            task_name = "Mở Hòm Hiếm"
        elif sub_choice == '3':
            c_option = load_image('hom_huyenthoai.png')
            task_name = "Mở Hòm Huyền Thoại"
        else:
            print("[!] Lựa chọn hòm không hợp lệ.")
            exit(1)
            
        c_unlock = load_image('unlock_action_btn.png')
        c_start = load_image('start_btn.png') 
        
    elif choice == '5':
        trigger_img = load_image('trigger_scroll.png')
        egms_img = load_image('egms_btn.png')
        confirm_img = load_image('start_btn.png')
        task_name = "Chạy EGMS"
        
    elif choice == '6':
        task_img = load_image('exp_in.png')
        confirm_img = load_image('start_btn.png')
        task_name = "AFK EXP Kĩ Thuật In"
    elif choice == '7':
        task_img = load_image('exp_yhoc.png')
        confirm_img = load_image('start_btn.png')
        task_name = "AFK EXP Y Học"
    elif choice == '8':
        task_img = load_image('exp_dan.png')
        confirm_img = load_image('start_btn.png')
        task_name = "AFK EXP Chế Tạo Đạn"

    elif choice == '9':
        lee_shop_img = load_image('lee_shop_btn.png')
        old_bag_img = load_image('old_bag_btn.png')
        confirm_img = load_image('start_btn.png')
        task_name = "Craft Bag (Túi cũ)"

    elif choice == '10':
        tap_doan_img = load_image('tap_doan_btn.png')
        tc_auto = load_image('taiche_auto.png')
        tc_plus = load_image('plus_btn.png')
        tc_vattu = load_image('vattu_yte.png')
        tc_input = load_image('input_box_1.png')
        tc_xacnhan = load_image('xac_nhan.png')
        tc_confirm = load_image('taiche_confirm.png')
        
        back_city_img = load_image('back_city_btn.png')
        
        lee_shop_img = load_image('lee_shop_btn.png')
        old_bag_img = load_image('old_bag_btn.png')
        confirm_img = load_image('start_btn.png')

        inventory_img = load_image('inventory_btn.png') if os.path.exists('inventory_btn.png') else load_image('balo_btn.png')
        che_tao_bright_img = load_image('che_tao_bright.png')
        che_tao_dark_img = load_image('che_tao_dark.png')
        material_bright_img = load_image('material_bright.png')
        material_dark_img = load_image('material_dark.png')
        hide_uncraftable_img = load_image('hide_uncraftable_btn.png')
        craft_vattu_img = load_image('vattu_yte_craft.png')
        craft_input_box = load_image('craft_input_box.png')
        max_btn_img = load_image('max_btn.png')
        map_img = load_image('map_btn.png')
        task_name = "Combo Liên Hoàn: Rã (8) -> Craft (4) -> Túi đồ (Set 8) -> Lặp lại"

    elif choice == '0':
        exit(0)
    else:
        exit(1)

    print(f"\n>>> BẮT ĐẦU: {task_name.upper()} <<<")
    print("[-] ÉP GÓC CHUỘT: Dừng khẩn cấp (Tắt tool)")
    print("[-] NHẤN PHÍM F9: Tạm dừng / Tiếp tục chạy\n")
    
    keyboard.add_hotkey('f9', toggle_pause)

    while True:
        try:
            # --- KIỂM TRA TRẠNG THÁI TẠM DỪNG ---
            if is_paused:
                time.sleep(0.5)
                continue
                
            # --- ƯU TIÊN 0: Lấy tất cả (Nhận/Claim) & Kiểm tra rương đầy ---
            if find_and_click(claim_img, MONITOR, threshold=THRESHOLD):
                print(f"[{time.strftime('%H:%M:%S')}] [+] Đã bấm Claim/Nhận thưởng, đang kiểm tra...")
                waiting_for_claim = False
                time.sleep(0.5) 
                
                if check_exists(full_img, MONITOR, threshold=THRESHOLD):
                    print("\n" + "!"*50)
                    print(f"[{time.strftime('%H:%M:%S')}] [!!!] BÁO ĐỘNG: ĐÃ MAX THÀNH PHẨM (RƯƠNG ĐẦY)!")
                    print("[!] Đang tự động ngắt tool để bảo vệ an toàn...")
                    print("!"*50 + "\n")
                    winsound.Beep(1000, 1500) 
                    break 

                # Click nút Trở Lại Trung Tâm sau khi nhận xong lượt Rã thứ 8
                if choice == '10' and back_after_claim:
                    back_after_claim = False
                    time.sleep(0.5)
                    wait_and_click_step(back_city_img, MONITOR, "Trở Lại Trung Tâm", timeout=4)
                    time.sleep(0.8)
                    continue

                # Chạy tiến trình Túi đồ -> Chế tạo -> Material -> Vật tư y tế (Set 8) -> Bắt đầu -> Bản đồ -> Tập đoàn sau khi Claim xong lượt Craft 4/4
                if choice == '10' and post_craft_after_claim:
                    post_craft_after_claim = False
                    time.sleep(0.5)
                    execute_post_craft_sequence(
                        inventory_img, che_tao_bright_img, che_tao_dark_img,
                        material_bright_img, material_dark_img,
                        craft_vattu_img, hide_uncraftable_img, craft_input_box,
                        max_btn_img, confirm_img, map_img, tap_doan_img
                    )
                    continue
                
                time.sleep(0.8) 

            # --- ƯU TIÊN 1: Làm mới thủ công (60s Cooldown) ---
            if time.time() - last_refresh_time > 60:
                if find_and_click(refresh_img, MONITOR, threshold=THRESHOLD):
                    print(f"[{time.strftime('%H:%M:%S')}] [*] Đã bấm Làm mới thủ công (chống kẹt).")
                    last_refresh_time = time.time()
                    time.sleep(0.5)
                    continue 

            # --- XỬ LÝ CHẾ ĐỘ 1, 2, 6, 7, 8 ---
            if choice in ['1', '2', '6', '7', '8']:
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
                execute_recycle_once(tc_auto, tc_plus, tc_vattu, tc_input, tc_xacnhan, tc_confirm)

            # --- XỬ LÝ CHẾ ĐỘ 4 ---
            elif choice == '4':
                if find_and_click(c_dashboard, MONITOR, threshold=THRESHOLD):
                    print(f"\n[{time.strftime('%H:%M:%S')}] [*] Mở Bảng điều khiển...")
                    time.sleep(0.5)
                    if wait_and_click_step(c_menu, MONITOR, "Mở khóa container", timeout=3):
                        time.sleep(0.3)
                        if wait_and_click_step(c_select, MONITOR, "Chọn rương", timeout=3):
                            time.sleep(0.3)
                            if wait_and_click_step(c_option, MONITOR, f"Chọn {task_name}", timeout=3):
                                time.sleep(0.3)
                                if wait_and_click_step(c_unlock, MONITOR, "Mở khóa", timeout=3):
                                    time.sleep(0.3)
                                    if wait_and_click_step(c_start, MONITOR, "Xác nhận Bắt đầu", timeout=3):
                                        print(f"[{time.strftime('%H:%M:%S')}] [V] Đã bấm Bắt đầu! Đang chờ Nhận...")
                                        time.sleep(0.5)

            # --- XỬ LÝ CHẾ ĐỘ 5 (EGMS - CÓ ĐIỂM NEO) ---
            elif choice == '5':
                if check_exists(trigger_img, MONITOR, threshold=THRESHOLD):
                    print(f"[{time.strftime('%H:%M:%S')}] [*] Đã thấy điểm neo! Kích hoạt cuộn chuột...")
                    human_scroll(-800) 
                    time.sleep(0.8) 
                    
                    if find_and_click(egms_img, MONITOR, threshold=THRESHOLD):
                        print(f"[{time.strftime('%H:%M:%S')}] [>] Đã bấm vào EGMS!")
                        time.sleep(0.8)
                        
                        if wait_and_click_step(confirm_img, MONITOR, "Xác nhận Bắt đầu", timeout=3):
                            print(f"[{time.strftime('%H:%M:%S')}] [V] Đã bấm Bắt đầu EGMS! Đang chờ Nhận...")
                            time.sleep(0.5)
                            
                            print(f"[{time.strftime('%H:%M:%S')}] [*] Cuộn chuột trở lại lên trên...")
                            human_scroll(800) 

            # --- XỬ LÝ CHẾ ĐỘ 9 ---
            elif choice == '9':
                if execute_craft_bag_once(lee_shop_img, old_bag_img, confirm_img):
                    print(f"[{time.strftime('%H:%M:%S')}] [V] Đã bấm Start chế tạo Túi cũ! Đang chờ Claim...")
                    time.sleep(0.5)

            # --- XỬ LÝ CHẾ ĐỘ 10 (COMBO LIÊN HOÀN) ---
            elif choice == '10':
                if waiting_for_claim:
                    time.sleep(0.3)
                    continue

                if combo_stage == "RECYCLE":
                    if need_enter_tapdoan:
                        need_enter_tapdoan = False
                        if not check_exists(tc_auto, MONITOR, threshold=THRESHOLD):
                            print(f"\n[{time.strftime('%H:%M:%S')}] [*] Cuộn chuột 1 lần tìm nút Tập đoàn...")
                            human_scroll(-800)
                            time.sleep(0.6)
                            wait_and_click_step(tap_doan_img, MONITOR, "Nút Tập đoàn", timeout=3)
                            time.sleep(0.8)

                    if execute_recycle_once(tc_auto, tc_plus, tc_vattu, tc_input, tc_xacnhan, tc_confirm):
                        combo_count += 1
                        waiting_for_claim = True
                        print(f"[{time.strftime('%H:%M:%S')}] [V] Tiến độ Rã: {combo_count}/{RECYCLE_TARGET}")
                        
                        if combo_count >= RECYCLE_TARGET:
                            combo_stage = "CRAFT"
                            combo_count = 0
                            back_after_claim = True
                            print(f"[{time.strftime('%H:%M:%S')}] [>>>] Đã đủ {RECYCLE_TARGET} lần Rã! Sẽ bấm Quay lại sau khi Claim để sang Craft Balo...")
                        time.sleep(0.5)

                elif combo_stage == "CRAFT":
                    if execute_craft_bag_once(lee_shop_img, old_bag_img, confirm_img):
                        combo_count += 1
                        waiting_for_claim = True
                        print(f"[{time.strftime('%H:%M:%S')}] [V] Tiến độ Craft Balo: {combo_count}/{CRAFT_TARGET}")
                        
                        if combo_count >= CRAFT_TARGET:
                            combo_stage = "RECYCLE"
                            combo_count = 0
                            post_craft_after_claim = True
                            print(f"[{time.strftime('%H:%M:%S')}] [>>>] Đã kích hoạt đủ {CRAFT_TARGET} lần Craft Balo! Sẽ mở Túi đồ (Inventory) chế Vật tư y tế sau khi Claim...")
                        time.sleep(0.5)
            
            time.sleep(0.3)
            
        except pyautogui.FailSafeException:
            print(f"\n[{time.strftime('%H:%M:%S')}] [!] Đã ngắt Tool bằng chuột (Failsafe)!")
            break

if __name__ == "__main__":
    main()