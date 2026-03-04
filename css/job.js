const JobModule = {
    jobList: [],
    currentJob: null,
    
    init() {
        this.setupParseButton();
        this.loadJobList();
    },
    
    setupParseButton() {
        const parseBtn = document.getElementById('parse-job-btn');
        
        parseBtn.addEventListener('click', () => this.handleParseJob());
    },
    
    async handleParseJob() {
        const jobDescription = document.getElementById('job-description').value.trim();
        
        if (!jobDescription) {
            showError('请输入岗位描述');
            return;
        }
        
        const progressArea = document.getElementById('job-progress');
        const resultArea = document.getElementById('job-result');
        const parseBtn = document.getElementById('parse-job-btn');
        
        parseBtn.disabled = true;
        progressArea.style.display = 'block';
        resultArea.style.display = 'none';
        
        try {
            const response = await API.parseJob(jobDescription);
            
            if (response.success) {
                this.currentJob = response.data;
                this.displayJobResult(response.data);
                
                await this.loadJobList();
                
                const jobSelect = document.getElementById('job-select');
                jobSelect.value = response.data.job_hash;
                
                showSuccess('岗位解析完成');
            } else {
                throw new Error(response.error || '解析失败');
            }
        } catch (error) {
            showError(error.message);
        } finally {
            parseBtn.disabled = false;
            progressArea.style.display = 'none';
        }
    },
    
    async loadJobList() {
        try {
            const response = await API.getJobList();
            
            if (response.success) {
                this.jobList = response.data.jobs || [];
                this.updateJobSelect();
            }
        } catch (error) {
            console.error('加载岗位列表失败:', error);
        }
    },
    
    updateJobSelect() {
        const select = document.getElementById('job-select');
        
        select.innerHTML = '<option value="">请选择岗位</option>';
        
        this.jobList.forEach(job => {
            const option = document.createElement('option');
            option.value = job.hash;
            option.textContent = job.title || `岗位 ${job.hash.substring(0, 8)}`;
            select.appendChild(option);
        });
    },
    
    async loadJob(hash) {
        try {
            const response = await API.getJob(hash);
            
            if (response.success) {
                this.currentJob = response.data;
                this.displayJobResult(response.data);
                return response.data;
            }
        } catch (error) {
            console.error('加载岗位失败:', error);
        }
    },
    
    displayJobResult(data) {
        const resultArea = document.getElementById('job-result');
        const resultContent = document.getElementById('job-result-content');
        
        let html = '';
        
        if (data.job_title) {
            html += `<div class="info-item"><span class="label">岗位名称:</span><span class="value">${data.job_title}</span></div>`;
        }
        
        if (data.experience_years) {
            const exp = data.experience_years;
            let expText = '';
            if (exp.min && exp.max) {
                expText = `${exp.min}-${exp.max}年`;
            } else if (exp.min) {
                expText = `${exp.min}年以上`;
            }
            if (expText) {
                html += `<div class="info-item"><span class="label">经验要求:</span><span class="value">${expText}</span></div>`;
            }
        }
        
        if (data.education_level && data.education_level.required) {
            html += `<div class="info-item"><span class="label">学历要求:</span><span class="value">${data.education_level.required}</span></div>`;
        }
        
        if (data.required_skills && data.required_skills.length > 0) {
            html += '<div class="info-section">';
            html += '<h4>技能要求</h4>';
            html += '<div class="skill-tags">';
            data.required_skills.forEach(skill => {
                const className = skill.importance === '必须' ? 'skill-tag' : 'skill-tag" style="background: #6c757d';
                html += `<span class="${className}">${skill.name}</span>`;
            });
            html += '</div></div>';
        }
        
        if (data.responsibilities && data.responsibilities.length > 0) {
            html += '<div class="info-section">';
            html += '<h4>岗位职责</h4>';
            html += '<ul>';
            data.responsibilities.forEach(resp => {
                html += `<li>${resp}</li>`;
            });
            html += '</ul></div>';
        }
        
        resultContent.innerHTML = html;
        resultArea.style.display = 'block';
    }
};
