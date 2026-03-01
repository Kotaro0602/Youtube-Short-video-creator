"""
わせだや YouTube Data API v3 データ取得スクリプト

チャンネルの直近30本の動画とコメントを取得し、
wasedaya-skills/data/youtube_data.json に保存する。

使い方:
    export YOUTUBE_API_KEY="your-api-key"
    export YOUTUBE_CHANNEL_ID="your-channel-id"
    python wasedaya-skills/scripts/fetch_youtube_data.py
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ImportError:
    print("エラー: google-api-python-client がインストールされていません。")
    print("以下を実行してください:")
    print("  pip install google-api-python-client")
    sys.exit(1)


def get_channel_uploads_playlist(youtube, channel_id: str) -> str:
    """チャンネルのアップロード再生リストIDを取得する。"""
    response = youtube.channels().list(
        part="contentDetails",
        id=channel_id,
    ).execute()

    if not response.get("items"):
        print(f"エラー: チャンネルID '{channel_id}' が見つかりません。")
        sys.exit(1)

    return response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]


def get_recent_videos(youtube, playlist_id: str, max_results: int = 30) -> list[str]:
    """再生リストから直近の動画IDを取得する。"""
    video_ids = []
    next_page_token = None

    while len(video_ids) < max_results:
        response = youtube.playlistItems().list(
            part="contentDetails",
            playlistId=playlist_id,
            maxResults=min(50, max_results - len(video_ids)),
            pageToken=next_page_token,
        ).execute()

        for item in response.get("items", []):
            video_ids.append(item["contentDetails"]["videoId"])

        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break

    return video_ids[:max_results]


def get_video_details(youtube, video_ids: list[str]) -> list[dict]:
    """動画のメタデータ（タイトル、再生数等）を取得する。"""
    videos = []

    # API は1リクエストで最大50件
    for i in range(0, len(video_ids), 50):
        batch = video_ids[i : i + 50]
        response = youtube.videos().list(
            part="snippet,statistics",
            id=",".join(batch),
        ).execute()

        for item in response.get("items", []):
            snippet = item["snippet"]
            stats = item.get("statistics", {})
            videos.append({
                "video_id": item["id"],
                "title": snippet["title"],
                "published_at": snippet["publishedAt"][:10],
                "view_count": int(stats.get("viewCount", 0)),
                "like_count": int(stats.get("likeCount", 0)),
                "comment_count": int(stats.get("commentCount", 0)),
                "top_comments": [],
            })

    return videos


def get_top_comments(youtube, video_id: str, max_results: int = 50) -> list[dict]:
    """動画の上位コメント（いいね数順）を取得する。"""
    try:
        response = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            order="relevance",
            maxResults=max_results,
            textFormat="plainText",
        ).execute()

        comments = []
        for item in response.get("items", []):
            comment = item["snippet"]["topLevelComment"]["snippet"]
            comments.append({
                "text": comment["textDisplay"],
                "like_count": comment["likeCount"],
            })

        # いいね数で降順ソート
        comments.sort(key=lambda c: c["like_count"], reverse=True)
        return comments

    except HttpError as e:
        if e.resp.status == 403:
            # コメントが無効化されている動画
            return []
        raise


def main():
    api_key = os.environ.get("YOUTUBE_API_KEY")
    channel_id = os.environ.get("YOUTUBE_CHANNEL_ID")

    if not api_key:
        print("エラー: 環境変数 YOUTUBE_API_KEY が設定されていません。")
        print("  export YOUTUBE_API_KEY='your-api-key'")
        sys.exit(1)

    if not channel_id:
        print("エラー: 環境変数 YOUTUBE_CHANNEL_ID が設定されていません。")
        print("  export YOUTUBE_CHANNEL_ID='your-channel-id'")
        sys.exit(1)

    youtube = build("youtube", "v3", developerKey=api_key)

    print("チャンネル情報を取得中...")
    playlist_id = get_channel_uploads_playlist(youtube, channel_id)

    print("直近の動画一覧を取得中...")
    video_ids = get_recent_videos(youtube, playlist_id, max_results=30)
    print(f"  {len(video_ids)}本の動画を取得")

    print("動画の詳細情報を取得中...")
    videos = get_video_details(youtube, video_ids)

    print("コメントを取得中...")
    for i, video in enumerate(videos):
        video["top_comments"] = get_top_comments(
            youtube, video["video_id"], max_results=50
        )
        print(f"  [{i + 1}/{len(videos)}] {video['title'][:30]}... ({len(video['top_comments'])}件)")

    data = {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "channel_id": channel_id,
        "videos": videos,
    }

    # 出力先
    script_dir = Path(__file__).resolve().parent
    output_path = script_dir.parent / "data" / "youtube_data.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\n保存完了: {output_path}")
    print(f"動画数: {len(videos)}")
    total_comments = sum(len(v['top_comments']) for v in videos)
    print(f"コメント総数: {total_comments}")


if __name__ == "__main__":
    main()
