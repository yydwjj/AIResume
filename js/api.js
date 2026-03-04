const API_BASE_URL = 'https://airesume-chfjdntfep.cn-hangzhou.fcapp.run';

const API = {
    async uploadResume(file) {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch(`${API_BASE_URL}/api/resume/upload`, {
            method: 'POST',
            body: formData
        });

        return response.json();
    },

    async parseJob(jobDescription) {
        const response = await fetch(`${API_BASE_URL}/api/job/parse`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ job_description: jobDescription })
        });

        return response.json();
    },

    async match(resumeHash, jobHash, mode) {
        const response = await fetch(`${API_BASE_URL}/api/match`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                resume_hash: resumeHash,
                job_hash: jobHash,
                mode: mode
            })
        });

        return response.json();
    },

    async getTaskStatus(taskId) {
        const response = await fetch(`${API_BASE_URL}/api/task/status/${taskId}`);
        return response.json();
    },

    async getResumeList() {
        const response = await fetch(`${API_BASE_URL}/api/resume/list`);
        return response.json();
    },

    async getJobList() {
        const response = await fetch(`${API_BASE_URL}/api/job/list`);
        return response.json();
    },

    async getResume(hash) {
        const response = await fetch(`${API_BASE_URL}/api/resume/${hash}`);
        return response.json();
    },

    async getJob(hash) {
        const response = await fetch(`${API_BASE_URL}/api/job/${hash}`);
        return response.json();
    }
};

async function pollTaskStatus(taskId, callback, interval = 2000, maxAttempts = 60) {
    let attempts = 0;

    return new Promise((resolve, reject) => {
        const poll = async () => {
            try {
                const result = await API.getTaskStatus(taskId);

                if (result.success) {
                    const task = result.data;
                    callback(task);

                    if (task.status === 'completed') {
                        resolve(task.result);
                    } else if (task.status === 'failed') {
                        reject(new Error(task.error || '任务失败'));
                    } else if (attempts >= maxAttempts) {
                        reject(new Error('任务超时'));
                    } else {
                        attempts++;
                        setTimeout(poll, interval);
                    }
                } else {
                    reject(new Error(result.error || '查询失败'));
                }
            } catch (error) {
                reject(error);
            }
        };

        poll();
    });
}

function showError(message) {
    alert(`错误: ${message}`);
}

function showSuccess(message) {
    const toast = document.createElement('div');
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #28a745;
        color: white;
        padding: 15px 25px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        z-index: 10000;
        font-size: 14px;
        animation: slideIn 0.3s ease-out;
    `;
    toast.textContent = message;
    document.body.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => {
            document.body.removeChild(toast);
        }, 300);
    }, 3000);
}

const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);
