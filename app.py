"""
个人色彩诊断 Flask 后端
"""
import os
import json
from flask import Flask, request, jsonify, render_template, send_from_directory
from werkzeug.utils import secure_filename
from color_analyzer import analyze_image, COLOR_RECOMMENDATIONS, REFERENCE_COLOR_CARD
from PIL import Image
import base64
import io

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
app.config['UPLOAD_FOLDER'] = '/workspace/personal-color/uploads'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'bmp'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/analyze', methods=['POST'])
def analyze():
    """分析上传的照片 + 问卷"""
    try:
        # 获取问卷数据
        questionnaire = {}
        for key in ['q1_vein', 'q2_jewelry', 'q3_sun', 'q4_lipstick',
                     'q5_white', 'q6_foundation', 'q7_eyes_hair', 'q8_style']:
            questionnaire[key] = request.form.get(key, '')

        # 获取面部区域
        face_x = request.form.get('face_x', type=int)
        face_y = request.form.get('face_y', type=int)
        face_w = request.form.get('face_w', type=int)
        face_h = request.form.get('face_h', type=int)

        face_region = None
        if all(v is not None for v in [face_x, face_y, face_w, face_h]):
            face_region = (face_x, face_y, face_w, face_h)

        # 处理图片上传
        if 'photo' not in request.files:
            return jsonify({'error': '请上传照片'}), 400

        file = request.files['photo']
        if file.filename == '':
            return jsonify({'error': '请选择照片'}), 400

        if not allowed_file(file.filename):
            return jsonify({'error': '请上传 JPG/PNG/WebP 格式的图片'}), 400

        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # 执行分析
        result = analyze_image(filepath, questionnaire, face_region)

        # 构建返回数据
        rec = result.recommendations
        skin = result.skin_analysis

        response_data = {
            'season_type': result.season_type,
            'season_name': rec['name'],
            'season_name_kr': rec['name_kr'],
            'description': rec['description'],
            'warm_cool': result.warm_cool,
            'saturation_level': result.saturation_level,
            'brightness_level': result.brightness_level,
            'confidence': result.confidence,
            'skin_analysis': {
                'rgb': f'rgb({skin.r}, {skin.g}, {skin.b})',
                'hex': f'#{skin.r:02x}{skin.g:02x}{skin.b:02x}',
                'hsv': f'H:{skin.h}° S:{skin.s}% V:{skin.v}%',
                'h': skin.h, 's': skin.s, 'v': skin.v,
                'lab_l': skin.lab_l, 'lab_a': skin.lab_a, 'lab_b': skin.lab_b,
            },
            'final_score': result.final_score,
            'recommendations': {
                'best_colors': rec['best_colors'],
                'worst_colors': rec['worst_colors'],
                'lipstick': rec['lipstick'],
                'hair_color': rec['hair_color'],
                'style': rec['style'],
                'celebrities': rec['celebrities'],
                'keywords': rec['keywords'],
            },
        }

        # 清理上传文件
        try:
            os.remove(filepath)
        except:
            pass

        return jsonify(response_data)

    except Exception as e:
        return jsonify({'error': f'分析出错: {str(e)}'}), 500


@app.route('/api/reference-card', methods=['GET'])
def reference_card():
    """返回参考色卡数据"""
    return jsonify(REFERENCE_COLOR_CARD)


@app.route('/api/all-types', methods=['GET'])
def all_types():
    """返回所有 12 型的简要信息"""
    types = {}
    for key, data in COLOR_RECOMMENDATIONS.items():
        types[key] = {
            'name': data['name'],
            'name_kr': data['name_kr'],
            'description': data['description'],
            'keywords': data['keywords'],
            'best_colors': data['best_colors'][:3],
        }
    return jsonify(types)


@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
