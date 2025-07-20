import os
import json
import copy

def print_message(obj, logger):
    obj_copy = copy.deepcopy(obj)

    if obj_copy['role'] != 'user':
        logger.info(obj_copy)
        return obj_copy
    else:
        if type(obj_copy['content']) == str:
            # print(obj)
            logger.info(obj_copy)
            return obj_copy
        else:
            print_obj = {
                'role': obj_copy['role'],
                'content': obj_copy['content']
            }
            for item in print_obj['content']:
                if item['type'] == 'image_url':
                    item['image_url'] =  {"url": "data:image/png;base64,{b64_img}"}
            logger.info(print_obj)
            return print_obj

def print_messages(json_object, save_dir=None):
    if not json_object:
        # No messages to print!
        return

    # Make a deep copy of the messages to avoid modifying the original object
    remove_b64code_obj = []
    for obj in json_object:
        obj_copy = copy.deepcopy(obj)

        if obj_copy['role'] != 'user':
            remove_b64code_obj.append(obj_copy)
        else:
            if type(obj_copy['content']) == str:
                remove_b64code_obj.append(obj_copy)
            else:
                print_obj = {
                    'role': obj_copy['role'],
                    'content': obj_copy['content']
                }
                for item in print_obj['content']:
                    if item['type'] == 'image_url':
                        item['image_url'] =  {"url": "data:image/png;base64,{b64_img}"}
                remove_b64code_obj.append(print_obj)
    
    if save_dir:
        with open(os.path.join(save_dir, f'messages.json'), 'w', encoding='utf-8') as fw:
            json.dump(remove_b64code_obj, fw, indent=2)
