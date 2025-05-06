# -*- coding: utf-8 -*-

import os
import csv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import yt_dlp
import concurrent.futures
import threading

def get_youtube_videos(relevance_language="RU", max_results=100):
    """
    获取YouTube视频ID列表
    
    Args:
        relevance_language (str): 视频语言，默认为'RU'
        max_results (int): 需要获取的视频数量，默认为100
        
    Returns:
        list: 视频ID列表，如果发生错误则返回空列表
    """
    api_key = os.environ.get('YOUTUBE_API_KEY')
    
    if not api_key:
        print("错误: 未设置环境变量 YOUTUBE_API_KEY")
        return []
    
    try:
        youtube = build(
            "youtube", 
            "v3", 
            developerKey=api_key
        )

        videos = []
        next_page_token = None

        # 添加语言相关的搜索词来增加获取指定语言视频的概率
        language_keywords = {
            "DE": "lustige videos OR viral deutschland OR tiktok deutschland OR deutsche trends OR alltag deutschland OR deutsche memes",
            "EN": "funny moments OR epic fails OR life hacks OR viral videos OR daily vlog OR trending US OR british humor",
            "FR": "vidéos drôles OR insolite OR humour français OR tendances france OR vie quotidienne france OR blagues françaises",
            "ID": "video lucu OR prank indonesia OR viral indonesia OR konten kreator OR kehidupan sehari-hari OR cerita lucu",
            "IT": "video divertenti OR momenti divertenti OR virali italia OR vita quotidiana OR scherzi italiani OR trend italia",
            "JA": "面白い動画 OR バイラル OR ドッキリ OR 日常風景 OR 爆笑動画 OR トレンド動画 OR 人気動画",
            "KO": "웃긴영상 OR 예능 OR 유머 OR 바이럴 OR 일상 브이로그 OR 코미디 OR 트렌드",
            "PT": "vídeos engraçados OR pegadinhas OR viral brasil OR dia a dia OR humor brasileiro OR trends brasil",
            "RU": "смешные видео OR приколы OR вайны OR тренды OR повседневная жизнь OR юмор OR развлечения",
            "TH": "คลิปตลก OR ไวรัล OR ความบันเทิง OR ฮาๆ OR ชีวิตประจำวัน OR เรื่องฮาๆ OR ติ๊กต็อก",
            "TR": "komik videolar OR viral türkiye OR eğlenceli anlar OR günlük yaşam OR türk mizah OR trend videolar",
            "VI": "video hài hước OR hài việt nam OR clip vui OR viral OR cuộc sống hàng ngày OR giải trí OR xu hướng"
        }
        
        search_query = language_keywords.get(relevance_language, "")
        
        while len(videos) < max_results:
            request = youtube.search().list(
                part="id",
                maxResults=50,
                pageToken=next_page_token,
                publishedAfter="2023-01-01T00:00:00Z",
                relevanceLanguage=relevance_language,
                type="video",
                videoCaption="closedCaption",
                videoDuration="short",
                q=search_query,
            )
            response = request.execute()
            
            # 只提取视频ID
            for item in response.get('items', []):
                if 'id' in item and 'videoId' in item['id']:
                    videos.append(item['id']['videoId'])
            
            next_page_token = response.get('nextPageToken')
            
            if not next_page_token or len(videos) >= max_results:
                break
        
        return videos[:max_results]
        
    except HttpError as e:
        print(f"发生错误: {e}")
        return []

def download_youtube_video(video_id, relevance_language="RU"):
    """
    使用yt-dlp下载YouTube视频
    
    Args:
        video_id (str): YouTube视频ID
        relevance_language (str): 视频语言，用于确定保存目录
        
    Returns:
        bool: 下载成功返回True，失败返回False
    """
    output_dir = os.path.join('data', relevance_language)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    
    ydl_opts = {
        'format': 'bestaudio/best',  # 下载最佳音频质量
        'outtmpl': os.path.join(output_dir, f'%(title)s-{video_id}.%(ext)s'),
        'socket_timeout': 30,
        'retries': 1,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    
    try:
        # 首先获取视频信息
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            title = info['title']
            # 构建预期的输出文件路径
            expected_file = os.path.join(output_dir, f'{title}-{video_id}.mp3')
            
            # 检查文件是否已存在
            if os.path.exists(expected_file):
                print(f"文件已存在，跳过下载: {expected_file}")
                return True
                
            # 文件不存在，执行下载
            ydl.download([video_url])
        return True
    except Exception as e:
        print(f"下载视频时发生错误: {e}")
        return False

def read_parameters():
    """
    从 input.csv 文件中读取多组参数
    
    Returns:
        list: [(relevance_language, audio_num), ...]，包含多组参数的列表
    """
    try:
        parameters = []
        with open('input.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:  # 读取每一行数据
                try:
                    lang = row.get('relevance_language', 'RU')
                    num = int(row.get('audio_num', 120))
                    parameters.append((lang, num))
                except (ValueError, KeyError) as e:
                    print(f"跳过无效的参数行: {row}, 错误: {e}")
                    continue
        
        if not parameters:  # 如果没有读取到有效参数，使用默认值
            print("未读取到有效参数，使用默认参数值")
            return [('RU', 10)]
        
        return parameters
        
    except (FileNotFoundError, csv.Error) as e:
        print(f"读取参数文件时发生错误: {e}")
        print("使用默认参数值")
        return [('RU', 10)]

def process_parameter_set(params):
    """
    处理单个参数组合
    
    Args:
        params (tuple): (relevance_language, audio_num) 参数组合
    """
    relevance_language, audio_num = params
    print(f"\n处理参数组合: 语言={relevance_language}, 数量={audio_num}")
    
    # 使用线程锁确保打印输出不会混乱
    print_lock = threading.Lock()
    
    def safe_print(*args, **kwargs):
        with print_lock:
            print(*args, **kwargs)
    
    # 使用函数获取视频列表
    video_ids = get_youtube_videos(relevance_language=relevance_language, max_results=audio_num)
    safe_print(f"获取到 {len(video_ids)} 个视频ID")
    safe_print("视频ID列表:", video_ids)

    # 下载获取到的视频
    if video_ids:
        safe_print("\n开始下载视频...")
        for video_id in video_ids:
            safe_print(f"正在下载视频 {video_id}...")
            if download_youtube_video(video_id, relevance_language):
                safe_print(f"视频 {video_id} 下载成功")
            else:
                safe_print(f"视频 {video_id} 下载失败")
    safe_print(f"\n完成参数组合: 语言={relevance_language}, 数量={audio_num} 的处理")

def main():
    # 获取所有参数组合
    parameter_sets = read_parameters()
    
    # 使用线程池并发执行不同的参数组合
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        # 提交所有任务
        futures = [executor.submit(process_parameter_set, params) for params in parameter_sets]
        
        # 等待所有任务完成
        concurrent.futures.wait(futures)
        
    print("\n所有参数组合处理完成！")

if __name__ == "__main__":
    main()