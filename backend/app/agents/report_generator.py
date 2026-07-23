from app.agents.question_selector import DIMENSIONS, DIMENSION_LABELS

async def generate_dimension_report(dimension: str, score: float, evidence: list[str], llm=None) -> dict:
    """Generate text interpretation for a dimension. Uses LLM if provided, else templates."""
    if llm:
        return await _llm_report(dimension, score, evidence, llm)

    templates = {
        "thinking": {
            "high": "你展现出很强的系统性思维和分析能力，擅长拆解复杂问题并找到逻辑规律。你在需要深度思考的领域有天然优势。",
            "mid": "你具备一定的分析能力，在面对复杂问题时能够进行逻辑思考。建议通过阅读和辩论等训练进一步提升思维深度。",
            "low": "你更倾向于直觉和经验驱动的决策方式。可以尝试刻意练习结构化思维，如使用思维导图、SWOT分析等工具。",
        },
        "creativity": {
            "high": "你拥有丰富的想象力和创造力，喜欢探索新想法和不同解决方案。你在创新型工作中能发挥最大价值。",
            "mid": "你有一定的创造力，在特定场景下能产生新颖的想法。尝试拓宽跨领域知识可以进一步激发创造潜能。",
            "low": "你更偏爱既定规则和成熟方法。可以通过头脑风暴、设计思维等练习逐步培养创造性思维。",
        },
        "execution": {
            "high": "你具备出色的执行力和自律性，能坚定地朝着目标推进。你的坚韧和计划性是团队中宝贵的品质。",
            "mid": "你有一定的执行力，在有外部督促时表现更好。建议建立个人任务管理系统来提升自主执行效率。",
            "low": "你在坚持完成长期目标方面可能遇到挑战。从小目标开始，逐步培养习惯是有效的改善路径。",
        },
        "social": {
            "high": "你在人际互动中表现得游刃有余，善于沟通协调和共情理解。你是团队中天然的关系润滑剂。",
            "mid": "你具备基本的社交能力，能够融入团队。多参与协作型项目有助于进一步提升人际影响力。",
            "low": "你更享受独立思考和工作。可以在舒适区内逐步增加社交练习来提升协作效率。",
        },
        "emotional": {
            "high": "你拥有出色的情绪管理能力，面对压力和挫折时能保持理性和冷静。这是领导力的重要基础。",
            "mid": "你基本能够管理自己的情绪，但在极端压力下可能出现波动。正念和冥想练习可以帮助提升情绪稳定性。",
            "low": "你可能容易受到情绪波动的影响。学习情绪觉察和调节技巧将对你的工作和生活有显著帮助。",
        },
        "drive": {
            "high": "你拥有强大的内在驱动力，对自我成长和成就充满渴望。这种主动性将推动你不断突破自我。",
            "mid": "你有基本的目标感和动力，在感兴趣的事情上表现更积极。尝试找到工作和个人价值的连接点。",
            "low": "你可能在寻找内在动力方面存在挑战。尝试探索自己真正热爱的事物，建立小的正向反馈循环。",
        },
    }

    level = "high" if score >= 75 else "mid" if score >= 50 else "low"
    tmpl = templates.get(dimension, {})
    return {
        "strengths": tmpl.get(level, ""),
        "areas_for_improvement": "",
        "description": tmpl.get(level, ""),
        "evidence": evidence[:3],
    }

async def generate_career_suggestions(scores: dict, llm=None) -> list[dict]:
    """Generate career direction suggestions based on dimension scores."""
    sorted_dims = sorted(scores.items(), key=lambda x: x[1]["score"], reverse=True)
    top = [d[0] for d in sorted_dims[:2]]

    career_map = {
        "thinking": [
            {"direction": "数据分析师", "match": 90, "reason": "你的系统思维和分析能力是该岗位的核心素质"},
            {"direction": "管理咨询", "match": 85, "reason": "结构化思维和逻辑推理能力适合咨询行业"},
        ],
        "creativity": [
            {"direction": "产品设计师", "match": 90, "reason": "你的创造力和发散思维是设计的核心驱动力"},
            {"direction": "内容创作者", "match": 85, "reason": "创意能力让你在内容领域有独特优势"},
        ],
        "execution": [
            {"direction": "项目经理", "match": 90, "reason": "出色的执行力和目标导向性让你适合项目管理工作"},
            {"direction": "运营管理", "match": 85, "reason": "自律和计划性是运营岗位的重要品质"},
        ],
        "social": [
            {"direction": "用户研究员", "match": 90, "reason": "你的共情和沟通能力是理解用户需求的关键"},
            {"direction": "BD/商务拓展", "match": 85, "reason": "人际影响力适合商务和关系型工作"},
        ],
        "emotional": [
            {"direction": "团队领导", "match": 85, "reason": "情绪稳定性是领导力的基础"},
            {"direction": "心理咨询师", "match": 80, "reason": "情绪觉察和管理能力是咨询的核心素质"},
        ],
        "drive": [
            {"direction": "创业者", "match": 88, "reason": "强大的内驱力和成就动机是创业者的核心特质"},
            {"direction": "自由职业者", "match": 85, "reason": "自驱力让你能够独立高效地工作"},
        ],
    }

    suggestions = []
    seen = set()
    for dim in [d[0] for d in sorted_dims[:3]]:
        for s in career_map.get(dim, []):
            if s["direction"] not in seen:
                s["match"] = min(95, s["match"] + int(scores[dim]["score"] / 10) - 50)
                suggestions.append(s)
                seen.add(s["direction"])
    return suggestions[:5]

async def generate_summary(scores: dict) -> str:
    """Generate an overall summary based on dimension scores."""
    top_dims = sorted(scores.items(), key=lambda x: x[1]["score"], reverse=True)[:2]
    low_dims = sorted(scores.items(), key=lambda x: x[1]["score"])[:2]

    top_names = [DIMENSION_LABELS[d[0]] for d in top_dims]
    low_names = [DIMENSION_LABELS[d[0]] for d in low_dims]

    return (
        f"综合来看，你的核心优势集中在{'和'.join(top_names)}方面。"
        f"你在需要{'和'.join(top_names)}的工作场景中能够发挥最大价值。"
        f"建议你在{'和'.join(low_names)}方面有意识地进行针对性提升，这将帮助你实现更全面的个人发展。"
    )
