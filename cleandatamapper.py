# Example Normalization Logic
def normalize_data(platform, raw_data):
    mapping = {
        "spotify": {"monthly_listeners": "total_listeners", "track_plays": "total_streams"},
        "apple": {"unique_listeners": "total_listeners", "plays": "total_streams"}
    }

    clean_data = {}
    for key, value in raw_data.items():
        if key in mapping[platform]:
            internal_key = mapping[platform][key]
            clean_data[internal_key] = value
    return clean_data