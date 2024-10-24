import serial # serial通信のライブラリ
import time
import re # 正規表現のライブラリ

def read_temperature() -> float:
  ser = serial.Serial("COM3", 57600)
  pattern = '\d'
  result = ser.readline().decode()
  matched = re.findall(pattern, result)
  if len(matched) > 0:
    temperature = matched[0]
  else:
    temperature = 0

  return float(temperature)