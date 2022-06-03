#### 确认是否是neox引擎
[解包](https://github.com/ZhangFengze/AndroidGameHackTutorial)
看是否有大量NeoX相关

#### 确认CPython版本
NeoX魔改了CPython，确认NeoX的CPython版本，以便参考源码。
IDA Pro打开核心so库，开Strings窗口，搜python，大概率能看到带python源码的调试输出字符串，例如  
![image](https://user-images.githubusercontent.com/21135715/171878141-a7e6755e-ef7f-4ff4-8bc5-cc5c60e129fa.png)
即可确认主次版本号


参考  
[neox-tools](https://github.com/xforce/neox-tools)  
[NeteaseUnpackTools](https://github.com/yuanbi/NeteaseUnpackTools)  
[unnpk](https://github.com/YJBeetle/unnpk)

基础流程没有变  
不过pyc混淆不止重映射opcode了，还加入了新的opcode  
需要根据含义将新引入的opcode改成常规opcode  
