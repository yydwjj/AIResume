RESUME_EXTRACTION_PROMPT = """请从以下简历文本中提取关键信息，并以JSON格式返回。

简历文本：
{resume_text}

请提取以下信息：

1. 基本信息（必填）：
   - name: 姓名
   - phone: 电话
   - email: 邮箱
   - address: 地址

2. 求职信息（可选）：
   - job_intention: 求职意向
   - expected_salary: 期望薪资（格式：数字+K，如"15-20K"）

3. 背景信息（可选）：
   - work_years: 工作年限（数字，如"3年"返回3）
   - education: 教育经历数组，每个元素包含：
     - school: 学校名称
     - degree: 学历（本科/硕士/博士等）
     - major: 专业
     - start_date: 开始时间（格式：YYYY-MM）
     - end_date: 结束时间（格式：YYYY-MM）
   - work_experience: 工作经历数组，每个元素包含：
     - company: 公司名称
     - position: 职位
     - description: 工作描述
     - start_date: 开始时间（格式：YYYY-MM）
     - end_date: 结束时间（格式：YYYY-MM）
   - projects: 项目经历数组，每个元素包含：
     - project_name: 项目名称
     - role: 担任角色
     - description: 项目描述
     - start_date: 开始时间（格式：YYYY-MM）
     - end_date: 结束时间（格式：YYYY-MM）
     - technologies: 使用的技术栈（数组）

4. 技能信息（重要）：
   请从简历中提取所有技术技能，并按照以下格式返回：
   - skills: 技能数组，每个技能包含：
     - name: 技能名称（使用标准名称，如"Python"而非"Python编程"）
     - category: 技能分类（编程语言/框架/数据库/工具/云服务等）
     - proficiency: 熟练度（入门/熟练/精通/专家）
     - usage_years: 使用年限（数字，如2）
     - source: 来源（项目经历/技能章节/工作经历）

返回JSON格式示例：
{{
    "basic_info": {{
        "name": "张三",
        "phone": "13800138000",
        "email": "zhangsan@example.com",
        "address": "北京市朝阳区"
    }},
    "job_info": {{
        "job_intention": "数据分析师",
        "expected_salary": "15-20K"
    }},
    "background_info": {{
        "work_years": 3,
        "education": [
            {{
                "school": "北京大学",
                "degree": "本科",
                "major": "计算机科学与技术",
                "start_date": "2016-09",
                "end_date": "2020-06"
            }}
        ],
        "work_experience": [
            {{
                "company": "某科技公司",
                "position": "数据分析师",
                "description": "负责数据分析工作",
                "start_date": "2020-07",
                "end_date": "2023-12"
            }}
        ],
        "projects": [
            {{
                "project_name": "数据分析平台",
                "role": "核心开发",
                "description": "负责数据采集、清洗、分析模块开发",
                "start_date": "2021-01",
                "end_date": "2022-12",
                "technologies": ["Python", "Pandas", "MySQL"]
            }}
        ]
    }},
    "skills": [
        {{
            "name": "Python",
            "category": "编程语言",
            "proficiency": "精通",
            "usage_years": 3,
            "source": "项目经历"
        }},
        {{
            "name": "机器学习",
            "category": "技术领域",
            "proficiency": "熟练",
            "usage_years": 2,
            "source": "项目经历"
        }}
    ]
}}

注意事项：
1. 技能名称请使用标准名称（如"Python"而非"Python编程"）
2. 如果技能有多个名称（如"深度学习"和"机器学习"），请使用更通用的名称
3. 熟练度请根据简历描述判断，不要凭空猜测
4. 无法提取的信息使用null
5. education、work_experience、projects必须是数组，即使只有一项
6. 日期格式统一为YYYY-MM
7. 不要编造信息，无法提取就返回null

请只返回JSON，不要包含其他解释文字。
"""

JOB_PARSE_PROMPT = """请分析以下岗位需求描述，提取关键信息。

岗位描述：
{job_description}

请以JSON格式返回：

{{
    "job_title": "岗位名称",
    "required_skills": [
        {{
            "name": "技能名称（使用标准名称）",
            "category": "技能分类",
            "importance": "必须/加分",
            "level": "入门/熟练/精通"
        }}
    ],
    "experience_years": {{
        "min": 3,
        "max": 5,
        "description": "3-5年"
    }},
    "education_level": {{
        "required": "本科",
        "preferred": "硕士"
    }},
    "responsibilities": ["职责1", "职责2"],
    "keywords": ["关键词1", "关键词2"],
    "skill_categories": {{
        "编程语言": ["Python", "Java"],
        "框架": ["Django", "Spring"],
        "数据库": ["MySQL", "Redis"],
        "工具": ["Git", "Docker"]
    }}
}}

注意事项：
1. 技能名称请使用标准名称（如"Python"而非"Python编程"）
2. 区分"必须"和"加分"技能
3. 工作年限返回数字范围，如果描述是"3年以上"，则min为3，max为null
4. 如果某项信息无法提取，使用null
5. required_skills必须是数组
6. responsibilities和keywords必须是数组

请只返回JSON，不要包含其他解释文字。
"""

SEMANTIC_MATCH_PROMPT = """请对以下简历与岗位进行深度语义匹配分析，并给出综合评分（0-100）。

候选人信息：
姓名：{name}
工作年限：{work_years}年
学历：{education}
技能：{skills}

项目经历：
{projects}

目标岗位：
岗位名称：{job_title}
岗位职责：
{responsibilities}
技能要求：{required_skills}

请从以下维度进行深度分析：

1. 能力匹配度（30分）：
   - 技能深度是否满足岗位需求
   - 技能广度是否覆盖岗位要求
   - 技能熟练度是否达标

2. 经验相关性（30分）：
   - 项目经历与岗位的匹配度
   - 工作经验是否相关
   - 是否有解决类似问题的经验

3. 潜力评估（20分）：
   - 学习能力和适应性
   - 成长空间
   - 是否有创新思维

4. 综合素质（20分）：
   - 沟通能力（从项目描述中推断）
   - 团队协作能力
   - 责任心和主动性

请返回JSON格式：
{{
    "overall_score": 82,
    "dimensions": {{
        "capability_match": {{
            "score": 25,
            "max_score": 30,
            "reason": "技能深度较好，但部分高级技能经验不足"
        }},
        "experience_relevance": {{
            "score": 26,
            "max_score": 30,
            "reason": "项目经历高度相关，有类似经验"
        }},
        "potential": {{
            "score": 16,
            "max_score": 20,
            "reason": "学习能力强，有良好成长潜力"
        }},
        "comprehensive_quality": {{
            "score": 15,
            "max_score": 20,
            "reason": "综合素质良好，但领导经验较少"
        }}
    }},
    "analysis": "该候选人与岗位匹配度较高...",
    "strengths": [
        "项目经验丰富，技术栈匹配",
        "有解决复杂问题的能力",
        "学习能力强，成长性好"
    ],
    "weaknesses": [
        "部分高级技能经验不足",
        "团队领导经验较少",
        "量化成果不够详细"
    ],
    "recommendation": "建议录用",
    "risk_factors": ["风险因素1", "风险因素2"]
}}

评分标准：
- 90-100分：高度匹配，强烈推荐
- 80-89分：匹配度较高，推荐录用
- 70-79分：基本匹配，可以考虑
- 60-69分：部分匹配，需要进一步评估
- 60分以下：匹配度较低，不建议录用

请只返回JSON，不要包含其他解释文字。
"""

PROJECT_RELEVANCE_PROMPT = """请分析以下简历中的项目经历与目标岗位的相关性。

目标岗位：
岗位名称：{job_title}
岗位职责：
{job_description}

简历中的项目经历：
{projects_text}

请从以下维度进行分析：

1. 项目相关性（0-100分）：
   - 项目类型与岗位的匹配度
   - 项目规模和复杂度是否符合要求
   - 项目中使用的技术栈是否相关

2. 角色匹配度（0-100分）：
   - 在项目中担任的角色是否符合岗位要求
   - 职责范围是否匹配

3. 经验深度（0-100分）：
   - 项目经历是否体现了足够的深度
   - 是否有解决复杂问题的经验

4. 成果体现（0-100分）：
   - 项目描述中是否体现了具体成果
   - 是否有量化的成就

请返回JSON格式：
{{
    "overall_score": 85,
    "dimensions": {{
        "project_relevance": {{
            "score": 90,
            "reason": "项目类型与岗位高度匹配，技术栈相关"
        }},
        "role_match": {{
            "score": 80,
            "reason": "角色职责基本匹配，但领导经验较少"
        }},
        "experience_depth": {{
            "score": 85,
            "reason": "项目经验丰富，有解决复杂问题的能力"
        }},
        "achievement": {{
            "score": 75,
            "reason": "有部分量化成果，但不够详细"
        }}
    }},
    "analysis": "该候选人的项目经历与岗位需求高度相关...",
    "strengths": ["优势1", "优势2"],
    "weaknesses": ["不足1", "不足2"],
    "recommendation": "建议"
}}

请只返回JSON，不要包含其他解释文字。
"""

SKILL_NORMALIZATION_PROMPT = """请将以下技能名称标准化为最通用的名称。

原始技能名称: {skill_name}

要求:
1. 返回最通用、最标准的技能名称
2. 如果是缩写，返回全称（如"ML" -> "机器学习"）
3. 如果有多个名称，选择最常用的
4. 只返回标准化后的名称，不要解释

示例:
- "Python编程" -> "Python"
- "深度学习" -> "深度学习"
- "ML" -> "机器学习"
- "React.js" -> "React"

请只返回标准化后的技能名称，不要包含其他解释文字。
"""
