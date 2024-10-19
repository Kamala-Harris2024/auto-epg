import xml.etree.ElementTree as ET
import os
import requests
import random

def load_m3u_tvg_ids(m3u_url):
    response = requests.get(m3u_url)
    m3u_content = response.text
    tvg_ids = set()

    for line in m3u_content.splitlines():
        if line.startswith('#EXTINF:'):
            parts = line.split('tvg-id="')
            if len(parts) > 1:
                tvg_id = parts[1].split('"')[0].strip()
                if tvg_id:
                    tvg_ids.add(tvg_id)
    return tvg_ids

def collect_unique_channels(target_dir, valid_tvg_ids, processed_ids):
    unique_channels = {}
    
    for dirpath, _, filenames in os.walk(target_dir):
        for filename in filenames:
            if filename.endswith('.xml'):
                input_file = os.path.join(dirpath, filename)
                print(f'Processing {input_file}...')
                
                tree = ET.parse(input_file)
                root = tree.getroot()
                
                for channel in root.findall('channel'):
                    xmltv_id = channel.get('xmltv_id')
                    
                    if xmltv_id and xmltv_id in valid_tvg_ids and xmltv_id not in processed_ids:
                        unique_channels[xmltv_id] = channel
                        processed_ids.add(xmltv_id)
    
    return unique_channels

def save_unique_channels(unique_channels, output_file):
    filtered_root = ET.Element('channels')
    
    channels_list = list(unique_channels.values())
    random.shuffle(channels_list)

    for channel in channels_list:
        filtered_root.append(channel)
    
    filtered_tree = ET.ElementTree(filtered_root)
    filtered_tree.write(output_file, encoding='utf-8', xml_declaration=True)

m3u_url = 'https://iptv-org.github.io/iptv/index.m3u'
valid_tvg_ids = load_m3u_tvg_ids(m3u_url)

base_directory = 'sites'
channels_directory = 'channels'
target_dirs = ['gatotv.com', 'mi.tv', 'dishtv.in', 'tv.cctv.com', 'movistarplus.es', 'tv.blue.ch', 'tvpassport.com', 'tvtv.us']

# Create the channels directory if it doesn't exist
os.makedirs(channels_directory, exist_ok=True)

processed_ids = set()
file_counter = 1

for target_dir in target_dirs:
    target_path = os.path.join(base_directory, target_dir)
    output_file = os.path.join(channels_directory, f'channels_{file_counter}.xml')
    
    unique_channels = collect_unique_channels(target_path, valid_tvg_ids, processed_ids)
    save_unique_channels(unique_channels, output_file)
    
    file_counter += 1
