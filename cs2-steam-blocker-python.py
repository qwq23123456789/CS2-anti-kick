import os
import sys
import json
import subprocess
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime
import ctypes
import winsound
from PIL import Image, ImageDraw
try:
    import keyboard
    import pystray
except ImportError as e:
    print(f"錯誤: 缺少套件 - {e}")
    print("請執行: pip install keyboard pystray pillow pywin32")
    sys.exit(1)

class CS2SteamBlocker:
    def __init__(self):
        self.is_in_match = False
        self.steam_blocked = False
        self.auto_block = True
        self.last_phase = ""
        self.tray_icon = None
        self.is_running = True
        self.steam_paths = [
            r"C:\Program Files (x86)\Steam\steam.exe",
            r"C:\Program Files\Steam\steam.exe",
            os.path.expanduser(r"~\Steam\steam.exe")
        ]
        self.gsi_config_name = "gamestate_integration_cs2steamblock.cfg"
        self.firewall_rule_out = "CS2_Block_Steam_Out"
        self.firewall_rule_in = "CS2_Block_Steam_In"
        self.log("=" * 60)
        self.log("CS2 Steam Blocker v3.4 - 修復版")
        self.log("=" * 60)
        self.check_admin()

    def check_admin(self):
        try:
            if not ctypes.windll.shell32.IsUserAnAdmin():
                self.log("⚠️  需要管理員權限!")
                self.show_notification("錯誤", "請以管理員身分執行")
        except:
            self.log("無法檢查權限")

    def log(self, message):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")

    def play_sound(self, sound_type):
        sounds = {
            "block": (1000, 150),
            "unblock": (500, 150),
            "match_start": (800, 120),
            "match_end": (600, 120),
            "toggle": (700, 80),
            "error": (300, 400)
        }
        try:
            freq, duration = sounds.get(sound_type, (800, 150))
            winsound.Beep(freq, duration)
        except:
            pass

    def show_notification(self, title, message):
        if self.tray_icon:
            try:
                self.tray_icon.notify(message, title)
            except:
                pass

    def find_steam_path(self):
        for path in self.steam_paths:
            if os.path.exists(path):
                return path
        return None

    def check_firewall_rule(self):
        try:
            result = subprocess.run(
                f'netsh advfirewall firewall show rule name="{self.firewall_rule_out}"',
                shell=True, capture_output=True, text=True, timeout=5
            )
            return self.firewall_rule_out in result.stdout
        except:
            return False

    def block_steam(self):
        if self.steam_blocked:
            self.log("ℹ️  Steam 已阻止")
            return
        steam_path = self.find_steam_path()
        if not steam_path:
            self.log("❌ 找不到 Steam")
            self.play_sound("error")
            return
        try:
            self.log(f"🔒 阻止 Steam UDP 3478-3480: {steam_path}")
            subprocess.run(
                f'netsh advfirewall firewall delete rule name="{self.firewall_rule_out}"',
                shell=True, capture_output=True, timeout=5
            )
            subprocess.run(
                f'netsh advfirewall firewall delete rule name="{self.firewall_rule_in}"',
                shell=True, capture_output=True, timeout=5
            )
            cmd_out = (
                f'netsh advfirewall firewall add rule name="{self.firewall_rule_out}" '
                f'dir=out program="{steam_path}" protocol=UDP '
                f'localport=3478-3480 remoteport=3478-3480 action=block'
            )
            cmd_in = (
                f'netsh advfirewall firewall add rule name="{self.firewall_rule_in}" '
                f'dir=in program="{steam_path}" protocol=UDP '
                f'localport=3478-3480 remoteport=3478-3480 action=block'
            )
            result_out = subprocess.run(cmd_out, shell=True, capture_output=True, text=True, timeout=10)
            result_in = subprocess.run(cmd_in, shell=True, capture_output=True, text=True, timeout=10)
            if result_out.returncode == 0 and result_in.returncode == 0 and self.check_firewall_rule():
                self.log("✅ Steam UDP 已阻止")
                self.steam_blocked = True
                self.play_sound("block")
                self.show_notification("Steam 已阻止", "UDP 3478-3480 已阻止")
                self.update_tray_menu()
            else:
                self.log("❌ 規則添加失敗")
                self.play_sound("error")
        except Exception as e:
            self.log(f"❌ 阻止失敗: {e}")
            self.play_sound("error")

    def unblock_steam(self):
        if not self.steam_blocked:
            self.log("ℹ️  Steam 已正常")
            return
        try:
            self.log("🔓 恢復 Steam...")
            subprocess.run(
                f'netsh advfirewall firewall delete rule name="{self.firewall_rule_out}"',
                shell=True, capture_output=True, timeout=5
            )
            subprocess.run(
                f'netsh advfirewall firewall delete rule name="{self.firewall_rule_in}"',
                shell=True, capture_output=True, timeout=5
            )
            self.log("✅ Steam 連線恢復")
            self.steam_blocked = False
            self.play_sound("unblock")
            self.show_notification("Steam 恢復", "網路連線正常")
            self.update_tray_menu()
        except Exception as e:
            self.log(f"❌ 恢復失敗: {e}")
            self.play_sound("error")

    def toggle_auto(self):
        self.auto_block = not self.auto_block
        status = "開啟" if self.auto_block else "關閉"
        self.log(f"⚙️  自動阻止: {status}")
        self.play_sound("toggle")
        self.show_notification("自動模式", f"自動阻止已{status}")
        self.update_tray_menu()

    def process_game_state(self, data):
        try:
            if 'map' not in data:
                return
            map_data = data['map']
            phase = map_data.get('phase', '')
            if phase != self.last_phase:
                self.log(f"🗺️  地圖: {map_data.get('name', 'unknown')} | 階段: {phase}")
                self.last_phase = phase
            in_match = phase in ['live', 'warmup']
            if in_match and not self.is_in_match:
                self.is_in_match = True
                self.play_sound("match_start")
                self.show_notification("進入比賽", "遊戲開始")
                if self.auto_block:
                    self.block_steam()
            elif not in_match and self.is_in_match:
                self.is_in_match = False
                self.play_sound("match_end")
                self.show_notification("離開比賽", "已回到大廳")
                if self.steam_blocked:
                    self.unblock_steam()
        except Exception as e:
            self.log(f"❌ 處理遊戲狀態錯誤: {e}")

    def create_gsi_config(self):
        config_content = '''"CS2 Steam Blocker GSI"
{
  "uri" "http://127.0.0.1:3000"
  "timeout" "5.0"
  "buffer" "0.1"
  "throttle" "0.5"
  "heartbeat" "30.0"
  "data"
  {
    "provider" "1"
    "map" "1"
    "round" "1"
    "player_state" "1"
  }
}'''
        possible_paths = [
            r"C:\Program Files (x86)\Steam\steamapps\common\Counter-Strike Global Offensive\game\csgo\cfg",
            r"C:\Program Files\Steam\steamapps\common\Counter-Strike Global Offensive\game\csgo\cfg",
            os.path.expanduser(r"~\Steam\steamapps\common\Counter-Strike Global Offensive\game\csgo\cfg")
        ]
        for path in possible_paths:
            if os.path.exists(path):
                try:
                    config_path = os.path.join(path, self.gsi_config_name)
                    with open(config_path, 'w', encoding='utf-8') as f:
                        f.write(config_content)
                    self.log(f"✅ GSI 配置檔: {config_path}")
                    return True
                except:
                    pass
        try:
            with open(self.gsi_config_name, 'w', encoding='utf-8') as f:
                f.write(config_content)
            self.log(f"⚠️  GSI 配置檔創建在當前目錄，請複製到 CS2 cfg")
            return False
        except:
            self.log("❌ 創建 GSI 配置檔失敗")
            return False

    def test_hotkey(self, key_name):
        self.log(f"🔔 快捷鍵 {key_name}")
        self.play_sound("toggle")
        self.show_notification("快捷鍵測試", f"{key_name} 正常")

    def setup_hotkeys(self):
        try:
            keyboard.add_hotkey('96', lambda: self.test_hotkey("Num 0"))
            keyboard.add_hotkey('97', self.block_steam)
            keyboard.add_hotkey('98', self.unblock_steam)
            keyboard.add_hotkey('99', self.toggle_auto)
            self.log("✅ 全域快捷鍵已註冊 (僅小鍵盤 0-3)")
            self.show_notification("快捷鍵就緒", "按小鍵盤 0 測試")
        except:
            self.log("❌ 快捷鍵註冊失敗，需管理員權限")

    def create_tray_icon_image(self, color='#00ff00'):
        image = Image.new('RGB', (64, 64), color)
        draw = ImageDraw.Draw(image)
        draw.rectangle([16, 20, 48, 44], fill='white')
        return image

    def create_tray_menu(self):
        def get_status_text(item):
            game = "⚡ 比賽中" if self.is_in_match else "📋 大廳"
            steam = "🚫 已阻止" if self.steam_blocked else "✓ 正常"
            auto = "✓ 開啟" if self.auto_block else "✗ 關閉"
            return f"遊戲: {game} | Steam: {steam} | 自動: {auto}"
        menu = pystray.Menu(
            pystray.MenuItem(get_status_text, lambda item: None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("🔧 測試功能", pystray.Menu(
                pystray.MenuItem("測試快捷鍵", lambda item: self.test_hotkey("托盤選單")),
                pystray.MenuItem("檢查防火牆", self.verify_firewall),
            )),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("手動阻止 Steam", self.block_steam),
            pystray.MenuItem("手動恢復 Steam", self.unblock_steam),
            pystray.MenuItem("切換自動阻止", self.toggle_auto),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("重新創建 GSI", self.create_gsi_config),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("退出程式", self.quit_app)
        )
        return menu

    def update_tray_menu(self):
        if self.tray_icon:
            self.tray_icon.menu = self.create_tray_menu()
            color = '#ff0000' if self.steam_blocked else '#ff9900' if self.is_in_match else '#00ff00'
            self.tray_icon.icon = self.create_tray_icon_image(color)

    def verify_firewall(self, item=None):
        if self.check_firewall_rule():
            self.log("✅ 防火牆規則有效")
            self.show_notification("規則驗證", "防火牆正常")
            self.play_sound("toggle")
        else:
            self.log("❌ 無防火牆規則")
            self.show_notification("規則驗證", "未檢測到規則")
            self.play_sound("error")

    def create_tray(self):
        icon_image = self.create_tray_icon_image()
        self.tray_icon = pystray.Icon(
            "cs2_steam_blocker",
            icon_image,
            "CS2 Steam Blocker",
            menu=self.create_tray_menu()
        )
        return self.tray_icon

    def quit_app(self, item=None):
        self.log("正在退出...")
        self.is_running = False
        if self.steam_blocked:
            self.unblock_steam()
        if self.tray_icon:
            self.tray_icon.stop()
        os._exit(0)

class GSIHandler(BaseHTTPRequestHandler):
    blocker = None
    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            if self.blocker:
                self.blocker.process_game_state(data)
        except:
            pass
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
    def log_message(self, format, *args):
        pass

def start_gsi_server(blocker):
    GSIHandler.blocker = blocker
    try:
        server = HTTPServer(('127.0.0.1', 3000), GSIHandler)
        blocker.log("✅ GSI 伺服器啟動 (127.0.0.1:3000)")
        server.serve_forever()
    except:
        blocker.log("❌ 伺服器啟動失敗，端口 3000 可能被占")

def print_startup_info():
    print("=" * 60)
    print("程式已在背景運行!")
    print("快捷鍵 (僅小鍵盤):")
    print("  小鍵盤 0 - 🔔 測試快捷鍵")
    print("  小鍵盤 1 - 🚫 手動阻止 Steam")
    print("  小鍵盤 2 - ✅ 手動恢復 Steam")
    print("  小鍵盤 3 - ⚙️  切換自動阻止")
    print("托盤圖示: 🟢 正常 | 🟠 比賽中 | 🔴 Steam 阻止")
    print("💡 先按小鍵盤 0 測試快捷鍵")
    print("=" * 60)

def main():
    blocker = CS2SteamBlocker()
    blocker.create_gsi_config()
    blocker.setup_hotkeys()
    server_thread = threading.Thread(target=start_gsi_server, args=(blocker,), daemon=True)
    server_thread.start()
    time.sleep(1)
    print_startup_info()
    blocker.create_tray().run()

if __name__ == "__main__":
    main()
