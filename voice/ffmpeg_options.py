from utils import clamp

def get_ffmpeg_options(rate: float = 1) -> dict[str, str]:

    rate = round(rate, 2)
    rate = clamp(rate, 0.5, 100.0)

    ffmpeg_options = {
            'options': f'-vn -filter:a "atempo={rate}"',
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'
    }

    return ffmpeg_options
