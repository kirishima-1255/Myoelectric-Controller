import serial
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import time
from datetime import datetime
import os

# シリアルポートとボーレートを設定（使用しているArduinoに合わせて変更）
ser = serial.Serial('COM3', 9600, timeout=1)  # Windowsの場合
# ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)  # Linuxの場合

plt.ion()  # インタラクティブモードの開始

# データ保存リストとタイムスタンプ
data = []
batch_data = []  # 一時的に3セット分のデータを保持
timestamps = []  # タイムスタンプ用リスト

# プロット設定
fig, ax = plt.subplots()
line, = ax.plot(data)
ax.set_ylim(0, 1023)  # Arduinoのアナログ入力は10ビット（0〜1023）

# ログファイルの保存先
log_dir = './log/'
os.makedirs(log_dir, exist_ok=True)  # ディレクトリを作成

start_time = time.time()  # プログラム開始時刻

try:
    while True:
        if ser.in_waiting > 0:
            line_data = ser.readline().decode().strip()  # シリアルデータを1行読み込む
            try:
                # 受信したデータをカンマで分割してリストに変換
                sensor_values = [int(x) for x in line_data.split(',')]
                
                # 受信した5回分のデータを一時リストに追加
                batch_data.extend(sensor_values)
                timestamps.extend([datetime.now()] * len(sensor_values))  # タイムスタンプを追加
                
                # 3セット分（15回分）のデータが揃ったらグラフを更新
                if len(batch_data) >= 15:
                    data.extend(batch_data)  # 3セット分のデータを追加
                    batch_data = []  # 一時リストをリセット

                    # 最新の100データのみ保持
                    if len(data) > 100:
                        data = data[-100:]

                    # グラフの更新
                    line.set_ydata(data)
                    line.set_xdata(np.arange(len(data)))

                    # 赤いインパルスの表示
                    if len(data) % 15 == 0:  # 3セットごとにインパルスを表示
                        ax.axvline(x=len(data) - 1, color='red', linestyle='--', linewidth=1)

                    ax.relim()
                    ax.autoscale_view(True, True, True)

                    plt.draw()
                    plt.pause(0.1)

                    # 5秒ごとにCSVファイルに保存
                    if int(time.time() - start_time) % 5 == 0:
                        filename = datetime.now().strftime("%m%d-%H%M%S") + ".csv"
                        filepath = os.path.join(log_dir, filename)

                        # データフレームを作成し、CSVに保存
                        df = pd.DataFrame({'Timestamp': timestamps[:len(data)], 'Value': data})
                        df.to_csv(filepath, index=False)

                        # 最初の15個のデータとそのタイムスタンプを削除
                        data = data[15:]
                        timestamps = timestamps[15:]

            except ValueError:
                # 読み込んだデータが数値に変換できない場合の処理
                pass
            
        # 20秒経過後にプログラムを終了
        if time.time() - start_time >= 20:
            break

except KeyboardInterrupt:
    # Ctrl+Cでプログラムを終了するときの処理
    ser.close()  # シリアルポートを閉じる
    plt.ioff()   # インタラクティブモードをオフ
    plt.show()

# プログラム終了時の処理
ser.close()  # シリアルポートを閉じる
plt.ioff()   # インタラクティブモードをオフ
plt.show()
