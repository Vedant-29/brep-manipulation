import tempfile
import os
from typing import List, Dict, Any, Tuple
import logging

# OpenCASCADE imports
from OCC.Core.STEPControl import STEPControl_Reader, STEPControl_Writer
from OCC.Core.IFSelect import IFSelect_RetDone, IFSelect_RetError
from OCC.Core.TopoDS import TopoDS_Shape, TopoDS_Face, TopoDS_Edge
from OCC.Core.TopExp import TopExp_Explorer
from OCC.Core.TopAbs import TopAbs_FACE, TopAbs_EDGE, TopAbs_VERTEX
from OCC.Core.BRepBuilderAPI import (
    BRepBuilderAPI_MakeVertex,
    BRepBuilderAPI_MakeEdge,
    BRepBuilderAPI_MakeFace,
    BRepBuilderAPI_Transform
)
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakePrism, BRepPrimAPI_MakeBox
from OCC.Core.BRepFilletAPI import BRepFilletAPI_MakeFillet, BRepFilletAPI_MakeChamfer
from OCC.Core.BRepOffsetAPI import BRepOffsetAPI_MakeOffset, BRepOffsetAPI_MakeThickSolid
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Fuse, BRepAlgoAPI_Cut, BRepAlgoAPI_Common
from OCC.Core.BRep import BRep_Tool
from OCC.Core.gp import gp_Vec, gp_Pnt, gp_Dir, gp_Trsf
from OCC.Core.TopTools import TopTools_ListOfShape
from OCC.Core.GeomAPI import GeomAPI_ProjectPointOnSurf
from OCC.Core.BRepAdaptor import BRepAdaptor_Surface
from OCC.Extend.TopologyUtils import TopologyExplorer
import io

logger = logging.getLogger(__name__)

class BrepOperations:
    def __init__(self):
        self.tolerance = 1e-6
    
    def load_step_from_string(self, step_content: str) -> TopoDS_Shape:
        """Load a STEP file from string content"""
        try:
            # Create a temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.step', delete=False) as temp_file:
                temp_file.write(step_content)
                temp_filename = temp_file.name
            
            # Read the STEP file
            reader = STEPControl_Reader()
            status = reader.ReadFile(temp_filename)
            
            # Clean up temp file
            os.unlink(temp_filename)
            
            if status != IFSelect_RetDone:
                raise ValueError("Failed to read STEP file content")
            
            reader.TransferRoot()
            shape = reader.OneShape()
            
            return shape
            
        except Exception as e:
            logger.error(f"Error loading STEP from string: {str(e)}")
            raise e
    
    def shape_to_step_string(self, shape: TopoDS_Shape) -> str:
        """Convert a shape to STEP file string content"""
        try:
            # Create a temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.step', delete=False) as temp_file:
                temp_filename = temp_file.name
            
            # Write the shape to STEP file
            writer = STEPControl_Writer()
            writer.Transfer(shape, IFSelect_RetDone)
            status = writer.Write(temp_filename)
            
            if status != IFSelect_RetDone:
                raise ValueError("Failed to write STEP file")
            
            # Read the file content
            with open(temp_filename, 'r') as f:
                step_content = f.read()
            
            # Clean up temp file
            os.unlink(temp_filename)
            
            return step_content
            
        except Exception as e:
            logger.error(f"Error converting shape to STEP string: {str(e)}")
            raise e
    
    def get_face_by_id(self, shape: TopoDS_Shape, face_id: int) -> TopoDS_Face:
        """Get a face by its ID (index)"""
        try:
            explorer = TopExp_Explorer(shape, TopAbs_FACE)
            faces = []
            
            while explorer.More():
                face = explorer.Current()
                faces.append(TopoDS_Face(face))
                explorer.Next()
            
            if face_id < 0 or face_id >= len(faces):
                raise ValueError(f"Face ID {face_id} out of range (0-{len(faces)-1})")
            
            return faces[face_id]
            
        except Exception as e:
            logger.error(f"Error getting face by ID: {str(e)}")
            raise e
    
    def get_edge_by_id(self, shape: TopoDS_Shape, edge_id: int) -> TopoDS_Edge:
        """Get an edge by its ID (index)"""
        try:
            explorer = TopExp_Explorer(shape, TopAbs_EDGE)
            edges = []
            
            while explorer.More():
                edge = explorer.Current()
                edges.append(TopoDS_Edge(edge))
                explorer.Next()
            
            if edge_id < 0 or edge_id >= len(edges):
                raise ValueError(f"Edge ID {edge_id} out of range (0-{len(edges)-1})")
            
            return edges[edge_id]
            
        except Exception as e:
            logger.error(f"Error getting edge by ID: {str(e)}")
            raise e
    
    def extend_face(self, shape: TopoDS_Shape, face: TopoDS_Face, distance: float, direction: List[float]) -> TopoDS_Shape:
        """Extend a face by extruding it"""
        try:
            # Create direction vector
            vec = gp_Vec(direction[0], direction[1], direction[2])
            vec.Normalize()
            vec.Scale(distance)
            
            # Create prism from face
            prism = BRepPrimAPI_MakePrism(face, vec)
            if not prism.IsDone():
                raise ValueError("Failed to create prism from face")
            
            extruded_shape = prism.Shape()
            
            # Fuse with original shape
            fuse = BRepAlgoAPI_Fuse(shape, extruded_shape)
            if not fuse.IsDone():
                raise ValueError("Failed to fuse extruded face with original shape")
            
            return fuse.Shape()
            
        except Exception as e:
            logger.error(f"Error extending face: {str(e)}")
            raise e
    
    def extend_edge(self, shape: TopoDS_Shape, edge: TopoDS_Edge, length: float, both_directions: bool = False) -> TopoDS_Shape:
        """Extend an edge"""
        try:
            # For now, we'll create a simple extension by creating a small extrusion
            # This is a simplified implementation - real edge extension is more complex
            
            # Get edge vertices
            vertices = []
            explorer = TopExp_Explorer(edge, TopAbs_VERTEX)
            while explorer.More():
                vertices.append(explorer.Current())
                explorer.Next()
            
            if len(vertices) < 2:
                raise ValueError("Edge must have at least 2 vertices")
            
            # For simplicity, return the original shape
            # In a real implementation, you would extend the edge geometry
            logger.warning("Edge extension is simplified - returning original shape")
            return shape
            
        except Exception as e:
            logger.error(f"Error extending edge: {str(e)}")
            raise e
    
    def extrude_face(self, shape: TopoDS_Shape, face: TopoDS_Face, distance: float, direction: List[float]) -> TopoDS_Shape:
        """Extrude a face to create new geometry"""
        return self.extend_face(shape, face, distance, direction)
    
    def offset_face(self, shape: TopoDS_Shape, face: TopoDS_Face, offset: float) -> TopoDS_Shape:
        """Offset a face"""
        try:
            # Create an offset surface
            # This is a simplified implementation
            offset_maker = BRepOffsetAPI_MakeThickSolid()
            
            faces_to_remove = TopTools_ListOfShape()
            faces_to_remove.Append(face)
            
            offset_maker.MakeThickSolidByJoin(shape, faces_to_remove, offset, self.tolerance)
            
            if not offset_maker.IsDone():
                raise ValueError("Failed to create offset")
            
            return offset_maker.Shape()
            
        except Exception as e:
            logger.error(f"Error offsetting face: {str(e)}")
            # Return original shape if offset fails
            return shape
    
    def fillet_edge(self, shape: TopoDS_Shape, edge: TopoDS_Edge, radius: float) -> TopoDS_Shape:
        """Apply fillet to an edge"""
        try:
            fillet = BRepFilletAPI_MakeFillet(shape)
            fillet.Add(radius, edge)
            
            if not fillet.IsDone():
                raise ValueError("Failed to create fillet")
            
            return fillet.Shape()
            
        except Exception as e:
            logger.error(f"Error creating fillet: {str(e)}")
            raise e
    
    def chamfer_edge(self, shape: TopoDS_Shape, edge: TopoDS_Edge, distance: float) -> TopoDS_Shape:
        """Apply chamfer to an edge"""
        try:
            chamfer = BRepFilletAPI_MakeChamfer(shape)
            chamfer.Add(distance, edge)
            
            if not chamfer.IsDone():
                raise ValueError("Failed to create chamfer")
            
            return chamfer.Shape()
            
        except Exception as e:
            logger.error(f"Error creating chamfer: {str(e)}")
            raise e
    
    def boolean_union(self, shape1: TopoDS_Shape, shape2: TopoDS_Shape) -> TopoDS_Shape:
        """Boolean union of two shapes"""
        try:
            union = BRepAlgoAPI_Fuse(shape1, shape2)
            if not union.IsDone():
                raise ValueError("Failed to perform boolean union")
            return union.Shape()
        except Exception as e:
            logger.error(f"Error in boolean union: {str(e)}")
            raise e
    
    def boolean_difference(self, shape1: TopoDS_Shape, shape2: TopoDS_Shape) -> TopoDS_Shape:
        """Boolean difference of two shapes"""
        try:
            difference = BRepAlgoAPI_Cut(shape1, shape2)
            if not difference.IsDone():
                raise ValueError("Failed to perform boolean difference")
            return difference.Shape()
        except Exception as e:
            logger.error(f"Error in boolean difference: {str(e)}")
            raise e
    
    def boolean_intersection(self, shape1: TopoDS_Shape, shape2: TopoDS_Shape) -> TopoDS_Shape:
        """Boolean intersection of two shapes"""
        try:
            intersection = BRepAlgoAPI_Common(shape1, shape2)
            if not intersection.IsDone():
                raise ValueError("Failed to perform boolean intersection")
            return intersection.Shape()
        except Exception as e:
            logger.error(f"Error in boolean intersection: {str(e)}")
            raise e
    
    def validate_step_content(self, step_content: str) -> Tuple[bool, Dict[str, Any]]:
        """Validate STEP file content and return info"""
        try:
            shape = self.load_step_from_string(step_content)
            
            # Count topology elements
            topo = TopologyExplorer(shape)
            
            info = {
                'faces_count': topo.number_of_faces(),
                'edges_count': topo.number_of_edges(),
                'vertices_count': topo.number_of_vertices(),
                'solids_count': topo.number_of_solids(),
                'shells_count': topo.number_of_shells(),
                'wires_count': topo.number_of_wires()
            }
            
            return True, info
            
        except Exception as e:
            return False, {'error': str(e)}
    
    def get_detailed_topology_info(self, step_content: str) -> Dict[str, Any]:
        """Get detailed topology information for manipulation"""
        try:
            shape = self.load_step_from_string(step_content)
            topo = TopologyExplorer(shape)
            
            # Get detailed information about each face
            faces_info = []
            for i, face in enumerate(topo.faces()):
                face_info = {
                    'id': i,
                    'type': 'face',
                    'area': self._get_face_area(face),
                    'center': self._get_face_center(face)
                }
                faces_info.append(face_info)
            
            # Get detailed information about each edge
            edges_info = []
            for i, edge in enumerate(topo.edges()):
                edge_info = {
                    'id': i,
                    'type': 'edge',
                    'length': self._get_edge_length(edge),
                    'center': self._get_edge_center(edge)
                }
                edges_info.append(edge_info)
            
            return {
                'faces': faces_info,
                'edges': edges_info,
                'total_faces': len(faces_info),
                'total_edges': len(edges_info),
                'total_vertices': topo.number_of_vertices()
            }
            
        except Exception as e:
            logger.error(f"Error getting topology info: {str(e)}")
            raise e
    
    def _get_face_area(self, face: TopoDS_Face) -> float:
        """Get the area of a face"""
        try:
            from OCC.Core.BRepGProp import brepgprop
            from OCC.Core.GProp import GProp_GProps
            
            props = GProp_GProps()
            brepgprop.SurfaceProperties(face, props)
            return props.Mass()
        except:
            return 0.0
    
    def _get_face_center(self, face: TopoDS_Face) -> List[float]:
        """Get the center point of a face"""
        try:
            from OCC.Core.BRepGProp import brepgprop
            from OCC.Core.GProp import GProp_GProps
            
            props = GProp_GProps()
            brepgprop.SurfaceProperties(face, props)
            center = props.CentreOfMass()
            return [center.X(), center.Y(), center.Z()]
        except:
            return [0.0, 0.0, 0.0]
    
    def _get_edge_length(self, edge: TopoDS_Edge) -> float:
        """Get the length of an edge"""
        try:
            from OCC.Core.BRepGProp import brepgprop
            from OCC.Core.GProp import GProp_GProps
            
            props = GProp_GProps()
            brepgprop.LinearProperties(edge, props)
            return props.Mass()
        except:
            return 0.0
    
    def _get_edge_center(self, edge: TopoDS_Edge) -> List[float]:
        """Get the center point of an edge"""
        try:
            from OCC.Core.BRepGProp import brepgprop
            from OCC.Core.GProp import GProp_GProps
            
            props = GProp_GProps()
            brepgprop.LinearProperties(edge, props)
            center = props.CentreOfMass()
            return [center.X(), center.Y(), center.Z()]
        except:
            return [0.0, 0.0, 0.0]