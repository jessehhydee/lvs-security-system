from flask import Flask, jsonify, request, Response
import socket
from logs import Logs
from capture import Capture

server = Flask(__name__)
logs = Logs()
capture = Capture()

"""
Creates a UDP socket.
Makes call to Googles DNS Server.
This helps determine which network is used to communicate with the WWW.
s.getsockname() returns a tuple containing the local address and port.
[0] grabs the IP from the tuple.

Returns:
    str: A string that holds the devices local ip address
"""
def get_local_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
    except Exception as e:
        raise RuntimeError(f"Error obtaining local IP address: {e}")
    return ip

@server.errorhandler(404)
def not_found_error(err) -> tuple[Response, int]:
    return jsonify({
        "success": False,
        "error": f"Not found: {str(err)}"
    }), 404

@server.errorhandler(500)
def internal_error(err) -> tuple[Response, int]:
    return jsonify({
        "success": False,
        "error": f"Internal server error: {str(err)}"
    }), 500

@server.route('/capture', methods=['POST'])
def capture_endpoint() -> tuple[Response, int]:
    try:
        cam_port = request.args.get("cam_port")
        if cam_port is not None:
            event = capture.handle_capture(cam_port)
        else:
            event = capture.handle_capture()

        logs.new_event_log(event)
        logs.new_system_log("Successful /capture call")
        return jsonify({
            "success": True,
            "event": event
        }), 201
    except Exception as err:
        logs.new_system_log(f"Failed /capture call: {str(err)}", True)
        return jsonify({
            "success": False,
            "error": str(err)
        }), 400 if str(err) == 'cam_port needs to be an integer' else 500

@server.route('/image-captures', methods=['DELETE'])
def clear_image_captures_endpoint() -> tuple[Response, int]:
    try:
        capture.clear_images_dir()

        logs.new_system_log("Successful clearing of images directory")
        return jsonify({
            "success": True
        }), 200
    except Exception as err:
        logs.new_system_log(f"Failed to clear images directory: {str(err)}", True)
        return jsonify({
            "success": False,
            "error": str(err)
        }), 500

@server.route('/events-log', methods=['DELETE'])
def clear_events_endpoint() -> tuple[Response, int]:
    try:
        logs.clear_event_logs()

        logs.new_system_log("Successful clearing of events log")
        return jsonify({
            "success": True
        }), 200
    except Exception as err:
        logs.new_system_log(f"Failed to clear events log: {str(err)}", True)
        return jsonify({
            "success": False,
            "error": str(err)
        }), 500

@server.route('/systems-log', methods=['DELETE'])
def clear_systems_endpoint() -> tuple[Response, int]:
    try:
        logs.clear_system_logs()

        logs.new_system_log("Successful clearing of systems log")
        return jsonify({
            "success": True
        }), 200
    except Exception as err:
        logs.new_system_log(f"Failed to clear systems log: {str(err)}", True)
        return jsonify({
            "success": False,
            "error": str(err)
        }), 500

def main() -> None:
    server.run(host = get_local_ip(), port = 8000)

if __name__ == "__main__":
    main()
