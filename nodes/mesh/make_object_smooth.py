import bpy
from ... base_types.node import AnimationNode

class MakeObjectSmoothNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_MakeObjectSmoothNode"
    bl_label = "Make Object Smooth"

    def create(self):
        self.inputs.new("an_ObjectSocket", "Object", "object").defaultDrawType = "PROPERTY_ONLY"
        self.inputs.new("an_BooleanSocket", "Smooth", "smooth")
        self.outputs.new("an_ObjectSocket", "Object", "outObject")

    def execute(self, object, smooth):
        if getattr(object, "type", "") == "MESH":
            for polygon in object.data.polygons:
                polygon.use_smooth = smooth
        return object
