from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import tempfile
import os
import logging
import json
import traceback
import numpy as np
from brep_builder import construct_brep, save_step_file

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'brep-builder',
        'version': '1.0.0'
    })

@app.route('/build-brep', methods=['POST'])
def build_brep():
    """Build BREP from JSON input and return STEP file content"""
    try:
        data = request.get_json()
        
        # Extract required parameters
        surf_wcs = np.array(data.get('surf_wcs', []))
        edge_wcs = [np.array(edge) for edge in data.get('edge_wcs', [])]
        face_edge_adj = data.get('face_edge_adj', [])
        edge_vertex_adj = np.array(data.get('edge_vertex_adj', []))
        
        logger.info(f"Building BREP with {len(surf_wcs)} surfaces, {len(edge_wcs)} edges")
        
        # Validate input
        if len(surf_wcs) == 0:
            return jsonify({
                'success': False,
                'error': 'No surface data provided (surf_wcs is empty)'
            }), 400
        
        if len(edge_wcs) == 0:
            return jsonify({
                'success': False,
                'error': 'No edge data provided (edge_wcs is empty)'
            }), 400
        
        if len(face_edge_adj) == 0:
            return jsonify({
                'success': False,
                'error': 'No face-edge adjacency data provided'
            }), 400
        
        if len(edge_vertex_adj) == 0:
            return jsonify({
                'success': False,
                'error': 'No edge-vertex adjacency data provided'
            }), 400
        
        # Build the BREP
        solid = construct_brep(surf_wcs, edge_wcs, face_edge_adj, edge_vertex_adj)
        
        # Convert to STEP file content
        step_content = save_step_file(solid)
        
        return jsonify({
            'success': True,
            'step_content': step_content,
            'surfaces_count': len(surf_wcs),
            'edges_count': len(edge_wcs)
        })
        
    except Exception as e:
        logger.error(f"Error building BREP: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/build-brep/download', methods=['POST'])
def build_brep_download():
    """Build BREP and return STEP file for download"""
    try:
        data = request.get_json()
        
        # Extract required parameters
        surf_wcs = np.array(data.get('surf_wcs', []))
        edge_wcs = [np.array(edge) for edge in data.get('edge_wcs', [])]
        face_edge_adj = data.get('face_edge_adj', [])
        edge_vertex_adj = np.array(data.get('edge_vertex_adj', []))
        
        # Build the BREP
        solid = construct_brep(surf_wcs, edge_wcs, face_edge_adj, edge_vertex_adj)
        
        # Create temporary STEP file
        with tempfile.NamedTemporaryFile(suffix='.step', delete=False) as temp_file:
            save_step_file(solid, temp_file.name)
            temp_filename = temp_file.name
        
        return send_file(
            temp_filename,
            as_attachment=True,
            download_name='generated_brep.step',
            mimetype='application/step'
        )
        
    except Exception as e:
        logger.error(f"Error building BREP for download: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    logger.info("Starting BREP Builder Service on port 5002")
    app.run(host='0.0.0.0', port=5002, debug=True)