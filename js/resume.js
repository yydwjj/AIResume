const ResumeModule = {
    resumeList: [],
    currentResume: null,

    init() {
        this.setupUploadArea();
        this.setupSummaryToggle();
        this.loadResumeList();
    },

    setupUploadArea() {
        const uploadArea = document.getElementById('upload-area');
        const fileInput = document.getElementById('resume-file');

        uploadArea.addEventListener('click', () => fileInput.click());

        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });

        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');

            const files = e.dataTransfer.files;
            if (files.length > 0) {
                this.handleFileUpload(files[0]);
            }
        });

        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                this.handleFileUpload(e.target.files[0]);
            }
        });
    },

    setupSummaryToggle() {
        const summary = document.getElementById('resume-summary');
        const resultContent = document.getElementById('resume-result-content');

        summary.addEventListener('click', () => {
            if (resultContent.style.display === 'none') {
                resultContent.style.display = 'block';
                summary.querySelector('.expand-hint').textContent = '点击收起详细信息';
            } else {
                resultContent.style.display = 'none';
                summary.querySelector('.expand-hint').textContent = '点击展开详细信息';
            }
        });
    },

    async handleFileUpload(file) {
        if (!file.name.endsWith('.pdf')) {
            showError('请上传PDF文件');
            return;
        }

        if (file.size > 10 * 1024 * 1024) {
            showError('文件大小不能超过10MB');
            return;
        }

        const progressArea = document.getElementById('resume-progress');
        const resultArea = document.getElementById('resume-result');
        const uploadArea = document.getElementById('upload-area');
        const statusText = document.querySelector('#resume-progress .status-text');

        uploadArea.style.display = 'none';
        progressArea.style.display = 'block';
        resultArea.style.display = 'none';
        statusText.textContent = '正在解析中...';

        try {
            const response = await API.uploadResume(file);

            if (response.success) {
                if (response.cached || !response.task_id) {
                    statusText.textContent = '使用缓存，加载解析结果...';

                    await this.loadResumeList();

                    const resumeSelect = document.getElementById('resume-select');
                    resumeSelect.value = response.file_hash;

                    if (response.data) {
                        this.displayResumeResult(response.data);
                    }

                    showSuccess('简历解析完成（使用缓存）');
                } else {
                    await pollTaskStatus(response.task_id, (task) => {
                        this.updateProgress(task.progress, task.stage);
                    });

                    await this.loadResumeList();

                    const resumeSelect = document.getElementById('resume-select');
                    resumeSelect.value = response.file_hash;

                    showSuccess('简历解析完成');
                }

                uploadArea.style.display = 'block';
                progressArea.style.display = 'none';
            } else {
                throw new Error(response.error || '上传失败');
            }
        } catch (error) {
            showError(error.message);
            uploadArea.style.display = 'block';
            progressArea.style.display = 'none';
        }
    },

    updateProgress(progress, stage) {
        const progressBar = document.getElementById('resume-progress-bar');
        const statusText = document.querySelector('#resume-progress .status-text');

        progressBar.style.width = `${progress}%`;
        statusText.textContent = stage || '处理中...';
    },

    async loadResumeList() {
        try {
            const response = await API.getResumeList();

            if (response.success) {
                this.resumeList = response.data.resumes || [];
                this.updateResumeSelect();
            }
        } catch (error) {
            console.error('加载简历列表失败:', error);
        }
    },

    updateResumeSelect() {
        const select = document.getElementById('resume-select');

        select.innerHTML = '<option value="">请选择简历</option>';

        this.resumeList.forEach(resume => {
            const option = document.createElement('option');
            option.value = resume.hash;
            option.textContent = resume.name || `简历 ${resume.hash.substring(0, 8)}`;
            select.appendChild(option);
        });
    },

    async loadResume(hash) {
        try {
            const response = await API.getResume(hash);

            if (response.success) {
                this.currentResume = response.data;
                this.displayResumeResult(response.data);
                return response.data;
            }
        } catch (error) {
            console.error('加载简历失败:', error);
        }
    },

    displayResumeResult(data) {
        const resultArea = document.getElementById('resume-result');
        const resultContent = document.getElementById('resume-result-content');
        const summary = document.getElementById('resume-summary');
        const summaryContent = document.getElementById('resume-summary-content');

        let summaryHtml = '';

        if (data.basic_info && data.basic_info.name) {
            summaryHtml += `<div class="summary-item"><span class="label">姓名:</span><span class="value">${data.basic_info.name}</span></div>`;
        }

        if (data.job_info) {
            if (data.job_info.job_intention) {
                summaryHtml += `<div class="summary-item"><span class="label">求职意向:</span><span class="value">${data.job_info.job_intention}</span></div>`;
            }
            if (data.job_info.expected_salary) {
                summaryHtml += `<div class="summary-item"><span class="label">期望薪资:</span><span class="value">${data.job_info.expected_salary}</span></div>`;
            }
        }

        if (data.background_info) {
            if (data.background_info.work_years) {
                summaryHtml += `<div class="summary-item"><span class="label">工作年限:</span><span class="value">${data.background_info.work_years}年</span></div>`;
            }
            if (data.background_info.education && data.background_info.education.length > 0) {
                const edu = data.background_info.education[0];
                summaryHtml += `<div class="summary-item"><span class="label">学历:</span><span class="value">${edu.school || ''} ${edu.major || ''}</span></div>`;
            }
            if (data.background_info.projects && data.background_info.projects.length > 0) {
                summaryHtml += `<div class="summary-item"><span class="label">项目经历:</span><span class="value">${data.background_info.projects.length}个</span></div>`;
            }
        }

        if (summaryHtml) {
            summaryContent.innerHTML = summaryHtml;
            summary.style.display = 'block';
            resultContent.style.display = 'none';
            summary.querySelector('.expand-hint').textContent = '点击展开详细信息';
        } else {
            summary.style.display = 'none';
            resultContent.style.display = 'block';
        }

        let html = '';

        if (data.basic_info) {
            html += '<div class="info-section">';
            html += '<h4>基本信息</h4>';
            if (data.basic_info.name) {
                html += `<div class="info-item"><span class="label">姓名:</span><span class="value">${data.basic_info.name}</span></div>`;
            }
            if (data.basic_info.phone) {
                html += `<div class="info-item"><span class="label">电话:</span><span class="value">${data.basic_info.phone}</span></div>`;
            }
            if (data.basic_info.email) {
                html += `<div class="info-item"><span class="label">邮箱:</span><span class="value">${data.basic_info.email}</span></div>`;
            }
            html += '</div>';
        }

        if (data.job_info) {
            html += '<div class="info-section">';
            html += '<h4>求职信息</h4>';
            if (data.job_info.job_intention) {
                html += `<div class="info-item"><span class="label">求职意向:</span><span class="value">${data.job_info.job_intention}</span></div>`;
            }
            if (data.job_info.expected_salary) {
                html += `<div class="info-item"><span class="label">期望薪资:</span><span class="value">${data.job_info.expected_salary}</span></div>`;
            }
            html += '</div>';
        }

        if (data.background_info) {
            html += '<div class="info-section">';
            html += '<h4>背景信息</h4>';
            if (data.background_info.work_years) {
                html += `<div class="info-item"><span class="label">工作年限:</span><span class="value">${data.background_info.work_years}年</span></div>`;
            }
            if (data.background_info.education && data.background_info.education.length > 0) {
                html += '<div class="info-item"><span class="label">学历背景:</span></div>';
                data.background_info.education.forEach(edu => {
                    html += `<div class="info-item" style="margin-left: 20px;">`;
                    html += `<span class="value">${edu.school || ''} - ${edu.major || ''} (${edu.degree || ''})</span>`;
                    html += '</div>';
                });
            }
            if (data.background_info.projects && data.background_info.projects.length > 0) {
                html += '<div class="info-item"><span class="label">项目经历:</span></div>';
                data.background_info.projects.forEach((proj, idx) => {
                    html += `<div class="info-item" style="margin-left: 20px;">`;
                    html += `<span class="value">${idx + 1}. ${proj.project_name || '未命名项目'}</span>`;
                    html += '</div>';
                });
            }
            html += '</div>';
        }

        if (data.skill_summary && data.skill_summary.normalized) {
            html += '<div class="info-section">';
            html += '<h4>技能标签</h4>';
            html += '<div class="skill-tags">';
            data.skill_summary.normalized.forEach(skill => {
                html += `<span class="skill-tag">${skill}</span>`;
            });
            html += '</div></div>';
        }

        resultContent.innerHTML = html;
        resultArea.style.display = 'block';
    }
};
