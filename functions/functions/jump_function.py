def jump_val(time, start, end, jumptime=5000):
    if time < jumptime:
        return start
    else:
        return end

    