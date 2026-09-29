def available_qualities(info: dict) -> list[int]:
    return sorted(
        {
            item["height"]
            for item in info.get("formats", [])
            if item.get("height") and item.get("vcodec") != "none"
        }
    )