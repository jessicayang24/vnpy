:: 定制环境安装公司内部定制软件
:: 需要预先安装vnstation 到 D:/wc-vnstudio
echo call activate
call D:\wc-vnstudio\Scripts\activate.bat
echo env switch complete
pip install --upgrade git+git://github.com/fsksf/vnpy.git
pip install --upgrade git+git://github.com/fsksf/vnpy_ctastrategy.git
pip install --upgrade git+git://github.com/fsksf/vnpy_tap.git
