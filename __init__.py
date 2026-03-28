# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
	"name": "Def2Ref",
	"author": "Marilyn M. Cere",
	"version": (1, 0, 0),
	"blender": (4, 4, 3),
	"description": "Create reference bones from deformation bones and constrain them aproprietly",
	"location": "",
	"warning": "",
	"wiki_url": "",
	"tracker_url": "",
	"category": "Rigging"
}

if "bpy" in locals():
    import importlib
    if "example" in locals():
        importlib.reload(def2ref)
else:
    import bpy
    from . import def2ref

addon_keymaps = {}

# def unregister_keymaps():
#     for km, kmi in addon_keymaps.values():
#         km.keymap_items.remove(kmi)
#     addon_keymaps.clear()
# def register_keymaps():
#     wm = bpy.context.window_manager
#     kc = wm.keyconfigs.addon
#     km = kc.keymaps.new(name="Window", space_type='EMPTY')
#     kmi = km.keymap_items.new('wm.def2ref', 'F2', 'PRESS', alt=True)
#     addon_keymaps['A2345'] = (km, kmi)


def register():
    #register_keymaps()
    
    bpy.utils.register_class(def2ref.Options)
    bpy.types.Scene.def2ref_opt = bpy.props.PointerProperty(type=def2ref.Options)
    bpy.utils.register_class(def2ref.Def2Ref_OT_Operator)
    bpy.utils.register_class(def2ref.Def2Ref_OT_Organizer)
    bpy.utils.register_class(def2ref.Def2Ref_PT_Panel)
    

def unregister():
    #unregister_keymaps()
    del bpy.types.Scene.def2ref_opt
    bpy.utils.unregister_class(def2ref.Options)
    bpy.utils.unregister_class(def2ref.Def2Ref_OT_Operator)
    bpy.utils.unregister_class(def2ref.Def2Ref_OT_Organizer)
    bpy.utils.unregister_class(def2ref.Def2Ref_PT_Panel)
    


if __name__ == "__main__":
    register()
