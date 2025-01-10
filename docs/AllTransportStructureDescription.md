# Data structure for all means of transport: description of files

generate_connections_trips_ztm.py - The file responsible for ZTM data processing, has already been used for heatmap generation. Reused now for data merging and structure compatibilities. Renamed for the recognition of individual scripts.

compare_stops.py - comparing of stops_[ ].txt files in search of duplications of ids beetwen structures in the folder. If found changes to ids in one structure should be implemented.

generate_connections_trips_skm.py - The file responsible for SKM data processing, with changes for correct reading of SKM data (difference form ZTM). There was no need to rename trips's ids because there were no repeatable keys with ZTM.

merge_jsons.py - merging of all connection_by_trips_[ ].json files in the same directory into one JSON file.

download_stops_files - downloading specified in the dictionary gtfs_data zip files and extracting only stop.txt files with the change of the name of the file depending of the sort of communication which it represents.

stop_list.py - collecting of all stop_[].txt files into one sorted unified_stops.csv, information about stop name, id, coordinations and transport type.

generate_connections_trips_ztm_zkm_skm.py - script combining functions of download_stops_files with added stoptimes, generation of connections for ztm, zkm, skm data and merging od json into one file
