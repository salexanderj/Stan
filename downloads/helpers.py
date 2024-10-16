import lavalink
import validators
from typing import Optional, List

from voice.player import StanPlayer
from downloads.yt_downloader import YTDownloader
from downloads.other_downloader import OtherDownloader
from downloads.media_type import MediaType
from downloads.media_info import MediaInfo


async def extract_tracks(query: str,
                         player: StanPlayer,
                         reqeuster_name: Optional[str] = None,
                         requester_avatar_url: Optional[str] = None) -> List[lavalink.AudioTrack]:

    downloader = YTDownloader(MediaType.AUDIO)
    if validators.url(query) and 'youtube' not in query and 'youtu.be' not in query:
        downloader = OtherDownloader(MediaType.AUDIO)

    print(f"USING {downloader.__class__.__name__.upper()}")

    media_infos = await downloader.extract_media_info(query,
                                                      requester_name=reqeuster_name,
                                                      requester_avatar_url=requester_avatar_url)
    tracks: List[lavalink.AudioTrack] = []
    for media_info in media_infos:
        lavalink_result = await player.node.get_tracks(media_info.media_url)
        track = lavalink_result.tracks[0]
        track_with_media_info = attach_track_media_info(track, media_info)
        tracks.append(track_with_media_info)

    return tracks


def attach_track_media_info(track: lavalink.AudioTrack,
                            media_info: MediaInfo) -> lavalink.AudioTrack:

    return lavalink.AudioTrack(track,
                               track.requester,
                               media_info=media_info)
