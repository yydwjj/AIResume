document.addEventListener('DOMContentLoaded', () => {
    ResumeModule.init();
    JobModule.init();
    MatchModule.init();

    const resumeSelect = document.getElementById('resume-select');
    resumeSelect.addEventListener('change', async (e) => {
        if (e.target.value) {
            await ResumeModule.loadResume(e.target.value);
        }
    });

    const jobSelect = document.getElementById('job-select');
    jobSelect.addEventListener('change', async (e) => {
        if (e.target.value) {
            await JobModule.loadJob(e.target.value);
        }
    });
});
