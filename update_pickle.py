import json
import pickle
import sys

def update_pickle_file_from_json():
    try:
        with open('maps.json') as json_file:
            mappings = json.load(json_file)
        with open('oncore_code_mappings.p', 'wb') as pickle_file:
            pickle.dump(mappings, pickle_file)
        print('oncore_code_mappings.p updated from maps.json')
    except:
        print('You must export your pickle file to json before updating it.')


def dump_pickle_to_json():
    with open('oncore_code_mappings.p', 'rb') as pickle_file:
        mappings = pickle.load(pickle_file)
    with open('maps.json', 'w') as json_file:
        json.dump(mappings, json_file, indent=2)
    print('Pickle file dumped to maps.json', 'Please make your updates there.\n', 'Once finished, run:', 'python update_pickle.py import\n')


def main():
    arg = sys.argv[1]
    if arg == 'export':
        dump_pickle_to_json()
    elif arg == 'import':
        update_pickle_file_from_json()
    else:
        print('Valid commands are:\nimport\nexport')
        

if __name__ == '__main__':
    main()
