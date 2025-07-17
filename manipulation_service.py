import tempfile
import os
from brep_operations import BrepOperations
import logging

logger = logging.getLogger(__name__)

class BrepManipulationService:
    def __init__(self):
        self.brep_ops = BrepOperations()
    
    def extend_face(self, step_content: str, face_id: int, parameters: dict) -> str:
        """Extend a face of the BREP model"""
        try:
            logger.info(f"Extending face {face_id} with parameters: {parameters}")
            
            # Load shape from STEP content
            shape = self.brep_ops.load_step_from_string(step_content)
            
            # Get the specific face
            face = self.brep_ops.get_face_by_id(shape, face_id)
            
            # Apply face extension
            distance = parameters.get('distance', 1.0)
            direction = parameters.get('direction', [0, 0, 1])  # Default to Z direction
            
            modified_shape = self.brep_ops.extend_face(shape, face, distance, direction)
            
            # Convert back to STEP content
            return self.brep_ops.shape_to_step_string(modified_shape)
            
        except Exception as e:
            logger.error(f"Error extending face: {str(e)}")
            raise e
    
    def extend_edge(self, step_content: str, edge_id: int, parameters: dict) -> str:
        """Extend an edge of the BREP model"""
        try:
            logger.info(f"Extending edge {edge_id} with parameters: {parameters}")
            
            shape = self.brep_ops.load_step_from_string(step_content)
            edge = self.brep_ops.get_edge_by_id(shape, edge_id)
            
            length = parameters.get('length', 1.0)
            both_directions = parameters.get('both_directions', False)
            
            modified_shape = self.brep_ops.extend_edge(shape, edge, length, both_directions)
            
            return self.brep_ops.shape_to_step_string(modified_shape)
            
        except Exception as e:
            logger.error(f"Error extending edge: {str(e)}")
            raise e
    
    def extrude_face(self, step_content: str, face_id: int, parameters: dict) -> str:
        """Extrude a face to create new geometry"""
        try:
            logger.info(f"Extruding face {face_id} with parameters: {parameters}")
            
            shape = self.brep_ops.load_step_from_string(step_content)
            face = self.brep_ops.get_face_by_id(shape, face_id)
            
            distance = parameters.get('distance', 1.0)
            direction = parameters.get('direction', [0, 0, 1])
            
            modified_shape = self.brep_ops.extrude_face(shape, face, distance, direction)
            
            return self.brep_ops.shape_to_step_string(modified_shape)
            
        except Exception as e:
            logger.error(f"Error extruding face: {str(e)}")
            raise e
    
    def offset_face(self, step_content: str, face_id: int, parameters: dict) -> str:
        """Offset a face by a specified distance"""
        try:
            logger.info(f"Offsetting face {face_id} with parameters: {parameters}")
            
            shape = self.brep_ops.load_step_from_string(step_content)
            face = self.brep_ops.get_face_by_id(shape, face_id)
            
            offset = parameters.get('offset', 0.1)
            
            modified_shape = self.brep_ops.offset_face(shape, face, offset)
            
            return self.brep_ops.shape_to_step_string(modified_shape)
            
        except Exception as e:
            logger.error(f"Error offsetting face: {str(e)}")
            raise e
    
    def fillet_edge(self, step_content: str, edge_id: int, parameters: dict) -> str:
        """Apply fillet to an edge"""
        try:
            logger.info(f"Filleting edge {edge_id} with parameters: {parameters}")
            
            shape = self.brep_ops.load_step_from_string(step_content)
            edge = self.brep_ops.get_edge_by_id(shape, edge_id)
            
            radius = parameters.get('radius', 0.1)
            
            modified_shape = self.brep_ops.fillet_edge(shape, edge, radius)
            
            return self.brep_ops.shape_to_step_string(modified_shape)
            
        except Exception as e:
            logger.error(f"Error filleting edge: {str(e)}")
            raise e
    
    def chamfer_edge(self, step_content: str, edge_id: int, parameters: dict) -> str:
        """Apply chamfer to an edge"""
        try:
            logger.info(f"Chamfering edge {edge_id} with parameters: {parameters}")
            
            shape = self.brep_ops.load_step_from_string(step_content)
            edge = self.brep_ops.get_edge_by_id(shape, edge_id)
            
            distance = parameters.get('distance', 0.1)
            
            modified_shape = self.brep_ops.chamfer_edge(shape, edge, distance)
            
            return self.brep_ops.shape_to_step_string(modified_shape)
            
        except Exception as e:
            logger.error(f"Error chamfering edge: {str(e)}")
            raise e
    
    def boolean_operation(self, step_content1: str, step_content2: str, operation: str) -> str:
        """Perform boolean operations between two shapes"""
        try:
            logger.info(f"Performing boolean {operation}")
            
            shape1 = self.brep_ops.load_step_from_string(step_content1)
            shape2 = self.brep_ops.load_step_from_string(step_content2)
            
            if operation == 'union':
                result = self.brep_ops.boolean_union(shape1, shape2)
            elif operation == 'difference':
                result = self.brep_ops.boolean_difference(shape1, shape2)
            elif operation == 'intersection':
                result = self.brep_ops.boolean_intersection(shape1, shape2)
            else:
                raise ValueError(f"Unknown boolean operation: {operation}")
            
            return self.brep_ops.shape_to_step_string(result)
            
        except Exception as e:
            logger.error(f"Error in boolean operation: {str(e)}")
            raise e