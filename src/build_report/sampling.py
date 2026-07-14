def reduce_points_by_ratio(points: list, ratio: int) -> list:
    target_count = max(2, int(len(points) * (ratio / 100)))
    if len(points) <= target_count:
        return points
    step = (len(points) - 1) / (target_count - 1)
    sampled = [
        points[round(i * step)]
        for i in range(target_count - 1)
    ]
    sampled.append(points[-1])
    return sampled


def reduce_points_to_limit(points: list, max_points: int) -> list:
    n = len(points)
    if n <= max_points:
        return points
    latest = points[-1]
    history = points[:-1]
    step = len(history) / (max_points - 1)
    sampled_history = [
        history[int(i * step)]
        for i in range(max_points - 1)
    ]
    merge = sampled_history + [latest]
    return merge
