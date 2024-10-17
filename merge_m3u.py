import requests

def download_m3u(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text

def extract_url_tvg(m3u_data):
    for line in m3u_data.splitlines():
        if line.startswith("#EXTM3U") and "url-tvg=" in line:
            return line
    return "#EXTM3U"

def normalize_category(category):
    if category in ["Кинозал", "Русский кинозал", "Кинозалы", "Кино и сериалы"]:
        return "Кино и Сериалы"
    if category in ["Общественные"]:
        return "Эфирные"
    if category in ["Наш спорт"]:
        return "Спортивные"
    if category in ["Досуг"]:
        return "Хобби и увлечения"
    if category in ["Новостные"]:
        return "Новости"
    if category in ["Региoнальные"]: # Опечатка в листе
        return "Региональные"
    if category in ["Христианские"]:
        return "Религиозные"
    return category

def parse_m3u(m3u_data):
    channels = {}
    lines = m3u_data.splitlines()
    current_channel = None

    for line in lines:
        if line.startswith("#EXTINF"):
            if 'group-title="Взрослые"' in line:
                current_channel = None
                continue

            if 'group-title="' in line:
                group_title = line.split('group-title="')[1].split('"')[0]
                normalized_category = normalize_category(group_title)
                line = line.replace(f'group-title="{group_title}"', f'group-title="{normalized_category}"')

            tvg_id = None
            if 'tvg-id' in line:
                tvg_id = line.split('tvg-id="')[1].split('"')[0]
            current_channel = {"info": line, "stream": None, "tvg-id": tvg_id, "category": normalized_category}
        elif line and current_channel:
            current_channel["stream"] = line
            if current_channel["tvg-id"]:
                channels[current_channel["tvg-id"]] = current_channel
            current_channel = None

    return channels

def merge_m3u_channels(channels1, channels2):
    merged_channels = channels1.copy()

    for tvg_id, channel in channels2.items():
        if tvg_id in merged_channels:
            existing_channel = merged_channels[tvg_id]
            if channel["category"] == existing_channel["category"]:
                continue
        merged_channels[tvg_id] = channel

    return merged_channels

def extract_channel_name(extinf_line):
    return extinf_line.split(",", 1)[1].strip()

def write_m3u(filename, channels, url_tvg):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"{url_tvg}\n")
        sorted_channels = sorted(channels.values(), key=lambda channel: extract_channel_name(channel['info']))
        for channel in sorted_channels:
            f.write(f"{channel['info']}\n")
            f.write(f"{channel['stream']}\n")

url1 = "https://github.com/smolnp/IPTVru/raw/refs/heads/gh-pages/IPTVru.m3u"
url2 = "https://gitlab.com/iptv135435/iptvshared/raw/main/IPTV_SHARED.m3u"

m3u_data1 = download_m3u(url1)
m3u_data2 = download_m3u(url2)

url_tvg = extract_url_tvg(m3u_data2)

channels1 = parse_m3u(m3u_data1)
channels2 = parse_m3u(m3u_data2)

merged_channels = merge_m3u_channels(channels1, channels2)

output_filename = "merged_channels.m3u"
write_m3u(output_filename, merged_channels, url_tvg)
