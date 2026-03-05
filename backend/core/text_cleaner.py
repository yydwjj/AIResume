import re
from typing import Dict, List


class TextCleaner:
    def __init__(self):
        self.section_patterns = {
            'basic_info': r'(个人信息|基本资料|个人简介|联系方式)',
            'education': r'(教育经历|学历背景|教育背景|求学经历)',
            'work_experience': r'(工作经历|工作履历|职业经历|工作背景)',
            'project_experience': r'(项目经历|项目经验|项目背景)',
            'skills': r'(专业技能|技能特长|技术能力|技能清单)',
            'self_evaluation': r'(自我评价|个人总结|个人优势)',
            'internship': r'(实习经历|实习经验)',
            'certificates': r'(证书|资格证书|荣誉奖项)',
        }
    
    def clean(self, text: str) -> str:
        """
        清洗简历文本
        """
        if not text:
            return ""
        
        text = self._remove_control_chars(text)
        text = self._normalize_whitespace(text)
        text = self._fix_broken_lines(text)
        text = self._remove_page_numbers(text)
        text = self._remove_headers_footers(text)
        
        return text.strip()
    
    def _remove_control_chars(self, text: str) -> str:
        """
        去除特殊控制字符
        """
        text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]', '', text)
        return text
    
    def _normalize_whitespace(self, text: str) -> str:
        """
        规范化空白字符
        """
        text = re.sub(r'[ \t]+', ' ', text)
        text = re.sub(r'\n\s*\n', '\n\n', text)
        return text
    
    def _fix_broken_lines(self, text: str) -> str:
        """
        修复断行问题
        """
        text = re.sub(r'([一-龯])\n([一-龯])', r'\1\2', text)
        text = re.sub(r'([a-zA-Z])\n([a-zA-Z])', r'\1\2', text)
        return text
    
    def _remove_page_numbers(self, text: str) -> str:
        """
        去除页码
        """
        text = re.sub(r'第\s*\d+\s*页\s*/\s*\d+', '', text)
        text = re.sub(r'Page\s*\d+\s*/\s*\d+', '', text, flags=re.IGNORECASE)
        text = re.sub(r'-\s*\d+\s*-', '', text)
        return text
    
    def _remove_headers_footers(self, text: str) -> str:
        """
        去除页眉页脚
        """
        text = re.sub(r'简历|个人简历|RESUME|Curriculum Vitae', '', text, flags=re.IGNORECASE)
        return text
    
    def structure(self, text: str) -> Dict[str, str]:
        """
        将文本按章节结构化
        """
        sections = {'other': []}
        current_section = 'other'
        
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            matched_section = self._detect_section(line)
            
            if matched_section:
                current_section = matched_section
                if current_section not in sections:
                    sections[current_section] = []
            else:
                if current_section not in sections:
                    sections[current_section] = []
                sections[current_section].append(line)
        
        for key in sections:
            sections[key] = '\n'.join(sections[key])
        
        return sections
    
    def _detect_section(self, line: str) -> str:
        """
        检测行是否为章节标题
        """
        for section_name, pattern in self.section_patterns.items():
            if re.search(pattern, line, re.IGNORECASE):
                return section_name
        return None
    
    def extract_sentences(self, text: str) -> List[str]:
        """
        提取句子
        """
        sentences = re.split(r'[。！？\n]', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def remove_duplicates(self, text: str) -> str:
        """
        去除重复内容
        """
        lines = text.split('\n')
        seen = set()
        unique_lines = []
        
        for line in lines:
            line = line.strip()
            if line and line not in seen:
                seen.add(line)
                unique_lines.append(line)
        
        return '\n'.join(unique_lines)
    
    def clean_and_structure(self, text: str) -> Dict:
        """
        清洗并结构化文本
        """
        cleaned_text = self.clean(text)
        structured_text = self.structure(cleaned_text)
        
        return {
            'raw_text': text,
            'cleaned_text': cleaned_text,
            'structured_text': structured_text
        }


text_cleaner = TextCleaner()

def get_text_cleaner() -> TextCleaner:
    return text_cleaner
