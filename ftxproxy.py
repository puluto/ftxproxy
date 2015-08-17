#!/usr/bin/python
# -*- coding: utf-8 -*-

import socket
import select
import time
import sys

buffer_size = 4096
delay = 0.0001


class Forward:
    """连接需要转发的服务器地址
       返回连接后的socket对象
    """

    def __init__(self):
        self.forward = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start(self, host, port):
        try:
            self.forward.connect((host, port))
            # 根据代理目标地址，判断并发送TGW包
            if 'twsapp.com' in host:
                tgw = 'tgw_l7_forward\r\nHost:{0}:{1}\r\n\r\n'.format(host,
                                                                      port)
                self.forward.sendall(tgw)
            return self.forward
        except Exception, ex:
            print ex
            return False


class TheServer:
    input_list = []
    channel = {}

    def __init__(self, local, remote, trust):
        self.local = local
        self.remote = remote
        self.trust = trust
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 设定可以TIME_WAIT连接复用,只对服务端有效
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind(('', int(self.local[1])))
        self.server.listen(200)

    def main_loop(self):
        # 服务器对象加入input_list列表
        self.input_list.append(self.server)

        while 1:
            time.sleep(delay)
            ss = select.select
            inputready, outputready, exceptready = ss(self.input_list, [], [])
            """select模块会检测活动的链接并返回到inputready,由操作系统底层控制
            当客户端发起新的连接时self.server才会产生数据，正常传输时只会
            触发连接代理服务器的对象和已经连接的客户端对象
            """
            for self.s in inputready:
                if self.s == self.server:
                    self.on_accept()
                    break

                self.data = self.s.recv(buffer_size)
                if len(self.data) == 0:
                    self.on_close()
                    break
                else:
                    self.on_recv()

    def on_accept(self):
        forward = Forward().start(self.remote[1], int(self.remote[2]))
        clientsock, clientaddr = self.server.accept()
        # 判断客户端是否为可信
        if self.trust and clientaddr[0] != self.trust:
            print clientaddr, 'not is trust addr !'
            clientsock.close()
        elif forward:
            print clientaddr, "has connected"
            self.input_list.append(clientsock)
            self.input_list.append(forward)
            self.channel[clientsock] = forward
            self.channel[forward] = clientsock
        else:
            print "Can't establish connection with remote server.",
            print "Closing connection with client side", clientaddr
            clientsock.close()

    def on_close(self):
        print self.s.getpeername(), "has disconnected"
        # 断开连接后移除server监听对象,以及远程服务器连接对象
        self.input_list.remove(self.s)
        self.input_list.remove(self.channel[self.s])
        out = self.channel[self.s]
        # 关闭用户端连接，等同于self.s.close()
        self.channel[out].close()
        # 关闭服务器端连接
        self.channel[self.s].close()
        # 清除通道对象
        del self.channel[out]
        del self.channel[self.s]

    def on_recv(self):
        data = self.data
        # 截获修改数据忽略TGW包
        if 'tgw_l7_forward' == data[0:14]:
            print data
            return 1
        self.channel[self.s].send(data)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print 'command l:local_port r:remote_server:remote_port [t:ip]'
        sys.exit(2)
    elif len(sys.argv) == 4:
        trust_ip = sys.argv[3].split(':')[1]
    else:
        trust_ip = 0
    local_options = sys.argv[1].split(':')[0] == 'l' and sys.argv[1].split(':') or None
    remote_options = sys.argv[2].split(':')[0] == 'r' and sys.argv[2].split(':') or None

    if local_options and remote_options:
        server = TheServer(local_options, remote_options, trust_ip)
    else:
        print 'command l:local_port r:remote_server:remote_port [t:ip]'
        sys.exit(1)
    try:
        server.main_loop()
    except KeyboardInterrupt:
        print "Ctrl C - Stopping server"
        sys.exit(1)
