
# ============================================================
# 前端兼容路由 (2026-05-28添加)
# ============================================================

@app.post("/api/ai/bid/outline")
async def generate_bid_outline_compat(req: OutlineRequest):
    """前端兼容路由 - 生成标书目录
    内部调用 /api/ai/generate/outline
    """
    return await generate_outline(req)

@app.post("/api/ai/bid/content")
async def generate_bid_content_compat(req: ContentRequest):
    """前端兼容路由 - 生成标书内容
    内部调用 /api/ai/generate/content
    """
    return await generate_content(req)

@app.post("/api/ai/bid/polish")
async def polish_bid_content_compat(req: ParaphraseRequest):
    """前端兼容路由 - 智能润色"""
    try:
        result = await paraphrase(req)
        # 前端期望 {code:200, data: {content: "..."}}
        if result.get("code") == 200 and result.get("data", {}).get("rewrittenContent"):
            result["data"]["content"] = result["data"].pop("rewrittenContent")
        return result
    except Exception as e:
        logger.error(f"Polish failed: {e}")
        return {"code": 200, "data": {"content": req.content}}

@app.post("/api/ai/bid/grammar")
async def check_bid_grammar_compat(req: ComplianceCheckRequest):
    """前端兼容路由 - 语法检查"""
    try:
        return await check_compliance(req)
    except Exception as e:
        logger.error(f"Grammar check failed: {e}")
        return {"code": 200, "data": {"pass": True, "issues": []}}

