const MatchModule = {
    init() {
        this.setupMatchButton();
        this.setupTabs();
    },

    setupMatchButton() {
        const matchBtn = document.getElementById('start-match-btn');

        matchBtn.addEventListener('click', () => this.handleMatch());
    },

    setupTabs() {
        const tabBtns = document.querySelectorAll('.tab-btn');

        tabBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                tabBtns.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');

                const tabId = btn.dataset.tab;
                document.querySelectorAll('.tab-content').forEach(content => {
                    content.classList.remove('active');
                });
                document.getElementById(`${tabId}-tab`).classList.add('active');
            });
        });
    },

    async handleMatch() {
        const resumeHash = document.getElementById('resume-select').value;
        const jobHash = document.getElementById('job-select').value;
        const mode = document.getElementById('match-mode').value;

        if (!resumeHash) {
            showError('请选择简历');
            return;
        }

        if (!jobHash) {
            showError('请选择岗位');
            return;
        }

        const progressArea = document.getElementById('match-progress');
        const resultSection = document.getElementById('result-section');
        const matchBtn = document.getElementById('start-match-btn');
        const statusText = document.querySelector('#match-progress .status-text');

        matchBtn.disabled = true;
        progressArea.style.display = 'block';
        resultSection.style.display = 'none';
        statusText.textContent = '正在匹配中...';

        try {
            const response = await API.match(resumeHash, jobHash, mode);

            if (response.success) {
                if (response.cached) {
                    statusText.textContent = '使用缓存，加载匹配结果...';
                    this.displayMatchResult(response.data);
                    showSuccess('匹配完成（使用缓存）');
                } else {
                    await pollTaskStatus(response.task_id, (task) => {
                        this.updateProgress(task.progress, task.stage);
                    });

                    const taskResult = await API.getTaskStatus(response.task_id);
                    if (taskResult.success && taskResult.data.result) {
                        this.displayMatchResult(taskResult.data.result);
                        showSuccess('匹配完成');
                    }
                }
            } else {
                throw new Error(response.error || '匹配失败');
            }
        } catch (error) {
            showError(error.message);
        } finally {
            matchBtn.disabled = false;
            progressArea.style.display = 'none';
        }
    },

    updateProgress(progress, stage) {
        const progressBar = document.getElementById('match-progress-bar');
        const statusText = document.querySelector('#match-progress .status-text');

        progressBar.style.width = `${progress}%`;
        statusText.textContent = stage || '处理中...';
    },

    displayMatchResult(data) {
        const resultSection = document.getElementById('result-section');
        const scoreValue = document.getElementById('score-value');
        const recommendation = document.getElementById('recommendation');
        const ruleResultContent = document.getElementById('rule-result-content');
        const semanticResultContent = document.getElementById('semantic-result-content');

        scoreValue.textContent = data.final_score || 0;
        recommendation.textContent = data.recommendation || '';

        this.displayRuleResult(data.rule_based, ruleResultContent);

        if (data.semantic) {
            this.displaySemanticResult(data.semantic, semanticResultContent);
        } else {
            semanticResultContent.innerHTML = '<p>快速匹配模式不包含语义分析</p>';
        }

        resultSection.style.display = 'block';
        resultSection.scrollIntoView({ behavior: 'smooth' });
    },

    displayRuleResult(data, container) {
        if (!data) {
            container.innerHTML = '<p>无规则匹配结果</p>';
            return;
        }

        let html = '';

        html += `<div class="info-item"><span class="label">匹配得分:</span><span class="value">${data.match_score}</span></div>`;
        html += `<div class="info-item"><span class="label">技能匹配率:</span><span class="value">${(data.skill_match_rate * 100).toFixed(0)}%</span></div>`;
        html += `<div class="info-item"><span class="label">经验匹配:</span><span class="value">${data.experience_match ? '✓ 符合' : '✗ 不符合'}</span></div>`;
        html += `<div class="info-item"><span class="label">学历匹配:</span><span class="value">${data.education_match ? '✓ 符合' : '✗ 不符合'}</span></div>`;

        if (data.matched_required_skills && data.matched_required_skills.length > 0) {
            html += '<div class="info-section">';
            html += '<h4>匹配的技能</h4>';
            html += '<div class="skill-tags">';
            data.matched_required_skills.forEach(skill => {
                html += `<span class="skill-tag matched">${skill}</span>`;
            });
            html += '</div></div>';
        }

        if (data.missing_required_skills && data.missing_required_skills.length > 0) {
            html += '<div class="info-section">';
            html += '<h4>缺失的技能</h4>';
            html += '<div class="skill-tags">';
            data.missing_required_skills.forEach(skill => {
                html += `<span class="skill-tag missing">${skill}</span>`;
            });
            html += '</div></div>';
        }

        container.innerHTML = html;
    },

    displaySemanticResult(data, container) {
        if (!data) {
            container.innerHTML = '<p>无语义匹配结果</p>';
            return;
        }

        let html = '';

        if (data.dimensions) {
            html += '<div class="dimensions">';
            for (const [key, dimension] of Object.entries(data.dimensions)) {
                html += `<div class="dimension-item">`;
                html += `<h4>${this.getDimensionName(key)}</h4>`;
                if (dimension.score !== undefined && dimension.max_score !== undefined) {
                    html += `<div class="score">${dimension.score}/${dimension.max_score}</div>`;
                } else if (dimension.score !== undefined) {
                    html += `<div class="score">${dimension.score}</div>`;
                }
                if (dimension.reason) {
                    html += `<div class="reason">${dimension.reason}</div>`;
                }
                html += '</div>';
            }
            html += '</div>';
        }

        if (data.analysis) {
            html += `<div class="info-section"><h4>综合分析</h4><p>${data.analysis}</p></div>`;
        }

        if (data.strengths || data.weaknesses) {
            html += '<div class="strengths-weaknesses">';

            if (data.strengths && data.strengths.length > 0) {
                html += '<div class="strengths">';
                html += '<h4>优势</h4>';
                html += '<ul>';
                data.strengths.forEach(s => {
                    html += `<li>${s}</li>`;
                });
                html += '</ul></div>';
            }

            if (data.weaknesses && data.weaknesses.length > 0) {
                html += '<div class="weaknesses">';
                html += '<h4>不足</h4>';
                html += '<ul>';
                data.weaknesses.forEach(w => {
                    html += `<li>${w}</li>`;
                });
                html += '</ul></div>';
            }

            html += '</div>';
        }

        container.innerHTML = html;
    },

    getDimensionName(key) {
        const names = {
            'capability_match': '能力匹配度',
            'experience_relevance': '经验相关性',
            'potential': '潜力评估',
            'comprehensive_quality': '综合素质',
            'project_relevance': '项目相关性',
            'role_match': '角色匹配度',
            'experience_depth': '经验深度',
            'achievement': '成果体现'
        };
        return names[key] || key;
    }
};
