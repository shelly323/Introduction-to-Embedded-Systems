import cv2
import numpy as np
import time
from socket_client import SocketClient
import tensorflow.lite as tflite

PC_IP = '192.168.0.245'
PORT = 65432
MODEL_PATH = "model_unquant.tflite"
LABEL_PATH = "labels.txt"

communicator = SocketClient(PC_IP, PORT)
communicator.connect()

interpreter = tflite.Interpreter(model_path=MODEL_PATH)
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

h = input_details[0]['shape'][1]
w = input_details[0]['shape'][2]

with open(LABEL_PATH, 'r') as f:
    labels = [line.strip() for line in f.readlines()]

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

# --- 初始化變數 ---
frame_count = 0
detect_every_n = 5
current_label = "Waiting..."
current_confidence = 0.0

print("開始執行！按 'q' 離開")

try:
    while True:
        ret, frame = cap.read()
        if not ret: break
        frame_count += 1
        if frame_count % detect_every_n == 0:
            # === 影像前處理 ===
            img_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            img_resized = cv2.resize(img_gray, (w, h))
            input_data = (np.float32(img_resized) / 127.5) - 1.0
            input_data = np.expand_dims(input_data, axis=-1)
            input_data = np.expand_dims(input_data, axis=0)
            # 5. 推論
            interpreter.set_tensor(input_details[0]['index'], input_data)
            interpreter.invoke()
            output_data = interpreter.get_tensor(output_details[0]['index'])
            # 6. 更新結果
            results = np.squeeze(output_data)
            top_index = np.argmax(results)
            current_confidence = results[top_index]
            current_label = labels[top_index] 
            # 7. 判斷與傳輸邏輯
            # 如果信心度夠高，就傳送結果給電腦
            if current_confidence > 0.8:
                print(f"偵測到: {current_label} ({current_confidence:.2f})")
                communicator.send_detection(current_label)

        # --- 繪圖區 ---
        # 顯示畫面
        text_color = (0, 255, 0) if current_confidence > 0.8 else (0, 0, 255)
        info = f"{current_label}: {current_confidence:.2f}"
        cv2.putText(frame, info, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, text_color, 2)
        
        cv2.imshow('Pi Camera', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    # 確保程式結束時關閉連線和相機
    cap.release()
    communicator.close()
    cv2.destroyAllWindows()