from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import tempfile
import logging
import json
import traceback
from manipulation_service import BrepManipulationService
from brep_operations import BrepOperations

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Initialize services
manipulation_service = BrepManipulationService()
brep_ops = BrepOperations()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'brep-manipulation',
        'version': '1.0.0'
    })

@app.route('/manipulate-brep', methods=['POST'])
def manipulate_brep():
    """Main BREP manipulation endpoint"""
    try:
        data = request.get_json()
        
        operation_type = data.get('operation_type')
        step_content = data.get('step_content')
        parameters = data.get('parameters', {})
        
        logger.info(f"Received manipulation request: {operation_type}")
        
        if not step_content:
            return jsonify({
                'success': False,
                'error': 'No STEP content provided'
            }), 400
        
        # Route to appropriate manipulation method
        if operation_type == 'extend_face':
            result = manipulation_service.extend_face(
                step_content,
                parameters.get('face_id'),
                parameters
            )
        elif operation_type == 'extend_edge':
            result = manipulation_service.extend_edge(
                step_content,
                parameters.get('edge_id'),
                parameters
            )
        elif operation_type == 'extrude_face':
            result = manipulation_service.extrude_face(
                step_content,
                parameters.get('face_id'),
                parameters
            )
        elif operation_type == 'offset_face':
            result = manipulation_service.offset_face(
                step_content,
                parameters.get('face_id'),
                parameters
            )
        elif operation_type == 'boolean_union':
            result = manipulation_service.boolean_operation(
                step_content,
                parameters.get('other_step_content'),
                'union'
            )
        elif operation_type == 'boolean_difference':
            result = manipulation_service.boolean_operation(
                step_content,
                parameters.get('other_step_content'),
                'difference'
            )
        elif operation_type == 'boolean_intersection':
            result = manipulation_service.boolean_operation(
                step_content,
                parameters.get('other_step_content'),
                'intersection'
            )
        elif operation_type == 'fillet_edge':
            result = manipulation_service.fillet_edge(
                step_content,
                parameters.get('edge_id'),
                parameters
            )
        elif operation_type == 'chamfer_edge':
            result = manipulation_service.chamfer_edge(
                step_content,
                parameters.get('edge_id'),
                parameters
            )
        else:
            return jsonify({
                'success': False,
                'error': f'Unknown operation type: {operation_type}'
            }), 400
        
        return jsonify({
            'success': True,
            'modified_step_content': result,
            'operation_applied': operation_type,
            'parameters_used': parameters
        })
        
    except Exception as e:
        logger.error(f"Error in BREP manipulation: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/validate-step', methods=['POST'])
def validate_step():
    """Validate STEP file content"""
    try:
        data = request.get_json()
        step_content = data.get('step_content')
        
        is_valid, info = brep_ops.validate_step_content(step_content)
        
        return jsonify({
            'valid': is_valid,
            'info': info
        })
        
    except Exception as e:
        return jsonify({
            'valid': False,
            'error': str(e)
        }), 500

@app.route('/get-topology-info', methods=['POST'])
def get_topology_info():
    """Get detailed topology information for manipulation"""
    try:
        data = request.get_json()
        step_content = data.get('step_content')
        
        topology_info = brep_ops.get_detailed_topology_info(step_content)
        
        return jsonify({
            'success': True,
            'topology_info': topology_info
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    logger.info("Starting BREP Manipulation Service on port 5002")
    app.run(host='0.0.0.0', port=5002, debug=True)