def recount_motion(motion: dict) -> tuple[int, int, int]:
    """
    recount curveCount, TotalSegmentCount and TotalPointCount in model3.json
    """
    segment_count = 0
    point_count = 0
    curves = motion["Curves"]
    curve_count = len(curves)
    for curve in curves:
        segments = curve["Segments"]
        end_pos = len(segments) 
        point_count += 1
        v = 2
        while v < end_pos:
            identifier = segments[v]
            if identifier == 0 or identifier == 2 or identifier == 3:
                point_count += 1
                v += 3
            elif identifier == 1:
                point_count += 3
                v += 7
            segment_count += 1
    return curve_count, segment_count, point_count
