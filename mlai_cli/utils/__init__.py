def human_readable(value, unit='B', unit_size=1024):
    if value < 0:
        return '-{}'.format(human_readable(-value))
    if value >= (unit_size**5):
        return '{:.1f} P{}'.format(value / (unit_size**5), unit)
    elif value >= (unit_size**4):
        return '{:.1f} T{}'.format(value / (unit_size**4), unit)
    elif value >= (unit_size**3):
        return '{:.1f} G{}'.format(value / (unit_size**3), unit)
    elif value >= (unit_size**2):
        return '{:.1f} M{}'.format(value / (unit_size**2), unit)
    elif value >= unit_size:
        return '{:.1f} K{}'.format(value / (unit_size**1), unit)
    else:
        return '{:.1f} {}'.format(value, unit)