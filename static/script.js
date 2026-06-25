/**
 * Personal Color 个人色彩诊断 - 前端交互
 */

// ─── 状态管理 ───
const state = {
    currentStep: 1,
    photoFile: null,
    faceRegion: null,
    isDragging: false,
    dragStart: { x: 0, y: 0 },
    selectorStart: { left: 0, top: 0, width: 0, height: 0 },
};

// ─── DOM 引用 ───
const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => document.querySelectorAll(sel);

const uploadArea = $('#upload-area');
const photoInput = $('#photo-input');
const previewArea = $('#preview-area');
const previewImg = $('#preview-img');
const faceSelector = $('#face-selector');
const btnNextStep = $('#btn-next-step');
const btnPrevStep = $('#btn-prev-step');
const btnReselect = $('#btn-reselect');
const btnAnalyze = $('#btn-analyze');
const btnRestart = $('#btn-restart');
const sectionUpload = $('#section-upload');
const sectionQuiz = $('#section-quiz');
const sectionResult = $('#section-result');
const loading = $('#loading');
const resultContent = $('#result-content');
const steps = $$('.step');

// ─── 步骤切换 ───
function showStep(step) {
    state.currentStep = step;
    sectionUpload.style.display = step === 1 ? '' : 'none';
    sectionQuiz.style.display = step === 2 ? '' : 'none';
    sectionResult.style.display = step === 3 ? '' : 'none';

    steps.forEach((s, i) => {
        s.classList.remove('active', 'completed');
        if (i + 1 < step) s.classList.add('completed');
        if (i + 1 === step) s.classList.add('active');
    });
}

// ─── 上传处理 ───
uploadArea.addEventListener('click', () => photoInput.click());

uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('drag-over');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('drag-over');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('drag-over');
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith('image/')) {
        handlePhoto(file);
    }
});

photoInput.addEventListener('change', () => {
    const file = photoInput.files[0];
    if (file) handlePhoto(file);
});

function handlePhoto(file) {
    state.photoFile = file;
    const reader = new FileReader();
    reader.onload = (e) => {
        previewImg.src = e.target.result;
        previewImg.onload = () => {
            // 重置选择器位置
            const imgW = previewImg.naturalWidth;
            const imgH = previewImg.naturalHeight;
            const displayW = previewImg.clientWidth;
            const displayH = previewImg.clientHeight;
            const scaleX = displayW / imgW;
            const scaleY = displayH / imgH;

            faceSelector.style.left = (displayW * 0.2) + 'px';
            faceSelector.style.top = (displayH * 0.15) + 'px';
            faceSelector.style.width = (displayW * 0.6) + 'px';
            faceSelector.style.height = (displayH * 0.55) + 'px';

            updateFaceRegion();
        };
        uploadArea.style.display = 'none';
        previewArea.style.display = '';
        btnNextStep.disabled = false;
    };
    reader.readAsDataURL(file);
}

btnReselect.addEventListener('click', () => {
    state.photoFile = null;
    previewImg.src = '';
    previewArea.style.display = 'none';
    uploadArea.style.display = '';
    btnNextStep.disabled = true;
    photoInput.value = '';
});

// ─── 面部区域选择器拖动 ───
faceSelector.addEventListener('mousedown', (e) => {
    state.isDragging = true;
    state.dragStart = { x: e.clientX, y: e.clientY };
    const style = faceSelector.style;
    state.selectorStart = {
        left: parseInt(style.left),
        top: parseInt(style.top),
        width: parseInt(style.width),
        height: parseInt(style.height),
    };
    e.preventDefault();
});

document.addEventListener('mousemove', (e) => {
    if (!state.isDragging) return;
    const dx = e.clientX - state.dragStart.x;
    const dy = e.clientY - state.dragStart.y;
    const container = previewImg.parentElement;
    const maxX = container.clientWidth - faceSelector.clientWidth;
    const maxY = container.clientHeight - faceSelector.clientHeight;

    let newLeft = state.selectorStart.left + dx;
    let newTop = state.selectorStart.top + dy;
    newLeft = Math.max(0, Math.min(newLeft, maxX));
    newTop = Math.max(0, Math.min(newTop, maxY));

    faceSelector.style.left = newLeft + 'px';
    faceSelector.style.top = newTop + 'px';
    updateFaceRegion();
});

document.addEventListener('mouseup', () => {
    if (state.isDragging) {
        state.isDragging = false;
        updateFaceRegion();
    }
});

// 触摸支持
faceSelector.addEventListener('touchstart', (e) => {
    state.isDragging = true;
    state.dragStart = { x: e.touches[0].clientX, y: e.touches[0].clientY };
    const style = faceSelector.style;
    state.selectorStart = {
        left: parseInt(style.left),
        top: parseInt(style.top),
        width: parseInt(style.width),
        height: parseInt(style.height),
    };
    e.preventDefault();
});

document.addEventListener('touchmove', (e) => {
    if (!state.isDragging) return;
    const dx = e.touches[0].clientX - state.dragStart.x;
    const dy = e.touches[0].clientY - state.dragStart.y;
    const container = previewImg.parentElement;
    const maxX = container.clientWidth - faceSelector.clientWidth;
    const maxY = container.clientHeight - faceSelector.clientHeight;

    let newLeft = state.selectorStart.left + dx;
    let newTop = state.selectorStart.top + dy;
    newLeft = Math.max(0, Math.min(newLeft, maxX));
    newTop = Math.max(0, Math.min(newTop, maxY));

    faceSelector.style.left = newLeft + 'px';
    faceSelector.style.top = newTop + 'px';
});

document.addEventListener('touchend', () => {
    if (state.isDragging) {
        state.isDragging = false;
        updateFaceRegion();
    }
});

function updateFaceRegion() {
    const imgW = previewImg.naturalWidth;
    const imgH = previewImg.naturalHeight;
    const displayW = previewImg.clientWidth;
    const displayH = previewImg.clientHeight;
    const scaleX = imgW / displayW;
    const scaleY = imgH / displayH;

    state.faceRegion = {
        x: Math.round(parseInt(faceSelector.style.left) * scaleX),
        y: Math.round(parseInt(faceSelector.style.top) * scaleY),
        w: Math.round(parseInt(faceSelector.style.width) * scaleX),
        h: Math.round(parseInt(faceSelector.style.height) * scaleY),
    };
}

// ─── 步骤导航 ───
btnNextStep.addEventListener('click', () => {
    if (!state.photoFile) return;
    updateFaceRegion();
    showStep(2);
});

btnPrevStep.addEventListener('click', () => {
    showStep(1);
});

// ─── 分析 ───
btnAnalyze.addEventListener('click', async () => {
    // 验证问卷
    const requiredQuestions = ['q1_vein', 'q2_jewelry', 'q3_sun', 'q4_lipstick',
        'q5_white', 'q6_foundation', 'q7_eyes_hair', 'q8_style'];
    let allAnswered = true;
    for (const q of requiredQuestions) {
        const checked = document.querySelector(`input[name="${q}"]:checked`);
        if (!checked) {
            allAnswered = false;
            // 高亮未回答的问题
            const quizItem = document.querySelector(`input[name="${q}"]`)?.closest('.quiz-item');
            if (quizItem) {
                quizItem.style.border = '2px solid #ef4444';
                quizItem.style.borderRadius = '12px';
                quizItem.style.padding = '12px';
                setTimeout(() => {
                    quizItem.style.border = '';
                    quizItem.style.padding = '';
                }, 2000);
            }
        }
    }

    if (!allAnswered) {
        alert('请回答所有问题后再进行分析！');
        return;
    }

    showStep(3);
    loading.style.display = '';
    resultContent.style.display = 'none';

    // 构建 FormData
    const formData = new FormData();
    formData.append('photo', state.photoFile);

    if (state.faceRegion) {
        formData.append('face_x', state.faceRegion.x);
        formData.append('face_y', state.faceRegion.y);
        formData.append('face_w', state.faceRegion.w);
        formData.append('face_h', state.faceRegion.h);
    }

    for (const q of requiredQuestions) {
        const checked = document.querySelector(`input[name="${q}"]:checked`);
        formData.append(q, checked.value);
    }

    try {
        const response = await fetch('/api/analyze', {
            method: 'POST',
            body: formData,
        });

        const data = await response.json();

        if (data.error) {
            alert('分析出错：' + data.error);
            showStep(2);
            return;
        }

        displayResult(data);
    } catch (err) {
        alert('网络错误：' + err.message);
        showStep(2);
    }
});

// ─── 结果展示 ───
function displayResult(data) {
    loading.style.display = 'none';
    resultContent.style.display = '';

    // Header
    $('#result-type-name').textContent = data.season_name;
    $('#result-type-kr').textContent = data.season_name_kr;
    const badge = $('#result-badge');
    badge.textContent = data.warm_cool === 'warm' ? '🔥 暖调' : '❄️ 冷调';
    badge.className = 'result-badge ' + (data.warm_cool === 'warm' ? 'badge-warm' : 'badge-cool');

    // 诊断详情
    const warmCoolMap = { warm: '🔥 暖调 (Warm)', cool: '❄️ 冷调 (Cool)', neutral: '⚖️ 中性' };
    const satMap = { soft: '🌫️ 柔 (Soft)', clear: '💎 净 (Clear)', medium: '📊 中等' };
    const briMap = { light: '☀️ 亮 (Light)', deep: '🌑 深 (Deep)', medium: '📊 中等' };

    $('#result-warm-cool').textContent = warmCoolMap[data.warm_cool] || data.warm_cool;
    $('#result-saturation').textContent = satMap[data.saturation_level] || data.saturation_level;
    $('#result-brightness').textContent = briMap[data.brightness_level] || data.brightness_level;
    $('#result-confidence').textContent = Math.round(data.confidence * 100) + '%';

    // 肤色色块
    const skinSwatch = $('#skin-swatch');
    skinSwatch.style.backgroundColor = data.skin_analysis.rgb;
    $('#skin-hex').textContent = data.skin_analysis.hex + '  ' + data.skin_analysis.hsv;

    // 推荐颜色
    renderColorPalette('best-colors', data.recommendations.best_colors);
    renderColorPalette('worst-colors', data.recommendations.worst_colors);

    // 口红
    const lipList = $('#lipstick-list');
    lipList.innerHTML = data.recommendations.lipstick.map(l => `<li>💄 ${l}</li>`).join('');

    // 发色
    const hairList = $('#hair-list');
    hairList.innerHTML = data.recommendations.hair_color.map(h => `<li>💇 ${h}</li>`).join('');

    // 穿搭风格
    $('#result-style').textContent = data.recommendations.style;

    // 明星
    const celebList = $('#celebrity-list');
    celebList.innerHTML = data.recommendations.celebrities.map(c => `<span class="celebrity-tag">⭐ ${c}</span>`).join('');

    // 关键词
    const kwList = $('#keyword-list');
    kwList.innerHTML = data.recommendations.keywords.map(k => `<span class="keyword-tag">#${k}</span>`).join('');

    // 评分条
    renderScoreBars(data.final_score);

    // 滚动到结果
    sectionResult.scrollIntoView({ behavior: 'smooth' });
}

function renderColorPalette(containerId, colors) {
    const container = $(`#${containerId}`);
    container.innerHTML = colors.map(hex => {
        const isLight = isLightColor(hex);
        return `<div class="color-chip" 
                     style="background:${hex}" 
                     data-hex="${hex}"
                     title="${hex}"></div>`;
    }).join('');
}

function isLightColor(hex) {
    const r = parseInt(hex.slice(1, 3), 16);
    const g = parseInt(hex.slice(3, 5), 16);
    const b = parseInt(hex.slice(5, 7), 16);
    return (r * 299 + g * 587 + b * 114) / 1000 > 150;
}

function renderScoreBars(scores) {
    const bars = $('#score-bars');
    const items = [
        { key: 'warm', label: '暖调', color: '#f59e0b' },
        { key: 'cool', label: '冷调', color: '#3b82f6' },
        { key: 'soft', label: '柔和', color: '#a78bfa' },
        { key: 'clear', label: '鲜明', color: '#ec4899' },
        { key: 'light', label: '明亮', color: '#fbbf24' },
        { key: 'deep', label: '深沉', color: '#1e293b' },
    ];

    bars.innerHTML = items.map(item => {
        const val = (scores[item.key] || 0) * 100;
        return `
            <div class="score-row">
                <span class="score-label">${item.label}</span>
                <div class="score-bar-wrap">
                    <div class="score-bar" style="width:${Math.min(val, 100)}%;background:${item.color}"></div>
                </div>
                <span class="score-value">${Math.round(val)}%</span>
            </div>
        `;
    }).join('');
}

// ─── 重新测试 ───
btnRestart.addEventListener('click', () => {
    state.photoFile = null;
    state.faceRegion = null;
    previewImg.src = '';
    previewArea.style.display = 'none';
    uploadArea.style.display = '';
    btnNextStep.disabled = true;
    photoInput.value = '';
    document.getElementById('quiz-form').reset();
    loading.style.display = 'none';
    resultContent.style.display = 'none';
    showStep(1);
    window.scrollTo({ top: 0, behavior: 'smooth' });
});
