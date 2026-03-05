# AI Resume API 文档

## 目录

- [基本信息](#基本信息)
- [API 端点列表](#api-端点列表)
  - [1. 健康检查](#1-健康检查)
  - [2. 上传简历](#2-上传简历)
  - [3. 解析岗位描述](#3-解析岗位描述)
  - [4. 获取简历列表](#4-获取简历列表)
  - [5. 获取简历详情](#5-获取简历详情)
  - [6. 获取岗位列表](#6-获取岗位列表)
  - [7. 获取岗位详情](#7-获取岗位详情)
  - [8. 简历岗位匹配](#8-简历岗位匹配)
  - [9. 查询任务状态](#9-查询任务状态)
- [任务状态说明](#任务状态说明)
- [错误码说明](#错误码说明)
- [使用示例](#使用示例)
- [注意事项](#注意事项)
- [数据结构参考](#数据结构参考)
  - [通用响应结构](#通用响应结构)
  - [简历数据结构](#简历数据结构)
  - [岗位数据结构](#岗位数据结构)
  - [匹配结果数据结构](#匹配结果数据结构)
  - [任务数据结构](#任务数据结构)
  - [数据类型说明](#数据类型说明)
  - [枚举值说明](#枚举值说明)

---

## 基本信息

- **基础URL**: `https://your-function-url.cn-hangzhou.fcapp.run`
- **数据格式**: JSON
- **编码**: UTF-8
- **CORS**: 已启用，支持跨域请求

---

## API 端点列表

| 端点 | 方法 | 描述 |
|------|------|------|
| `/` | GET | 健康检查 / 获取数据列表 |
| `/api/resume/upload` | POST | 上传简历 |
| `/api/resume/parse` | POST | 解析简历（内部调用） |
| `/api/resume/list` | GET | 获取简历列表 |
| `/api/resume/<hash>` | GET | 获取简历详情 |
| `/api/job/parse` | POST | 解析岗位描述 |
| `/api/job/list` | GET | 获取岗位列表 |
| `/api/job/<hash>` | GET | 获取岗位详情 |
| `/api/match` | POST | 简历岗位匹配 |
| `/api/task/status/<task_id>` | GET | 查询任务状态 |

---

## 1. 健康检查

### 请求

```
GET /
```

### 响应

```json
{
  "success": true,
  "data": {
    "resumes": [
      {
        "hash": "string",
        "name": "string",
        "parse_time": "string"
      }
    ],
    "jobs": [
      {
        "hash": "string",
        "title": "string"
      }
    ]
  }
}
```

### 数据结构说明

**响应参数**：

| 参数 | 类型 | 说明 |
|------|------|------|
| success | boolean | 请求是否成功 |
| data | object | 数据列表 |
| data.resumes | array | 简历列表 |
| data.resumes[].hash | string | 简历哈希值 |
| data.resumes[].name | string | 求职者姓名 |
| data.resumes[].parse_time | string | 解析时间 |
| data.jobs | array | 岗位列表 |
| data.jobs[].hash | string | 岗位哈希值 |
| data.jobs[].title | string | 岗位名称 |

---

## 2. 上传简历

### 请求

```
POST /api/resume/upload
Content-Type: application/json
```

### 请求体

```json
{
  "file": "<base64编码的PDF文件内容>",
  "filename": "resume.pdf"
}
```

### 响应

```json
{
  "success": true,
  "task_id": "task_abc123",
  "file_hash": "abc123def456...",
  "message": "简历上传成功，正在解析中"
}
```

### 数据结构说明

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| file | string | 是 | PDF文件的base64编码 |
| filename | string | 是 | 文件名（必须以.pdf结尾） |

**响应参数**：

| 参数 | 类型 | 说明 |
|------|------|------|
| success | boolean | 请求是否成功 |
| task_id | string | 任务ID，用于查询解析状态 |
| file_hash | string | 文件哈希值，用于标识简历 |
| message | string | 提示信息 |

### 错误响应

```json
{
  "success": false,
  "error": "错误信息"
}
```

---

## 3. 解析岗位描述

### 请求

```
POST /api/job/parse
Content-Type: application/json
```

### 请求体

```json
{
  "job_description": "岗位名称: Java开发工程师\n工作职责: ...\n任职要求: ..."
}
```

### 响应

```json
{
  "success": true,
  "data": {
    "job_hash": "string",
    "job_title": "string",
    "experience_years": {
      "min": "number",
      "max": "number",
      "description": "string"
    },
    "education_level": {
      "required": "string",
      "preferred": "string"
    },
    "required_skills": [
      {
        "name": "string",
        "importance": "string",
        "proficiency": "string"
      }
    ],
    "responsibilities": ["string"],
    "keywords": ["string"],
    "skill_summary": {
      "normalized": ["string"],
      "expanded": ["string"]
    },
    "original_description": "string"
  },
  "cached": "boolean"
}
```

### 数据结构说明

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| job_description | string | 是 | 岗位描述文本 |

**响应参数**：

| 参数 | 类型 | 说明 |
|------|------|------|
| success | boolean | 请求是否成功 |
| data | object | 解析结果数据 |
| cached | boolean | 是否使用缓存 |

**data数据结构**：

| 字段 | 类型 | 说明 |
|------|------|------|
| job_hash | string | 岗位哈希值 |
| job_title | string | 岗位名称 |
| experience_years | object | 工作年限要求 |
| experience_years.min | number | 最低年限 |
| experience_years.max | number | 最高年限 |
| experience_years.description | string | 年限描述 |
| education_level | object | 学历要求 |
| education_level.required | string | 必需学历 |
| education_level.preferred | string | 优先学历 |
| required_skills | array | 必需技能列表 |
| required_skills[].name | string | 技能名称 |
| required_skills[].importance | string | 重要性（必须/加分） |
| required_skills[].proficiency | string | 熟练度要求 |
| responsibilities | array | 工作职责列表 |
| keywords | array | 关键词列表 |
| skill_summary | object | 技能摘要 |
| skill_summary.normalized | array | 标准化技能列表 |
| skill_summary.expanded | array | 扩展技能列表 |
| original_description | string | 原始岗位描述 |

---

## 4. 获取简历列表

### 请求

```
GET /api/resume/list
```

### 响应

```json
{
  "success": true,
  "data": {
    "resumes": [
      {
        "hash": "string",
        "name": "string",
        "parse_time": "string"
      }
    ]
  }
}
```

### 数据结构说明

**响应参数**：

| 参数 | 类型 | 说明 |
|------|------|------|
| success | boolean | 请求是否成功 |
| data | object | 简历列表数据 |
| data.resumes | array | 简历列表 |
| data.resumes[].hash | string | 简历哈希值 |
| data.resumes[].name | string | 求职者姓名 |
| data.resumes[].parse_time | string | 解析时间 |

---

## 5. 获取简历详情

### 请求

```
GET /api/resume/<hash>
```

### 路径参数

| 参数 | 类型 | 描述 |
|------|------|------|
| hash | string | 简历哈希值 |

### 响应

```json
{
  "success": true,
  "data": {
    "resume_hash": "string",
    "metadata": {
      "page_count": "number",
      "parse_time": "string"
    },
    "basic_info": {
      "name": "string",
      "phone": "string",
      "email": "string",
      "location": "string"
    },
    "job_info": {
      "current_company": "string",
      "current_position": "string",
      "job_intention": "string",
      "expected_salary": "string"
    },
    "background_info": {
      "work_years": "number",
      "education": [
        {
          "school": "string",
          "degree": "string",
          "major": "string",
          "graduation_year": "number",
          "start_date": "string",
          "end_date": "string"
        }
      ],
      "work_experience": [
        {
          "company": "string",
          "position": "string",
          "start_date": "string",
          "end_date": "string",
          "description": "string"
        }
      ],
      "projects": [
        {
          "project_name": "string",
          "role": "string",
          "description": "string",
          "technologies": ["string"],
          "start_date": "string",
          "end_date": "string"
        }
      ]
    },
    "skills": [
      {
        "name": "string",
        "category": "string",
        "proficiency": "string",
        "usage_years": "number",
        "source": "string"
      }
    ],
    "skill_summary": {
      "normalized": ["string"],
      "expanded": ["string"]
    }
  }
}
```

### 数据结构说明

**响应参数**：

| 参数 | 类型 | 说明 |
|------|------|------|
| success | boolean | 请求是否成功 |
| data | object | 简历详情数据 |

**data数据结构**：

| 字段 | 类型 | 说明 |
|------|------|------|
| resume_hash | string | 简历哈希值 |
| metadata | object | 元数据 |
| metadata.page_count | number | PDF页数 |
| metadata.parse_time | string | 解析时间 |
| basic_info | object | 基本信息 |
| basic_info.name | string | 姓名 |
| basic_info.phone | string | 电话 |
| basic_info.email | string | 邮箱 |
| basic_info.location | string | 地址 |
| job_info | object | 求职信息 |
| job_info.current_company | string | 当前公司 |
| job_info.current_position | string | 当前职位 |
| job_info.job_intention | string | 求职意向 |
| job_info.expected_salary | string | 期望薪资 |
| background_info | object | 背景信息 |
| background_info.work_years | number | 工作年限 |
| background_info.education | array | 教育经历列表 |
| background_info.education[].school | string | 学校名称 |
| background_info.education[].degree | string | 学位 |
| background_info.education[].major | string | 专业 |
| background_info.education[].graduation_year | number | 毕业年份 |
| background_info.education[].start_date | string | 入学时间 |
| background_info.education[].end_date | string | 毕业时间 |
| background_info.work_experience | array | 工作经历列表 |
| background_info.work_experience[].company | string | 公司名称 |
| background_info.work_experience[].position | string | 职位 |
| background_info.work_experience[].start_date | string | 入职时间 |
| background_info.work_experience[].end_date | string | 离职时间 |
| background_info.work_experience[].description | string | 工作描述 |
| background_info.projects | array | 项目经历列表 |
| background_info.projects[].project_name | string | 项目名称 |
| background_info.projects[].role | string | 担任角色 |
| background_info.projects[].description | string | 项目描述 |
| background_info.projects[].technologies | array | 使用技术 |
| background_info.projects[].start_date | string | 开始时间 |
| background_info.projects[].end_date | string | 结束时间 |
| skills | array | 技能列表 |
| skills[].name | string | 技能名称 |
| skills[].category | string | 技能分类 |
| skills[].proficiency | string | 熟练度 |
| skills[].usage_years | number | 使用年限 |
| skills[].source | string | 来源（提取/推断/扩展） |
| skill_summary | object | 技能摘要 |
| skill_summary.normalized | array | 标准化技能列表 |
| skill_summary.expanded | array | 扩展技能列表 |

---

## 6. 获取岗位列表

### 请求

```
GET /api/job/list
```

### 响应

```json
{
  "success": true,
  "data": {
    "jobs": [
      {
        "hash": "string",
        "title": "string"
      }
    ]
  }
}
```

### 数据结构说明

**响应参数**：

| 参数 | 类型 | 说明 |
|------|------|------|
| success | boolean | 请求是否成功 |
| data | object | 岗位列表数据 |
| data.jobs | array | 岗位列表 |
| data.jobs[].hash | string | 岗位哈希值 |
| data.jobs[].title | string | 岗位名称 |

---

## 7. 获取岗位详情

### 请求

```
GET /api/job/<hash>
```

### 路径参数

| 参数 | 类型 | 描述 |
|------|------|------|
| hash | string | 岗位哈希值 |

### 响应

```json
{
  "success": true,
  "data": {
    "job_hash": "string",
    "job_title": "string",
    "experience_years": {
      "min": "number",
      "max": "number",
      "description": "string"
    },
    "education_level": {
      "required": "string",
      "preferred": "string"
    },
    "required_skills": [
      {
        "name": "string",
        "importance": "string",
        "proficiency": "string"
      }
    ],
    "responsibilities": ["string"],
    "keywords": ["string"],
    "skill_summary": {
      "normalized": ["string"],
      "expanded": ["string"]
    },
    "original_description": "string"
  }
}
```

### 数据结构说明

**响应参数**：

| 参数 | 类型 | 说明 |
|------|------|------|
| success | boolean | 请求是否成功 |
| data | object | 岗位详情数据 |

**data数据结构**：

| 字段 | 类型 | 说明 |
|------|------|------|
| job_hash | string | 岗位哈希值 |
| job_title | string | 岗位名称 |
| experience_years | object | 工作年限要求 |
| experience_years.min | number | 最低年限 |
| experience_years.max | number | 最高年限 |
| experience_years.description | string | 年限描述 |
| education_level | object | 学历要求 |
| education_level.required | string | 必需学历 |
| education_level.preferred | string | 优先学历 |
| required_skills | array | 必需技能列表 |
| required_skills[].name | string | 技能名称 |
| required_skills[].importance | string | 重要性（必须/加分） |
| required_skills[].proficiency | string | 熟练度要求 |
| responsibilities | array | 工作职责列表 |
| keywords | array | 关键词列表 |
| skill_summary | object | 技能摘要 |
| skill_summary.normalized | array | 标准化技能列表 |
| skill_summary.expanded | array | 扩展技能列表 |
| original_description | string | 原始岗位描述 |

---

## 8. 简历岗位匹配

### 请求

```
POST /api/match
Content-Type: application/json
```

### 请求体

```json
{
  "resume_hash": "string",
  "job_hash": "string",
  "mode": "string"
}
```

### 参数说明

| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| resume_hash | string | 是 | 简历哈希值 |
| job_hash | string | 是 | 岗位哈希值 |
| mode | string | 否 | 匹配模式：`fast`（快速）、`standard`（标准）、`deep`（深度），默认`standard` |

### 响应（异步任务）

```json
{
  "success": true,
  "task_id": "string"
}
```

### 响应（缓存结果）

```json
{
  "success": true,
  "data": {
    "match_score": "number",
    "skill_match_rate": "number",
    "experience_match": "string",
    "education_match": "string",
    "matched_required_skills": ["string"],
    "matched_preferred_skills": ["string"],
    "missing_required_skills": ["string"],
    "details": {
      "experience": {
        "match": "string",
        "score": "number",
        "message": "string"
      },
      "education": {
        "match": "string",
        "score": "number",
        "message": "string"
      }
    },
    "semantic_analysis": {
      "overall_score": "number",
      "analysis": "string",
      "strengths": ["string"],
      "weaknesses": ["string"],
      "recommendations": ["string"]
    },
    "resume_hash": "string",
    "job_hash": "string"
  },
  "cached": "boolean"
}
```

### 数据结构说明

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| resume_hash | string | 是 | 简历哈希值 |
| job_hash | string | 是 | 岗位哈希值 |
| mode | string | 否 | 匹配模式（fast/standard/deep），默认standard |

**响应参数（异步任务）**：

| 参数 | 类型 | 说明 |
|------|------|------|
| success | boolean | 请求是否成功 |
| task_id | string | 任务ID，用于查询匹配结果 |

**响应参数（缓存结果）**：

| 参数 | 类型 | 说明 |
|------|------|------|
| success | boolean | 请求是否成功 |
| data | object | 匹配结果数据 |
| cached | boolean | 是否使用缓存 |

**data数据结构**：

| 字段 | 类型 | 说明 |
|------|------|------|
| match_score | number | 总体匹配分数（0-100） |
| skill_match_rate | number | 技能匹配率（0-1） |
| experience_match | string | 工作经验匹配结果（符合/不足/超出） |
| education_match | string | 学历匹配结果（符合/不足/超出） |
| matched_required_skills | array | 匹配的必需技能列表 |
| matched_preferred_skills | array | 匹配的加分技能列表 |
| missing_required_skills | array | 缺失的必需技能列表 |
| details | object | 详细匹配信息 |
| details.experience | object | 工作经验详情 |
| details.experience.match | string | 匹配状态 |
| details.experience.score | number | 匹配分数 |
| details.experience.message | string | 匹配说明 |
| details.education | object | 学历详情 |
| details.education.match | string | 匹配状态 |
| details.education.score | number | 匹配分数 |
| details.education.message | string | 匹配说明 |
| semantic_analysis | object | 语义分析结果（深度模式） |
| semantic_analysis.overall_score | number | 语义分析总分 |
| semantic_analysis.analysis | string | 综合分析文本 |
| semantic_analysis.strengths | array | 优势列表 |
| semantic_analysis.weaknesses | array | 劣势列表 |
| semantic_analysis.recommendations | array | 建议列表 |
| resume_hash | string | 简历哈希值 |
| job_hash | string | 岗位哈希值 |

**匹配模式说明**：

| 模式 | 说明 | 响应内容 |
|------|------|---------|
| fast | 快速匹配 | 仅规则匹配结果 |
| standard | 标准匹配 | 规则匹配 + 基础语义分析 |
| deep | 深度匹配 | 规则匹配 + 详细语义分析（包含项目分析） |

---

## 9. 查询任务状态

### 请求

```
GET /api/task/status/<task_id>
```

### 路径参数

| 参数 | 类型 | 描述 |
|------|------|------|
| task_id | string | 任务ID |

### 响应（进行中）

```json
{
  "success": true,
  "data": {
    "task_id": "string",
    "type": "string",
    "status": "string",
    "progress": "number",
    "message": "string",
    "created_at": "string",
    "updated_at": "string"
  }
}
```

### 响应（已完成）

```json
{
  "success": true,
  "data": {
    "task_id": "string",
    "type": "string",
    "status": "string",
    "progress": "number",
    "message": "string",
    "result": {
      "match_score": "number",
      "skill_match_rate": "number",
      "experience_match": "string",
      "education_match": "string",
      "matched_required_skills": ["string"],
      "matched_preferred_skills": ["string"],
      "missing_required_skills": ["string"],
      "details": {
        "experience": {
          "match": "string",
          "score": "number",
          "message": "string"
        },
        "education": {
          "match": "string",
          "score": "number",
          "message": "string"
        }
      },
      "semantic_analysis": {
        "overall_score": "number",
        "analysis": "string",
        "strengths": ["string"],
        "weaknesses": ["string"],
        "recommendations": ["string"]
      }
    },
    "created_at": "string",
    "updated_at": "string"
  }
}
```

### 响应（失败）

```json
{
  "success": true,
  "data": {
    "task_id": "string",
    "type": "string",
    "status": "string",
    "progress": "number",
    "message": "string",
    "error": "string",
    "created_at": "string",
    "updated_at": "string"
  }
}
```

### 数据结构说明

**响应参数**：

| 参数 | 类型 | 说明 |
|------|------|------|
| success | boolean | 请求是否成功 |
| data | object | 任务数据 |

**data数据结构**：

| 字段 | 类型 | 说明 |
|------|------|------|
| task_id | string | 任务ID |
| type | string | 任务类型（resume_parse/match） |
| status | string | 任务状态（pending/processing/completed/failed） |
| progress | number | 进度（0-100） |
| message | string | 状态消息 |
| result | object | 任务结果（仅completed状态） |
| error | string | 错误信息（仅failed状态） |
| created_at | string | 创建时间（ISO 8601格式） |
| updated_at | string | 更新时间（ISO 8601格式） |

**result数据结构**（匹配任务）：

| 字段 | 类型 | 说明 |
|------|------|------|
| match_score | number | 总体匹配分数（0-100） |
| skill_match_rate | number | 技能匹配率（0-1） |
| experience_match | string | 工作经验匹配结果 |
| education_match | string | 学历匹配结果 |
| matched_required_skills | array | 匹配的必需技能列表 |
| matched_preferred_skills | array | 匹配的加分技能列表 |
| missing_required_skills | array | 缺失的必需技能列表 |
| details | object | 详细匹配信息 |
| details.experience | object | 工作经验详情 |
| details.education | object | 学历详情 |
| semantic_analysis | object | 语义分析结果（深度模式） |

---

## 任务状态说明

| 状态 | 描述 |
|------|------|
| pending | 任务等待处理 |
| processing | 任务处理中 |
| completed | 任务已完成 |
| failed | 任务失败 |

---

## 错误码说明

| HTTP状态码 | 描述 |
|------------|------|
| 200 | 请求成功 |
| 400 | 请求参数错误 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

---

## 使用示例

### cURL 示例

#### 1. 上传简历

```bash
# 将PDF转换为base64并上传
PDF_BASE64=$(base64 -w 0 resume.pdf)

curl -X POST "https://your-function-url.cn-hangzhou.fcapp.run/api/resume/upload" \
  -H "Content-Type: application/json" \
  -d "{\"file\": \"$PDF_BASE64\", \"filename\": \"resume.pdf\"}"
```

#### 2. 解析岗位

```bash
curl -X POST "https://your-function-url.cn-hangzhou.fcapp.run/api/job/parse" \
  -H "Content-Type: application/json" \
  -d '{
    "job_description": "岗位名称: Java开发工程师\n工作职责: 负责后端开发\n任职要求: 3年以上Java经验"
  }'
```

#### 3. 匹配简历和岗位

```bash
curl -X POST "https://your-function-url.cn-hangzhou.fcapp.run/api/match" \
  -H "Content-Type: application/json" \
  -d '{
    "resume_hash": "abc123...",
    "job_hash": "xyz789...",
    "mode": "standard"
  }'
```

#### 4. 查询任务状态

```bash
curl -X GET "https://your-function-url.cn-hangzhou.fcapp.run/api/task/status/task_abc123"
```
---

## 注意事项

1. **异步处理**: 简历上传和匹配操作是异步的，需要通过任务状态接口查询结果
2. **缓存机制**: 岗位解析和匹配结果会被缓存，相同内容不会重复处理
3. **文件格式**: 目前仅支持PDF格式的简历文件
4. **超时设置**: 建议客户端设置至少30秒的超时时间
5. **并发限制**: 阿里云函数计算有并发限制，大量请求可能需要排队


---


## 数据结构参考

### 通用响应结构

所有API响应都遵循以下基本结构：

```json
{
  "success": "boolean",
  "data": "object|array",
  "cached": "boolean",
  "error": "string"
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| success | boolean | 请求是否成功 |
| data | object/array | 响应数据（成功时） |
| cached | boolean | 是否使用缓存（可选） |
| error | string | 错误信息（失败时） |

---

### 简历数据结构

#### ResumeInfo

```json
{
  "resume_hash": "string",
  "metadata": {
    "page_count": "number",
    "parse_time": "string"
  },
  "basic_info": {
    "name": "string",
    "phone": "string",
    "email": "string",
    "location": "string"
  },
  "job_info": {
    "current_company": "string",
    "current_position": "string",
    "job_intention": "string",
    "expected_salary": "string"
  },
  "background_info": {
    "work_years": "number",
    "education": ["EducationInfo"],
    "work_experience": ["WorkExperienceInfo"],
    "projects": ["ProjectInfo"]
  },
  "skills": ["SkillInfo"],
  "skill_summary": {
    "normalized": ["string"],
    "expanded": ["string"]
  }
}
```

#### EducationInfo

```json
{
  "school": "string",
  "degree": "string",
  "major": "string",
  "graduation_year": "number",
  "start_date": "string",
  "end_date": "string"
}
```

#### WorkExperienceInfo

```json
{
  "company": "string",
  "position": "string",
  "start_date": "string",
  "end_date": "string",
  "description": "string"
}
```

#### ProjectInfo

```json
{
  "project_name": "string",
  "role": "string",
  "description": "string",
  "technologies": ["string"],
  "start_date": "string",
  "end_date": "string"
}
```

#### SkillInfo

```json
{
  "name": "string",
  "category": "string",
  "proficiency": "string",
  "usage_years": "number",
  "source": "string"
}
```

---

### 岗位数据结构

#### JobInfo

```json
{
  "job_hash": "string",
  "job_title": "string",
  "experience_years": {
    "min": "number",
    "max": "number",
    "description": "string"
  },
  "education_level": {
    "required": "string",
    "preferred": "string"
  },
  "required_skills": ["RequiredSkillInfo"],
  "responsibilities": ["string"],
  "keywords": ["string"],
  "skill_summary": {
    "normalized": ["string"],
    "expanded": ["string"]
  },
  "original_description": "string"
}
```

#### RequiredSkillInfo

```json
{
  "name": "string",
  "importance": "string",
  "proficiency": "string"
}
```

---

### 匹配结果数据结构

#### MatchResult

```json
{
  "match_score": "number",
  "skill_match_rate": "number",
  "experience_match": "string",
  "education_match": "string",
  "matched_required_skills": ["string"],
  "matched_preferred_skills": ["string"],
  "missing_required_skills": ["string"],
  "details": {
    "experience": "MatchDetail",
    "education": "MatchDetail"
  },
  "semantic_analysis": "SemanticAnalysis",
  "resume_hash": "string",
  "job_hash": "string"
}
```

#### MatchDetail

```json
{
  "match": "string",
  "score": "number",
  "message": "string"
}
```

#### SemanticAnalysis

```json
{
  "overall_score": "number",
  "analysis": "string",
  "strengths": ["string"],
  "weaknesses": ["string"],
  "recommendations": ["string"]
}
```

---

### 任务数据结构

#### TaskInfo

```json
{
  "task_id": "string",
  "type": "string",
  "status": "string",
  "progress": "number",
  "message": "string",
  "result": "MatchResult",
  "error": "string",
  "created_at": "string",
  "updated_at": "string"
}
```

---

### 数据类型说明

| 类型 | 说明 | 示例 |
|------|------|------|
| string | 字符串 | "张三" |
| number | 数字 | 25 |
| boolean | 布尔值 | true/false |
| array | 数组 | ["Java", "Python"] |
| object | 对象 | {"name": "张三", "age": 25} |

---

### 枚举值说明

#### 任务状态 (status)
- `pending` - 等待处理
- `processing` - 处理中
- `completed` - 已完成
- `failed` - 失败

#### 任务类型 (type)
- `resume_parse` - 简历解析
- `match` - 匹配分析

#### 匹配模式 (mode)
- `fast` - 快速匹配
- `standard` - 标准匹配
- `deep` - 深度匹配

#### 匹配结果 (match)
- `符合` - 符合要求
- `不足` - 低于要求
- `超出` - 超出要求

#### 技能重要性 (importance)
- `必须` - 必需技能
- `加分` - 加分技能

#### 技能来源 (source)
- `提取` - 从简历中提取
- `推断` - AI推断
- `扩展` - 技能库扩展
