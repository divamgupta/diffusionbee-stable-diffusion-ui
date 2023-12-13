import random

def get_textbox(id, type="str" , default="" ,  title="" , description=""):

    types = {"str" : "text" , "int" : "number" , "float" : "number"}

    return {
                "id": str(random.randint(0,19989999)),
                "component": "InputWithDesc",
                "title": title,
                "description":description ,
                "children": [
                    {
                        "id": id,
                        "component": "Textbox",
                        "placeholder" : "",
                        "default_value" : default ,
                        "type" : types[type],
                        "output_type" :type ,
                        "is_persistant" : False
                    }
                ]
            }

def get_output_text(text):
    return {
        "id":  str(random.randint(0,19989999)),
        "component": "OutputText",
        "text" : text
    }
def get_output_img(img_path, save_ext='.png' , is_save=False):
    return {
        "id":  str(random.randint(0,19989999)),
        "component": "OutputImage",
        "img_path" : img_path,
        "is_save" : is_save , 
        "save_ext" : save_ext 
    }

def get_file_textbox(id , path_type="",  title="" , description="" ):
    return {
                "id":  str(random.randint(0,19989999)),
                "component": "InputWithDesc",
                "full_width": True,
                "title": title,
                "description": description,
                "children": [
                    {
                        "id": id ,
                        "component": "FilePathTextBox",
                        "placeholder" : "",
                        "is_persistant" : False,
                        "path_type" : path_type
                    },
                ]
            }

def get_textarea(id ,   title="" , description="" ):
    return {
                "id":  str(random.randint(0,19989999)),
                "component": "InputWithDesc",
                "full_width": True,
                "title": title,
                "description": description,
                "children": [
                    {
                        "id": id ,
                        "component": "Textarea",
                        "placeholder" : title ,
                        "is_small" : True,
                        "is_persistant" : False,
                    },
                ]
            }

