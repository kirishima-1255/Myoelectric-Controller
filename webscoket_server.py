
import json
import time

import tornado.websocket
import tornado.web
import tornado.ioloop

import reading_temperature # 先ほど作成した温度読み取りプログラム

class SendWebSocket(tornado.websocket.WebSocketHandler):
  def open(self):
    print('Session Opened. IP:' + self.request.remote_ip)
    self.ioloop = tornado.ioloop.IOLoop.instance()
    self.send_websocket()

  def on_close(self):
    print("Session Closed")

  def check_origin(self, origin):
    return True

  def send_websocket(self):
    self.ioloop.add_timeout(time.time() + 0.1, self.send_websocket)
    if self.ws_connection:
      message = json.dumps({
        'data': reading_temperature(), # ここでarduinoで読み取った温度をwebsocketで送っている。
      })
      self.write_message(message)
app = tornado.web.Application([(r"/ws/display", SendWebSocket)])

if __name__ == "__main__":
  app.listen(8080)
  tornado.ioloop.IOLoop.current().start()