


          
# YouTube audio downloader

## 项目简介
这是一个用于从YouTube下载音频的Python应用程序。该程序可以根据指定的语言、数量和关键词搜索YouTube视频并下载其音频内容。

## 功能特点
- 支持多语言视频搜索
- 可配置下载数量
- 支持关键词搜索
- 并发下载处理
- 支持CSV配置文件

## 环境要求
- Python 3.9+
- YouTube API密钥
- FFmpeg（用于音频处理）

## 安装步骤
1. 克隆仓库
2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 设置环境变量：
```bash
export YOUTUBE_API_KEY='你的YouTube API密钥'
```

## 使用方法
1. 配置input.csv文件，包含以下字段：
   - relevance_language: 视频语言代码（如RU, EN, zh-Hans等）
   - audio_num: 需要下载的音频数量
   - search_keywords: 搜索关键词

2. 运行程序：
```bash
python main.py
```

## 输出目录结构
下载的音频文件将保存在以下目录结构中：
```
data/
  ├── RU/        # 俄语音频
  ├── EN/        # 英语音频
  └── zh-Hans/   # 中文音频
```

## 注意事项
- 请确保有足够的磁盘空间
- 需要稳定的网络连接
- 遵守YouTube的服务条款和API使用限制
- 建议使用VPN以避免地理限制

## 许可证
开源许可证

## 贡献指南
欢迎提交Issue和Pull Request来帮助改进项目。
