# NeoXResearch
  
网易NeoX引擎npk格式研究

## 参考
[neox-tools](https://github.com/xforce/neox-tools)  
[NeteaseUnpackTools](https://github.com/yuanbi/NeteaseUnpackTools)  
[unnpk](https://github.com/YJBeetle/unnpk)  
[pymarshal.py](https://gist.github.com/fate0/3e1d23bce9d4d2cfa93848dd92aba3d4)  
fate0的博客 *阴阳师：一个非酋的逆向旅程*  (自行搜索)
  
## 逆向思路
网上已有一些前人工作可供参考，但更新大多停留在几年前（2017~2019年）左右，已经失效了，不能直接拿来用  

主要有以下变化：
* 之前so会导出一些CPython函数，现在不再导出
* 之前pyc混淆只调换了opcode的定义，现在增加了新opcode
* 部分函数从纯python实现改成了native注册给python实现

这里仅介绍关键部分 与 基础流程需要修改的部分  

基础流程见参考链接  

#### 找出CPython关键函数
NeoX内置了CPython，并魔改了一部分源码，我们需要找到关键函数比如Py_Initialize以便分析  

##### 确认CPython版本
首先确认NeoX使用的CPython版本，以便参考源码  

CPython有很多调试字符串，里面记录了源文件路径，我们可以借此得到python主次版本号  

IDA Pro打开核心so库，开Strings窗口，搜python  

可以搜到类似 engine/NeoX/src/3d-engine/branches/mobile/engine/python27/Objects/classobject.c 的字符串，即可确认主次版本号为2.7  

CPython定义了PY_VERSION字符串，格式是MAJOR.MINOR.PATCH，我们再次搜索2.7.  

可以搜到2.7.3，即可确认完整版本号  

#### 对照CPython源码分析
拿到版本号后，去CPython官方仓库取对应源码  

例如我们要找Py_Initialize函数，可以看到源码中有很多字符串，例如 Py_Initialize: can't make first interpreter  

编译器会优化代码等，但是不做特殊处理的话，字符串一般是不会改的  

我们继续IDA Pro的Strings窗口中直接搜索  

搜到了以后找对该字符串的引用，发现只有一个是函数，点进去看，基本和源码长得差不多，即可确认找到了目标函数  

找到一个函数后，即可根据调用关系进一步找到更多相关函数  

这里推荐多找一些CPython函数，这样之后分析其他用到了CPython函数的代码时比较容易分析  

#### 找加载脚本流程
由前人工作可知，redirect.nxs负责解密脚本  

尝试直接搜索redirect字符串，可以找到硬编码处理redirect.nxs的函数  

由于之前已经分析好了CPython函数，可以看出该函数读取了redirect.nxs文件，调用PyMarshal_ReadObjectFromString得到PyObject，再调用PyImport_ExecCodeModule，执行并引入了redirect模块   

所以redirect.nxs是一个序列化好了的python module，翻python源码可知这相当于去掉了文件头的pyc文件  

动态调试将redirect.nxs dump出来，加上文件头，使用uncompyle6反编译  

不出意外的失败了，因为做了混淆  

暂且不处理混淆，至此可以大胆猜测，NeoX做了pyc混淆，开启游戏时首先加载redirect.pyc模块，此模块做了一些事情，很可能是解密文件得到pyc，然后再加载其他pyc    

#### 找加载文件流程
暂时不管redirect.nxs，继续顺藤摸瓜分析处理redirect.nxs的函数  

redirect.nxs的文件内容是从IScriptFileSystem的成员函数调用得到的  

IScriptFileSystem是通过字符串找出来的，继续搜字符串，找到注册IScriptFileSystem的地方，确认IScriptFileSystem的实际类型是neox::game::FileSystem

找到neox::game::FileSystem的vtable，其第一个成员函数为读取文件，假设叫ReadFile  

一路分析，可知neox::game::FileSystem::ReadFile调用neox::filesystem::NXFileSystem::Open

neox::filesystem::NXFileSystem::Open遍历neox::filesystem::NXFileLoader，采用第一个成功的FileLoader读出的结果  

找neox::filesystem::NXFileLoader的构造，可知是由多种FileLoaderCreator构造的，例如neox::filesystem::NXNpkLoaderCreator::NewLoader  

而所有FileLoaderCreator统一在neox::filesystem::NXFileLoaderCreatorManager::NXFileLoaderCreatorManager中注册自己  

通过名字猜测NXDiscreteFileLoaderCreator对应散文件，优先读取，NXNpkLoaderCreator对应npk  

通过动态调试确认上述猜测，应该是采用了常见手游文件管理方式，游戏发更新时直接将散文件存在文件系统，优先读取，没找到散文件则去资源包读取  

NXDiscreteFileLoader::Open直接调用neox::io::input的成员函数，将数据读进buffer  

neox::io::InputCFile应该是neox::io::input的主要实现，读取函数直接转发到fread  

neox::filesystem::NXNpkLoader::Open遍历了NxPackage，neox::filesystem::NXNpkLoader::NewPackage创建Package，可知实际类型为NxNpk  

NxNpk::Load又转发给NpkReader::Load  












#### 修复pyc
由前人工作，可知NeoX修改了CPython的opcode定义。可以看反汇编代码，也可以对比魔改的Python产生的pyc与原版，得到映射关系。  
我试图找到其他更简洁的方法，于是翻CPython源码，发现有个opcode模块可以直接打印opcode表。但是NeoX是Embed Python，opcode是py module，没有内置此模块。    
也没有想到其他的好办法，最后还是用对比pyc的方法拿到了opcode映射表。  

#### 修复无法识别的opcode
按前人记录，拿到opcode映射表以后就可以解码pyc了。实测后发现，NeoX又额外引入了一些opcode，这些opcode的作用与已有的不同，opcode映射表无法解决这些新opcde。  
由CPython源码，找到CPython解释执行opcode的实际函数PyEval_EvalFrameEx，对比源码与反汇编代码，得到这些新opcode的作用，基本就是旧opcode的组合。  
修复opcode时按规则将新opcode换成旧opcode的组合即可。  
这里可能有更好解法：  
1.令NeoX Python编译py得到带新opcode的pyc，对比原版。但是NeoX Python常规编译pyc是不带新opcode的。怀疑是有一个特殊的函数，或者独立的工具来编译带新opcode的pyc。NeoX Python只能够接收处理这些opcode，并不能生成。没有细找是否是特殊函数。（也不一定，从维护成本上来说，只魔改一个CPython仓库最好，所以可能是没找到这个特殊函数）  
2.令NeoX Python解读自己的pyc得到内存对象，再用原版Python函数输出原版pyc。仔细想了下，解读pyc得到的内存对象还是魔改过的一堆opcode，无法直接用原版Python输出。没找到是否有其他中间对象可供转换。（发现AST似乎可以当中间对象，但没有内置的pyc转AST的） 

#### 获得内置模块
NeoX从C++注册了一些模块，大部分不重要，部分重要的，查Python注册模块函数，能搜到模块函数表

参考  

