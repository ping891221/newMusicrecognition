import threading
import time
from queue import Queue
import concurrent.futures
from record_audio_test import record_audio_test
from match_songs1 import match_songs1
from match_songs2 import match_songs2
from match_songs3 import match_songs3
from match_songs4 import match_songs4
from match_songs5 import match_songs5
from match_songs6 import match_songs6
from match_songs7 import match_songs7
from match_songs8 import match_songs8
import queue
import time
import serial
# 创建一个队列用于存储音频数据
data_queue = Queue()

# 创建一个 ThreadPoolExecutor，指定线程数量
executor1 = concurrent.futures.ThreadPoolExecutor(max_workers=8)
executor2 = concurrent.futures.ThreadPoolExecutor(max_workers=8)

#bluetooth
ser = serial.Serial(
    port='/dev/rfcomm0',
    baudrate=38400,
    parity=serial.PARITY_ODD,
    stopbits=serial.STOPBITS_TWO,
    bytesize=serial.SEVENBITS
)

# 定义 recognition 函数
def recognition1(match_songs_func):
    try:
        #print('hiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii')
        data = data_queue.get()
        print("Currently executing:", match_songs_func.__name__)
        songname = match_songs_func(data)
        print(songname," ",songname," ",songname)
        return songname or 'no', match_songs_func.__name__
    except queue.Empty:
        return 'no', match_songs_func.__name__
    except Exception as e:
        print(f"An exception occurred: {e}")
        
def recognition2(match_songs_func):
    try:
        #print('hiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii')
        data = data_queue.get()
        print("Currently executing:", match_songs_func.__name__)
        songname = match_songs_func(data)
        return songname or 'no', match_songs_func.__name__
    except queue.Empty:
        return 'no', match_songs_func.__name__
    except Exception as e:
        print(f"An exception occurred: {e}")

# 生成音频数据的线程函数
def generate_audio_data():
    while True:
        d = record_audio_test()
        data_queue.put(d)  # 将新数据放入队列

# 处理音频数据的线程函数
def process_audio_data1():
    while True:
        #data = data_queue.get()  # 从队列中获取新数据

        # 提交任务，每个任务使用不同的 match_songs 函数
        futures = [
            executor1.submit(recognition1, match_songs1),
            executor1.submit(recognition1, match_songs2),
            executor1.submit(recognition1, match_songs3),
            executor1.submit(recognition1, match_songs4)
        ]

        # 获取任务的结果
        for future in concurrent.futures.as_completed(futures):
            #data = data_queue.get()
            result, name = future.result()
            #if result=='':
            print("\033[1;33;44m" + name + ":" + result + "\033[0m")
            if result == 'police.mp3':
                ser.write(str(1).encode())
            elif result =='ambulance.mp3':
                ser.write(str(2).encode())
            elif result == 'car-horn-sound.mp3':
                ser.write(str(3).encode())
            elif result == 'fire(Yu).mp3':
                ser.write(str(4).encode())
            elif result == 'twTruck.mp3':
                ser.write(str(5).encode())
            else:
                print('why?') 
# 处理音频数据的线程函数
def process_audio_data2():
    
    while True:
        #data = data_queue.get()  # 从队列中获取新数据

        # 提交任务，每个任务使用不同的 match_songs 函数
        futures = [
            executor2.submit(recognition2, match_songs5),
            executor2.submit(recognition2, match_songs6),
            executor2.submit(recognition2, match_songs7),
            executor2.submit(recognition2, match_songs8)
        ]

        # 获取任务的结果
        for future in concurrent.futures.as_completed(futures):
            #data = data_queue.get()
            result, name = future.result()
            print("\033[1;33;44m" + name + ":" + result + "\033[0m")
# 启动两个线程，一个用于生成音频数据，另一个用于处理音频数据
audio_data_thread = threading.Thread(target=generate_audio_data)
audio_data_thread.start()

audio_processing_thread1 = threading.Thread(target=process_audio_data1)
audio_processing_thread1.start()

audio_processing_thread2 = threading.Thread(target=process_audio_data2)
audio_processing_thread2.start()
# 主线程等待两个子线程结束
audio_data_thread.join()
audio_processing_thread.join()

