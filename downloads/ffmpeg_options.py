def get_ffmpeg_options(speed: float = 1) -> dict[str, str]:
    speed = round(speed, 2)

    if speed < 0.01:
        speed = 0.01
    elif speed > 10:
        speed = 10

    ffmpeg_options = {
        'options': f'-vn -filter:a "atempo={speed},atempo={speed}"',
        "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
    }

    return ffmpeg_options
