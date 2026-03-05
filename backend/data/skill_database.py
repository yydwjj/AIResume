import json
import os
from typing import Dict, List, Optional, Set


class SkillDatabase:
    def __init__(self, db_path: str = None):
        if db_path is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            db_path = os.path.join(current_dir, "skills.json")
        
        self.db_path = db_path
        self.skills = {}
        self.hierarchy = {}
        self.categories = {}
        self._load_database()
    
    def _load_database(self) -> None:
        if os.path.exists(self.db_path):
            with open(self.db_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.skills = data.get('skills', {})
                self.hierarchy = data.get('hierarchy', {})
                self.categories = data.get('categories', {})
        else:
            self._init_default_skills()
    
    def _init_default_skills(self) -> None:
        self.skills = {
            "python": "Python",
            "python编程": "Python",
            "python开发": "Python",
            "py": "Python",
            "python3": "Python",
            "python 3": "Python",
            
            "java": "Java",
            "java开发": "Java",
            "jdk": "Java",
            
            "javascript": "JavaScript",
            "js": "JavaScript",
            "es6": "JavaScript",
            "ecmascript": "JavaScript",
            
            "typescript": "TypeScript",
            "ts": "TypeScript",
            
            "go": "Go",
            "golang": "Go",
            "go语言": "Go",
            
            "c++": "C++",
            "cpp": "C++",
            "c plus plus": "C++",
            
            "c#": "C#",
            "csharp": "C#",
            "c sharp": "C#",
            
            "php": "PHP",
            "php开发": "PHP",
            
            "ruby": "Ruby",
            "ruby开发": "Ruby",
            
            "swift": "Swift",
            "swift开发": "Swift",
            
            "kotlin": "Kotlin",
            "kotlin开发": "Kotlin",
            
            "rust": "Rust",
            "rust开发": "Rust",
            
            "scala": "Scala",
            "scala开发": "Scala",
            
            "机器学习": "机器学习",
            "ml": "机器学习",
            "machine learning": "机器学习",
            
            "深度学习": "深度学习",
            "deep learning": "深度学习",
            "dl": "深度学习",
            "神经网络": "深度学习",
            
            "自然语言处理": "自然语言处理",
            "nlp": "自然语言处理",
            "natural language processing": "自然语言处理",
            
            "计算机视觉": "计算机视觉",
            "cv": "计算机视觉",
            "computer vision": "计算机视觉",
            
            "强化学习": "强化学习",
            "reinforcement learning": "强化学习",
            "rl": "强化学习",
            
            "数据分析": "数据分析",
            "data analysis": "数据分析",
            "数据分析": "数据分析",
            
            "数据挖掘": "数据挖掘",
            "data mining": "数据挖掘",
            
            "数据科学": "数据科学",
            "data science": "数据科学",
            
            "tensorflow": "TensorFlow",
            "tf": "TensorFlow",
            
            "pytorch": "PyTorch",
            "torch": "PyTorch",
            
            "keras": "Keras",
            
            "scikit-learn": "Scikit-learn",
            "sklearn": "Scikit-learn",
            "scikit": "Scikit-learn",
            
            "pandas": "Pandas",
            
            "numpy": "NumPy",
            
            "matplotlib": "Matplotlib",
            
            "seaborn": "Seaborn",
            
            "django": "Django",
            "django框架": "Django",
            
            "flask": "Flask",
            "flask框架": "Flask",
            
            "fastapi": "FastAPI",
            "fastapi框架": "FastAPI",
            
            "tornado": "Tornado",
            "tornado框架": "Tornado",
            
            "spring": "Spring",
            "spring框架": "Spring",
            "spring boot": "Spring Boot",
            "springboot": "Spring Boot",
            
            "mybatis": "MyBatis",
            
            "hibernate": "Hibernate",
            
            "struts": "Struts",
            
            "react": "React",
            "react.js": "React",
            "reactjs": "React",
            "react.js": "React",
            
            "vue": "Vue.js",
            "vue.js": "Vue.js",
            "vuejs": "Vue.js",
            "vue2": "Vue.js",
            "vue3": "Vue.js",
            
            "angular": "Angular",
            "angular.js": "Angular",
            "angularjs": "Angular",
            
            "node.js": "Node.js",
            "nodejs": "Node.js",
            "node": "Node.js",
            
            "express": "Express",
            "express.js": "Express",
            "expressjs": "Express",
            
            "koa": "Koa",
            "koa.js": "Koa",
            
            "next.js": "Next.js",
            "nextjs": "Next.js",
            
            "nuxt.js": "Nuxt.js",
            "nuxtjs": "Nuxt.js",
            
            "mysql": "MySQL",
            "mysql数据库": "MySQL",
            
            "postgresql": "PostgreSQL",
            "postgres": "PostgreSQL",
            "pgsql": "PostgreSQL",
            
            "mongodb": "MongoDB",
            "mongo": "MongoDB",
            
            "redis": "Redis",
            "redis缓存": "Redis",
            
            "oracle": "Oracle",
            "oracle数据库": "Oracle",
            
            "sqlserver": "SQL Server",
            "sql server": "SQL Server",
            "mssql": "SQL Server",
            
            "sqlite": "SQLite",
            
            "elasticsearch": "Elasticsearch",
            "es": "Elasticsearch",
            
            "kafka": "Kafka",
            "apache kafka": "Kafka",
            
            "rabbitmq": "RabbitMQ",
            "rabbit mq": "RabbitMQ",
            
            "rocketmq": "RocketMQ",
            "rocket mq": "RocketMQ",
            
            "docker": "Docker",
            "docker容器": "Docker",
            "容器化": "Docker",
            
            "kubernetes": "Kubernetes",
            "k8s": "Kubernetes",
            
            "jenkins": "Jenkins",
            
            "git": "Git",
            "git版本控制": "Git",
            "github": "Git",
            "gitlab": "Git",
            
            "linux": "Linux",
            "linux系统": "Linux",
            "ubuntu": "Linux",
            "centos": "Linux",
            "debian": "Linux",
            
            "nginx": "Nginx",
            
            "apache": "Apache",
            
            "tomcat": "Tomcat",
            
            "aws": "Amazon Web Services",
            "amazon web services": "Amazon Web Services",
            "amazon": "Amazon Web Services",
            
            "gcp": "Google Cloud Platform",
            "google cloud": "Google Cloud Platform",
            "google cloud platform": "Google Cloud Platform",
            
            "阿里云": "Alibaba Cloud",
            "alibaba cloud": "Alibaba Cloud",
            "aliyun": "Alibaba Cloud",
            
            "azure": "Azure",
            "microsoft azure": "Azure",
            
            "hadoop": "Hadoop",
            "apache hadoop": "Hadoop",
            
            "spark": "Spark",
            "apache spark": "Spark",
            
            "hive": "Hive",
            "apache hive": "Hive",
            
            "flink": "Flink",
            "apache flink": "Flink",
            
            "storm": "Storm",
            "apache storm": "Storm",
            
            "tableau": "Tableau",
            
            "power bi": "Power BI",
            "powerbi": "Power BI",
            
            "excel": "Excel",
            "microsoft excel": "Excel",
            
            "sql": "SQL",
            
            "html": "HTML",
            "html5": "HTML",
            
            "css": "CSS",
            "css3": "CSS",
            
            "sass": "Sass",
            "scss": "Sass",
            
            "less": "Less",
            
            "webpack": "Webpack",
            
            "vite": "Vite",
            
            "babel": "Babel",
            
            "jest": "Jest",
            
            "mocha": "Mocha",
            
            "selenium": "Selenium",
            
            "appium": "Appium",
            
            "jmeter": "JMeter",
            
            "postman": "Postman",
        }
        
        self.hierarchy = {
            "机器学习": ["深度学习", "自然语言处理", "计算机视觉", "强化学习"],
            "数据科学": ["机器学习", "数据分析", "数据挖掘"],
            "后端开发": ["Python", "Java", "Go", "Node.js", "PHP", "Ruby", "C++", "C#"],
            "前端开发": ["JavaScript", "TypeScript", "React", "Vue.js", "Angular", "HTML", "CSS"],
            "云计算": ["Amazon Web Services", "Google Cloud Platform", "Alibaba Cloud", "Azure"],
            "数据库": ["MySQL", "PostgreSQL", "MongoDB", "Redis", "Oracle", "SQL Server"],
            "大数据": ["Hadoop", "Spark", "Hive", "Flink", "Kafka"],
            "DevOps": ["Docker", "Kubernetes", "Jenkins", "Git", "Linux"],
        }
        
        self.categories = {
            "编程语言": ["Python", "Java", "JavaScript", "TypeScript", "Go", "C++", "C#", "PHP", "Ruby", "Swift", "Kotlin", "Rust", "Scala"],
            "机器学习": ["机器学习", "深度学习", "自然语言处理", "计算机视觉", "强化学习", "TensorFlow", "PyTorch", "Keras", "Scikit-learn"],
            "数据分析": ["数据分析", "数据挖掘", "数据科学", "Pandas", "NumPy", "Matplotlib", "Seaborn", "Tableau", "Power BI"],
            "Web框架": ["Django", "Flask", "FastAPI", "Spring", "Spring Boot", "React", "Vue.js", "Angular", "Express", "Koa"],
            "数据库": ["MySQL", "PostgreSQL", "MongoDB", "Redis", "Oracle", "SQL Server", "SQLite", "Elasticsearch"],
            "消息队列": ["Kafka", "RabbitMQ", "RocketMQ"],
            "DevOps": ["Docker", "Kubernetes", "Jenkins", "Git", "Linux", "Nginx"],
            "云计算": ["Amazon Web Services", "Google Cloud Platform", "Alibaba Cloud", "Azure"],
            "大数据": ["Hadoop", "Spark", "Hive", "Flink", "Storm"],
            "前端技术": ["HTML", "CSS", "JavaScript", "TypeScript", "React", "Vue.js", "Angular", "Webpack", "Vite"],
        }
        
        self._save_database()
    
    def normalize(self, skill: str) -> Optional[str]:
        if not skill:
            return None
        
        skill_lower = skill.lower().strip()
        
        if skill_lower in self.skills:
            return self.skills[skill_lower]
        
        return skill.strip().title()
    
    def add_skill_mapping(self, original: str, normalized: str) -> None:
        self.skills[original.lower()] = normalized
        self._save_database()
    
    def add_hierarchy(self, parent: str, children: List[str]) -> None:
        self.hierarchy[parent] = children
        self._save_database()
    
    def add_category(self, category: str, skills: List[str]) -> None:
        self.categories[category] = skills
        self._save_database()
    
    def expand_skills(self, skills: List[str]) -> Set[str]:
        expanded = set(skills)
        
        for skill in skills:
            for parent, children in self.hierarchy.items():
                if skill in children:
                    expanded.add(parent)
        
        return expanded
    
    def get_parent_skills(self, skill: str) -> List[str]:
        parents = []
        for parent, children in self.hierarchy.items():
            if skill in children:
                parents.append(parent)
        return parents
    
    def get_category(self, skill: str) -> Optional[str]:
        for category, skills in self.categories.items():
            if skill in skills:
                return category
        return None
    
    def get_skills_by_category(self, category: str) -> List[str]:
        return self.categories.get(category, [])
    
    def _save_database(self) -> None:
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with open(self.db_path, 'w', encoding='utf-8') as f:
            json.dump({
                'skills': self.skills,
                'hierarchy': self.hierarchy,
                'categories': self.categories
            }, f, ensure_ascii=False, indent=2)


skill_db = None

def get_skill_db() -> SkillDatabase:
    global skill_db
    if skill_db is None:
        skill_db = SkillDatabase()
    return skill_db
