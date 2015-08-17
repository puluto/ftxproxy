## FTXProxy
不到100行代码实现代理服务，并穿透腾讯TGW进行tcp代理，项目借用国外大神代码 http://voorloopnul.com/blog/a-python-proxy-in-less-than-100-lines-of-code/

### 使用方式
    # l:绑定本地端口
    # r:绑定远端代理IP:端口
    # t:信任IP[可选]，设定本参数后(仅支持单一IP)，只有此IP可以连接l绑定的端口
    ./ftxproxy l:local_port r:remote_ip:remote_port [t:trust_ip]
### 注意事项
* 当远端出错或者拒绝连接时程序会退出，可以使用supervisor管理进程
* 每个进程只支持绑定一个代理端口
* 本脚本没有进行大规模并发测试，请勿用于关键系统

### 联系方式
Email: puluto#gmail.com

QQ: 34201567

欢迎提出建议以及pull request.
