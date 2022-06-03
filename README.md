#### 确认是否是neox引擎
[解包](https://github.com/ZhangFengze/AndroidGameHackTutorial)
看是否有大量NeoX相关

#### 确认CPython版本
NeoX魔改了CPython，确认NeoX的CPython版本，以便参考源码。  
CPython有很多调试字符串，里面记录了源文件路径，我们可以借此得到python主次版本号。  
IDA Pro打开核心so库，开Strings窗口，搜python    
![image](https://user-images.githubusercontent.com/21135715/171880588-df7fbaec-d307-443d-925f-c8458eac20d5.png)  

CPython定义了PY_VERSION字符串，格式是MAJOR.MINOR.PATCH，我们再次搜索2.7.  
![image](https://user-images.githubusercontent.com/21135715/171880752-0c2db9c7-5b09-439a-b60b-d40bc072a415.png)  
可得到完整版本号为2.7.3


参考  
[neox-tools](https://github.com/xforce/neox-tools)  
[NeteaseUnpackTools](https://github.com/yuanbi/NeteaseUnpackTools)  
[unnpk](https://github.com/YJBeetle/unnpk)

基础流程没有变  
不过pyc混淆不止重映射opcode了，还加入了新的opcode  
需要根据含义将新引入的opcode改成常规opcode  
