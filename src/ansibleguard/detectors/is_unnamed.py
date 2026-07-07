def is_unnamed(play_name):
    if play_name is None or (isinstance(play_name, str) and not play_name.strip()):
        return 1
    else:
        return 0
