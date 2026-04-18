# 自动整理图片和视频存放路径的工具

## ✨工具特性
- 在源目录下，自动建立 YYYY/mm 的文件夹，将媒体文件放到正确的目录中；
- 不修改图片，视频的文件名：兼容iPhone拍摄的实况照片；
- 如果存在重名文件，则跳过处理，并提示源文件路径。

## 🚀使用方法
1. 初始化环境
需要安装Python 3.12以上版本
```
git clone git@github.com:jefferylakie/organization_media_path.git
cd organization_media_path
python -m venv .venv
```


2. 使用虚拟环境
Windows:
`.venv\\Script\\activate`

macOS / Linux:
`source .venv/bin/activate`

3. 安装依赖库和使用
```
pip install -r requirements.txt
python main.py
```
