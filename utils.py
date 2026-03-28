import bpy,os

def _import_shapes():
    file_dir = os.path.dirname(os.path.abspath(__file__))
    addon_directory = os.path.dirname(file_dir)    
    filepath = addon_directory + "/def2ref/CTRL_SAPES.blend"

    with bpy.data.libraries.load(filepath, link=False) as (data_from, data_to):
        #data_to.objects = data_from.objects
        data_to.collections = data_from.collections


    for collec in data_to.collections:
        bpy.context.scene.collection.children.link(collec)
