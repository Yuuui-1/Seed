from app.agents.question_selector import DIMENSIONS, DIMENSION_LABELS

def _format_evidence(dimension: str, score: float, evidence: list[str]) -> list[str]:
    """Format evidence with interpretive context instead of raw question quotes."""
    if not evidence:
        return []
    contexts = {
        "thinking": "在面对需要深入分析的场景时，你倾向于",
        "creativity": "在处理需要创新的问题时，你表现出",
        "execution": "在需要持续投入的任务中，你展现出",
        "social": "在人际互动场景里，你反映出",
        "emotional": "在情绪波动的时刻，你体现出",
        "drive": "在面对有挑战性的目标时，你展现出",
    }
    prefix = contexts.get(dimension, "测评数据显示你")
    results = []
    for e in evidence[:3]:
        short = e.replace("第X题：", "").replace("第", "").replace("题：", "").strip()
        if len(short) > 40:
            short = short[:40] + "..."
        results.append(f"{prefix}{short}")
    return results


TEMPLATES = {
    "thinking": {
        "very_high": {"strengths": "你表现出卓越的系统性分析能力，善于在复杂信息中识别规律和逻辑结构。你习惯先拆解再解决的思维方式是你最大的认知资产。", "improve": "注意避免过度分析导致的行动延迟，在需要快速决策的场景中可以适当依赖直觉。"},
        "high": {"strengths": "你具备良好的分析推理能力，面对复杂问题时能保持结构化思考。你在需要逻辑判断的领域有天然优势。", "improve": "可以尝试更广泛地接触跨领域知识，提升类比和迁移能力。"},
        "mid": {"strengths": "你具备基本的逻辑分析能力，在处理熟悉领域的问题时表现出条理性。你的思维方式在结构化环境中发挥最好。", "improve": "建议通过阅读推理类书籍、参与辩论或使用思维导图等工具来刻意练习深度思考。"},
        "low_mid": {"strengths": "你更倾向于实用导向的思考方式，关注解决方案而非分析过程。这在需要快速行动的场景中是优势。", "improve": "可以尝试在遇到问题时多问一个'为什么'，练习从多角度审视同一个问题。"},
        "low": {"strengths": "你偏好直觉和经验驱动的决策方式，在人际互动和创意场景中往往能做出快速判断。", "improve": "建议有意识地使用 SWOT 分析、5Why 法等方法论工具，逐步建立结构化思维习惯。"},
    },
    "creativity": {
        "very_high": {"strengths": "你拥有极为丰富想象力和创造力，善于跳出框架思考，经常产生令人耳目一新的想法。这是创新工作中不可替代的品质。", "improve": "注意在需要收敛时能够聚焦，将创造力落实到可执行的方案上。"},
        "high": {"strengths": "你具备良好的创意能力，不满足于常规方案，愿意尝试新方法和新视角。在需要创新的场景中你能提供独特价值。", "improve": "尝试系统性的创意方法（如设计思维、头脑风暴），让创造力更稳定地产出。"},
        "mid": {"strengths": "你在特定场景或领域内能展现出创造力，尤其是当你对某个话题充满兴趣时。你具备创造性思维的潜力。", "improve": "拓宽输入渠道——多接触不同领域的知识、艺术形式和文化体验，有助于激活更多创意连接。"},
        "low_mid": {"strengths": "你更擅长优化和改进已有方案，而非从零创造。这种实用主义创造力在工程和运营领域很有价值。", "improve": "可以从小处开始创意练习，比如每天想一个改进现有产品的小点子。"},
        "low": {"strengths": "你偏好既定规则和成熟方法，这在需要稳定性和可靠性的工作中是优势。你善于在框架内发挥。", "improve": "尝试在安全环境中做创意练习，比如列出'一个问题的 10 种不同解法'，先求量不求质。"},
    },
    "execution": {
        "very_high": {"strengths": "你拥有极强的执行力和自驱力，能够长期坚持目标不受干扰。这种坚毅品质是成就任何事业的基础。", "improve": "注意平衡执行与反思，定期花时间确认你正朝正确的方向前进，而非仅仅在前进。"},
        "high": {"strengths": "你具备出色的自律和行动力，能坚定地朝着目标推进。在需要长期投入的项目中你能保持稳定产出。", "improve": "可以建立更加系统化的任务管理方法，让执行力在更高的工作量下也能保持。"},
        "mid": {"strengths": "你在有明确目标和外部监督时执行效率较高。一旦明确了方向，你就能投入行动。", "improve": "建议建立个人任务管理系统（如 GTD 方法），培养在没有外部督促时的自主执行习惯。"},
        "low_mid": {"strengths": "你偏好灵活和自发的行动方式，这在需要快速响应和适应变化的环境中很有价值。", "improve": "尝试从完成小目标开始积累成就感，逐步延长你的专注时长和坚持周期。"},
        "low": {"strengths": "你对环境和外部支持有较高的依赖，在有良好团队氛围和明确分工时表现最佳。", "improve": "建议从小小习惯开始——早起的 10 分钟规划，每天完成 3 件小事，逐步建立执行正循环。"},
    },
    "social": {
        "very_high": {"strengths": "你拥有出色的人际洞察力和沟通能力，善于理解和协调不同角色。你在团队中是天然的关系枢纽。", "improve": "注意在必要时保护自己的情感能量，学会在深度倾听和自我保护之间找到平衡。"},
        "high": {"strengths": "你具备良好的共情和沟通能力，能够在团队中建立信任和理解。你在需要协作的场合能发挥重要作用。", "improve": "尝试更主动地向上管理和表达个人诉求，让社交力不仅服务他人也服务自己。"},
        "mid": {"strengths": "你能够融入团队并进行基本的协作沟通。在熟悉的环境中，你的人际交往是顺畅的。", "improve": "可以主动参与需要协调的工作场景，练习公开表达和跨部门沟通。"},
        "low_mid": {"strengths": "你更享受独立和深度的交流，而非大范围的社交。这种偏好让你在需要专注的任务中表现优秀。", "improve": "可以在舒适区内逐步扩大社交圈，加入兴趣小组或行业协会，以共同话题降低社交压力。"},
        "low": {"strengths": "你更偏好独立思考和行动，在需要深度工作和个人空间的任务中能发挥最大价值。", "improve": "不需要强迫自己成为社交达人。重点发展 2-3 个深度关系，同时在工作中利用异步沟通工具来协作。"},
    },
    "emotional": {
        "very_high": {"strengths": "你拥有卓越的情绪调节能力，在高压和逆境中能保持冷静和理智。这是领导力的核心素质之一。", "improve": "注意不要压抑正常的负面情绪，适度的情绪表达是健康心理的一部分。"},
        "high": {"strengths": "你面对压力和挫折时能较快恢复状态，情绪的稳定性让你在波动环境中保持持续产出。", "improve": "可以尝试更精细地识别和命名自己的情绪，这有助于你在情绪波动前及时调整。"},
        "mid": {"strengths": "你在大多数日常情况下能管理好自己的情绪。面对较大压力时可能出现波动，但整体处于健康范围。", "improve": "建议建立个人的压力管理工具箱：运动、正念冥想、写日记等都是有效方法。"},
        "low_mid": {"strengths": "你对情绪有敏锐的感知能力，这不是弱点——情绪敏感者往往也是高度共情的人。", "improve": "学习区分'我的情绪'和'他人的情绪'，练习在强烈情绪出现时的暂停技巧。"},
        "low": {"strengths": "你的情绪体验丰富而真实，让你在艺术创作和人际共情方面有独特视角。", "improve": "建议从最简单的方法开始——每天 5 分钟的正念呼吸。如有需要，专业心理咨询也是值得考虑的资源。"},
    },
    "drive": {
        "very_high": {"strengths": "你拥有极为强劲的内在驱动力，不需要外部胡萝卜或鞭子就能持续前进。你对卓越的追求是你最大的引擎。", "improve": "注意避免 burnout——在追求卓越的同时确保有足够的休息和恢复期。"},
        "high": {"strengths": "你有明确的目标感和内在动力，在感兴趣的事情上能自驱前行。你的人生方向感较强。", "improve": "尝试将个人目标与更大的价值意义连接，这会让你的动力更加持久。"},
        "mid": {"strengths": "你在有明确目标和适当激励时能够保持动力。一旦找到了心之所向，你就能全力以赴。", "improve": "花时间探索真正让你心动的目标。尝试写下'我理想的 5 年后是什么样子'，找到内在的连接点。"},
        "low_mid": {"strengths": "你对外部环境和他人期望的响应较好，在团队驱动下能发挥很好。你不是没有动力，而是动力来源不同。", "improve": "寻找一个能激发你热情的伙伴或社群，用同伴的力量带动自己的行动。"},
        "low": {"strengths": "你对'努力'这件事持开放和反思的态度，有时候'躺平'也是一种智慧。", "improve": "从小小的承诺开始——今天读 5 页书，本周跑步 1 次。微小的成功体验会慢慢激活你的内在驱动。"},
    },
}


async def generate_dimension_report(dimension: str, score: float, evidence: list[str], llm=None) -> dict:
    """Generate text interpretation for a dimension. Uses LLM if provided, else templates."""
    if llm:
        return await _llm_report(dimension, score, evidence, llm)

    level = "very_high" if score >= 85 else "high" if score >= 70 else "mid" if score >= 55 else "low_mid" if score >= 40 else "low"
    entry = TEMPLATES.get(dimension, {}).get(level, {"strengths": "", "improve": "持续关注这一维度的发展。"})
    return {
        "strengths": entry.get("strengths", ""),
        "areas_for_improvement": entry.get("improve", ""),
        "description": f"{entry.get('strengths', '')}\n\n{entry.get('improve', '')}",
        "evidence": _format_evidence(dimension, score, evidence),
    }


async def generate_career_suggestions(scores: dict, llm=None) -> list[dict]:
    """Generate career direction suggestions based on dimension scores."""
    sorted_dims = sorted(scores.items(), key=lambda x: x[1]["score"], reverse=True)
    career_map = {
        "thinking": [{"direction": "数据分析师", "match": 90, "reason": "你的系统思维和分析能力是该岗位的核心素质"}, {"direction": "管理咨询", "match": 85, "reason": "结构化思维和逻辑推理能力适合咨询行业"}],
        "creativity": [{"direction": "产品设计师", "match": 90, "reason": "你的创造力和发散思维是设计的核心驱动力"}, {"direction": "内容创作者", "match": 85, "reason": "创意能力让你在内容领域有独特优势"}],
        "execution": [{"direction": "项目经理", "match": 90, "reason": "出色的执行力和目标导向性让你适合项目管理工作"}, {"direction": "运营管理", "match": 85, "reason": "自律和计划性是运营岗位的重要品质"}],
        "social": [{"direction": "用户研究员", "match": 90, "reason": "你的共情和沟通能力是理解用户需求的关键"}, {"direction": "BD/商务拓展", "match": 85, "reason": "人际影响力适合商务和关系型工作"}],
        "emotional": [{"direction": "团队领导", "match": 85, "reason": "情绪稳定性是领导力的基础"}, {"direction": "心理咨询师", "match": 80, "reason": "情绪觉察和管理能力是咨询的核心素质"}],
        "drive": [{"direction": "创业者", "match": 88, "reason": "强大的内驱力和成就动机是创业者的核心特质"}, {"direction": "自由职业者", "match": 85, "reason": "自驱力让你能够独立高效地工作"}],
    }
    suggestions = []
    seen = set()
    for dim in [d[0] for d in sorted_dims[:3]]:
        for s in career_map.get(dim, []):
            if s["direction"] not in seen:
                s["match"] = min(97, 40 + int(scores[dim]["score"] * 0.6))
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
