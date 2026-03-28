from __future__ import annotations
from . import utils
from dataclasses import dataclass, field
import bpy,os
from bpy.types import (
    Operator,
    Panel,
    PropertyGroup,
    UILayout,
    Scene
)
from bpy.props import (
    BoolProperty,
    CollectionProperty,
    EnumProperty,
    StringProperty,
    
)

class Options(PropertyGroup):
    Deformer_String: StringProperty(name="",description="What is the deformer prefix used in your rig. Include seperator:(.|_)")# type: ignore
    Reference_String: StringProperty(name="", description="What is the reference prefix used in your rig. Include seperator:(.|_)")# type: ignore
    Mechanical_String: StringProperty(name="", description="What is the mechanical prefix used in your rig. Include seperator:(.|_)")# type: ignore
    
@dataclass
class BoneVisProps():
    Ref = { "custom_shape" : "REF",
           "color_palette": "CUSTOM",
           "color_custom_normal" : (0.518,0.506,0.196),
           "color_custom_select" : (0.859,0.827,0.380),
           "color_custom_active" : (1.0,0.969,0.0),
           "collection_name" : "Reference"}
    Def = { "custom_shape" : "DEF",
           "color_palette": "CUSTOM",
           "color_custom_normal" : (0.518,0.4,0.196),
           "color_custom_select" : (0.859,0.773,0.380),
           "color_custom_active" : (1.0,0.973,0.369),
           "collection_name" : "Deformer"}
    Mch = { "custom_shape" : "MCH",
           "color_palette": "CUSTOM",
           "color_custom_normal" : (0.0,0.0,0.0),
           "color_custom_select" : (0.5,0.5,0.5),
           "color_custom_active" : (1.0,1.0,1.0),
           "collection_name" : "Mechanical"}
    

class Def2Ref_OT_Operator(Operator):
    bl_idname="def2ref.operator"
    bl_label="Generate Ref"
    jim = ""

    def duplicate(self,arm, bone):
        new_bone= arm.edit_bones.new(self.ref_str + bone.name[len(self.def_str):])
        new_bone.length = bone.length
        new_bone.matrix = bone.matrix.copy()
        new_bone.use_connect = False
        
        if self.ref_str + bone.parent.name[len(self.def_str):] in arm.edit_bones:
            new_bone.parent = arm.edit_bones[self.ref_str + bone.parent.name[len(self.def_str):]] if bone.parent else bone.parent        
        else:
            new_bone.parent = bone.parent
        
        
        return new_bone
    
    def execute(self,context):
        import re
        
        bpy.ops.object.mode_set(mode = "EDIT")
        #edit mode
        #REGEX
        def_match = re.compile(fr"(?i)(?P<pre>^{self.def_str})")
        ref_match = re.compile(fr"(?i)(?P<pre>^{self.ref_str})")
        #RIG
        arm = context.active_object.data
        arm.use_mirror_x = False
        edit_bones = arm.edit_bones
        #BONES
        def_bones = [bone for bone in edit_bones if def_match.match(bone.name)]
        for bone in def_bones:
            if bone.parent is None :
                self.report(type = {'ERROR'}, message="Not all def bones have parents, please at least parentt bones to Root")
                return {"FINISHED"}           
        ref_bones = [self.duplicate(arm,bone) for bone in def_bones if self.ref_str + bone.name[len(self.def_str):] not in edit_bones]
        #BONE NAMES
        #you have to store the names because if you switch to pose mode and try and call edit bones the data get corupted and rearanged even in a list that is seperate from
        #the context of blender idky 
        ref_names = [bone.name for bone in ref_bones]
        def_names = [bone.name for bone in def_bones]

        
        
        
        #ERROR
        if not def_bones: 
            self.report(type = {'ERROR'}, message="No bones with given prefixes")
            return {'FINISHED'}
        if not ref_bones:
            self.report(type = {'ERROR'}, message="Refference bones already exist")
            return {'FINISHED'}
            
        #I hate this vvv but I have no clue how to fix it without a recursive search
        #Thankfully I can't imageigine any one having multiple non deforming chain roots at the stage I excepect this to be used
        #It is however slow  
        p = None
        for deff in def_bones:
            if not def_match.match(deff.parent.name): 
                p = deff.parent
        for deff in def_bones:
            deff.use_connect = False
            deff.parent = p
            
            
        #edit mode end
        
        #pose mode
        bpy.ops.object.mode_set(mode = "POSE")
        pose_bones = context.active_object.pose.bones
        
        #COLECTIONS
        bone_collections = arm.collections
        
        def_collection = bone_collections.new("Deformer") if "Deformer" not in bone_collections else bone_collections["Deformer"]
        ref_collection = bone_collections.new("Reference") if "Reference" not in bone_collections else bone_collections["Reference"]
        #Ref colections match      
        bones = arm.bones
        for deff in def_names:
            for name in [c.name for c in bones[deff].collections]:
                if self.ref_str+name[len(self.def_str):] not in arm.collections_all:
                    bone_collections.new(self.ref_str+name[len(self.def_str):])
        
        
         
        for ref,deff in zip(ref_names,def_names):
            
            for c in  bones[deff].collections:
                arm.collections_all[self.ref_str+c.name[len(self.def_str):]].assign(pose_bones[ref])
                
            pose_bones[ref].custom_shape = self.shapes["REF"]
            pose_bones[ref].color.palette = "CUSTOM"
            pose_bones[ref].color.custom.normal = (0.518,0.506,0.196)
            pose_bones[ref].color.custom.select = (0.859,0.827,0.380)
            pose_bones[ref].color.custom.active = (1.0,0.969,0.0)
            ref_collection.assign(pose_bones[ref])
            
            
            pose_bones[deff].constraints.new(type = "COPY_TRANSFORMS")
            pose_bones[deff].constraints[0].target = context.active_object
            pose_bones[deff].constraints[0].subtarget = ref 
            #end of constraints
            pose_bones[deff].custom_shape = self.shapes["DEF"]
            pose_bones[deff].color.palette = "CUSTOM"           
            pose_bones[deff].color.custom.normal = (0.518,0.4,0.196)
            pose_bones[deff].color.custom.select = (0.859,0.773,0.380)
            pose_bones[deff].color.custom.active = (1.0,0.973,0.369)
            pose_bones[deff].bone.hide_select = True
            #arm.collections_all["Deformer"].assign(pose_bones[deff])
            def_collection.assign(pose_bones[deff])
            
            
            
            
            
        

        #pose mode end
            
            
            
        return {'FINISHED'}
    
    @classmethod
    def m(cls, context):
        obj = context.active_object
        return obj.type == "ARMATURE" 
    
    def invoke(self,context,event):
        if "CTRL_SHAPES" not in context.scene.collection.children: 
            utils._import_shapes()
        shapes = "NO"
        for col in context.scene.collection.children:
            if "CTRL_SHAPES" in col.name:
                shapes = col.objects
                break
        if shapes == "NO":
            self.report(type = {'ERROR'}, message="Something went wron importing shapes")
            return {'FINISHED'}
        self.shapes = {"REF":"REF","DEF":"DEF","MCH":"MCH"}
        for shape in shapes:
            if "REF" in shape.name:
                self.shapes["REF"] = shape 
            elif "DEF" in shape.name:
                self.shapes["DEF"] = shape
            elif "MCH" in shape.name:
                self.shapes["MCH"] = shape        
        self.opt = context.scene.def2ref_opt
        self.def_str = self.opt.Deformer_String
        self.ref_str = self.opt.Reference_String 
        self.jim = "dogass"  
        return self.execute(context) 

class Def2Ref_OT_Organizer(Operator):
    bl_idname="def2ref.organizer"
    bl_label="Organize"
    shapes = "" 
    props = BoneVisProps()

    def update_visuals(self,context,bone, prop):
        bone.custom_shape = self.shapes[prop["custom_shape"]]
        bone.color.palette = prop["color_palette"]
        bone.color.custom.normal = prop["color_custom_normal"]
        bone.color.custom.select = prop["color_custom_select"]
        bone.color.custom.active = prop["color_custom_active"]
        context.active_object.data.collections_all[prop["collection_name"]].assign(bone)
        

    def execute(self,context):
        """"""
        arm =context.active_object
        bone_allcollections = arm.data.collections_all
        bones = arm.pose.bones
        
        

        for bone in bones:
            if self.def_str in bone.name:
                self.update_visuals(context,bone,self.props.Def)
            elif self.ref_str in bone.name:
                self.update_visuals(context,bone,self.props.Ref)
            elif self.mch_str in bone.name:
                self.update_visuals(context,bone,self.props.Mch)
                arm.data.bones[bone.name].show_wire = True
            else:
                continue
        return {'FINISHED'}
                


    def invoke(self,context,event):
        self.opt = context.scene.def2ref_opt
        self.def_str = self.opt.Deformer_String
        self.ref_str = self.opt.Reference_String
        self.mch_str = self.opt.Mechanical_String
        #should check for multiple scenes and thier colections would be easier and cost less
        if "CTRL_SHAPES" not in context.scene.collection.children:
            utils._import_shapes()
        shapes = "NO"
        for col in context.scene.collection.children:
            if "CTRL_SHAPES" in col.name:
                shapes = col.objects
                break
        if shapes == "NO":
            self.report(type = {'ERROR'}, message="Something went wron importing shapes")
            return {'FINISHED'}
        self.shapes = {"REF":"REF","DEF":"DEF","MCH":"MCH"}
        for shape in shapes:
            if "REF" in shape.name:
                self.shapes["REF"] = shape 
            elif "DEF" in shape.name:
                self.shapes["DEF"] = shape
            elif "MCH" in shape.name:
                self.shapes["MCH"] = shape
        arm =context.active_object.data
        bone_allcollections = arm.collections_all
        bone_collections = arm.collections
        bone_collections.new("Deformer") if "Deformer" not in bone_allcollections else bone_allcollections["Deformer"]
        bone_collections.new("Reference") if "Reference" not in bone_allcollections else bone_allcollections["Reference"]
        bone_collections.new("Mechanical") if "Mechanical" not in bone_allcollections else bone_allcollections["Mechanical"]
        return self.execute(context) 

class Def2Ref_PT_Panel(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Def2Ref'
    bl_label = "Def2Ref_PT"
    bl_idname = "DEF2REF_PT_panel"  

    
    def draw(self, context):
        opt = context.scene.def2ref_opt
        opt_keys = list(opt.__annotations__.keys())
        l = self.layout
        box = l.box()      
        for o in opt_keys:
            row = box.row()
            row.label(text = o + ":")
            row.prop(opt, o)
            row = box.row()
        row.operator("def2ref.operator")
        row = box.row()
        row.operator("def2ref.organizer")
           
    @classmethod
    def poll(cls, context):
        obj = context.active_object 
        return obj.type == "ARMATURE" if obj else False

