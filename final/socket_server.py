import socket
import pyautogui
import time
from plyer import notification 

HOST = '0.0.0.0'
PORT = 65432
BUFFER_SIZE = 1024
COOLDOWN_SECONDS = 10  
label = ["boss", "maneger", "non-people"]

def show_notification(who):
    notification.notify(
        title='偵測警報',
        message=f'{who}經過',
        app_name='Pi 監視器',
        timeout=0.5 
    )

def switch_screen_action():
    print("switch on")
    pyautogui.hotkey('alt', 'tab')

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(1) 

    boss_is_not_here = True
    show = True
    current_message = ''
    last_switch_time = 0
    last_message = ''
    
    print(f"waiting server... IP: {socket.gethostbyname(socket.gethostname())}, Port: {PORT}")

    while True:
        conn, addr = server.accept()
        print(f"connect: {addr}")
            
        with conn:
            while True:
                data = conn.recv(BUFFER_SIZE)
                if not data:
                    print("disconnect, please wait")
                    break
            
                message = data.decode('utf-8').lower() 
                person_name = ''
                for keyword in label:
                    if keyword in message:
                        person_name = keyword.upper()
                    else:
                        continue

                print(f"收到訊號: {person_name}")
                if person_name != current_message :
                    show = True
                    last_message = current_message
                    current_message = person_name
                else:
                    show = False

                if "BOSS" in current_message:
                    if boss_is_not_here:
                        boss_is_not_here = False
                        current_time = time.time()
                        if current_time - last_switch_time > COOLDOWN_SECONDS:
                            if show :
                                show_notification(current_message)
                            switch_screen_action()
                            last_switch_time = current_time
                        else:
                            print(f"剩餘 {int(COOLDOWN_SECONDS - (current_time - last_switch_time))} 秒")
                elif "NON-PEOPLE" in current_message:
                    boss_is_not_here = True
                    if show and last_message != '':
                        notification.notify(
                        title='偵測警報',
                        message=f'{last_message}已離開',
                        app_name='Pi 監視器',
                        timeout = 1 
                        )
                else:
                    boss_is_not_here = True
                    if show:
                        show_notification(current_message)  
                            
if __name__ == "__main__":
    start_server()