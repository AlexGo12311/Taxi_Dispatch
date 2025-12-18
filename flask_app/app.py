from flask import Flask, jsonify
from flask_cors import CORS
from config import config
from extentions import db

import logging

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    logging.basicConfig(level=logging.INFO)
    db.init_app(app)

    with app.app_context():
        from api import api_bp
        app.register_blueprint(api_bp)

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 'Ресурс не найден',
            'message': str(error)
        }), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'success': False,
            'error': 'Внутренняя ошибка сервера',
            'message': str(error)
        }), 500

    return app
app = create_app()

if __name__ == '__main__':
    port = 5003
    print(f"🔗 URL: http://localhost:{port}")

    app.run(host='0.0.0.0', port=port, debug=True)