#!/usr/bin/env python3
"""
Marketing Analytics AI MCP Server
=====================================
Marketing analytics toolkit for AI agents: campaign ROI, A/B test analysis,
funnel optimization, attribution modeling, and ad copy generation.

By MEOK AI Labs | https://meok.ai

Install: pip install mcp
Run:     python server.py
"""


import sys, os
sys.path.insert(0, os.path.expanduser('~/clawd/meok-labs-engine/shared'))
from auth_middleware import check_access

import math
import re
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Optional
from mcp.server.fastmcp import FastMCP

# ---------------------------------------------------------------------------
# Rate limiting
# ---------------------------------------------------------------------------
FREE_DAILY_LIMIT = 30
_usage: dict[str, list[datetime]] = defaultdict(list)


def _check_rate_limit(caller: str = "anonymous") -> Optional[str]:
    now = datetime.now()
    cutoff = now - timedelta(days=1)
    _usage[caller] = [t for t in _usage[caller] if t > cutoff]
    if len(_usage[caller]) >= FREE_DAILY_LIMIT:
        return f"Free tier limit reached ({FREE_DAILY_LIMIT}/day). Upgrade: https://mcpize.com/marketing-analytics-ai-mcp/pro"
    _usage[caller].append(now)
    return None


# ---------------------------------------------------------------------------
# Core operations
# ---------------------------------------------------------------------------
def _campaign_roi(spend: float, revenue: float, conversions: int,
                  impressions: int, clicks: int, period_days: int) -> dict:
    """Calculate comprehensive campaign ROI metrics."""
    if spend <= 0:
        return {"error": "Spend must be positive"}

    roi_pct = ((revenue - spend) / spend) * 100
    roas = revenue / spend
    cpa = spend / max(conversions, 1)
    cpc = spend / max(clicks, 1)
    cpm = (spend / max(impressions, 1)) * 1000
    ctr = (clicks / max(impressions, 1)) * 100
    conv_rate = (conversions / max(clicks, 1)) * 100
    profit = revenue - spend
    daily_spend = spend / max(period_days, 1)
    daily_revenue = revenue / max(period_days, 1)

    if roi_pct > 200:
        performance = "Exceptional"
        recommendation = "Scale budget 50-100%. This campaign is highly profitable."
    elif roi_pct > 100:
        performance = "Strong"
        recommendation = "Scale budget 20-50%. Optimize top-performing segments."
    elif roi_pct > 0:
        performance = "Profitable"
        recommendation = "Maintain budget. Focus on improving conversion rate."
    elif roi_pct > -30:
        performance = "Marginal"
        recommendation = "Optimize targeting and creatives before increasing spend."
    else:
        performance = "Poor"
        recommendation = "Pause campaign. Review targeting, offer, and landing page."

    benchmarks = {
        "avg_ecommerce_roas": 4.0,
        "avg_saas_cac_months": 12,
        "avg_email_roi_pct": 3600,
        "avg_social_ctr_pct": 1.3,
        "avg_search_ctr_pct": 3.17,
    }

    return {
        "roi_pct": round(roi_pct, 2),
        "roas": round(roas, 2),
        "profit": round(profit, 2),
        "performance": performance,
        "recommendation": recommendation,
        "metrics": {
            "spend": spend,
            "revenue": revenue,
            "conversions": conversions,
            "cpa": round(cpa, 2),
            "cpc": round(cpc, 2),
            "cpm": round(cpm, 2),
            "ctr_pct": round(ctr, 2),
            "conversion_rate_pct": round(conv_rate, 2),
        },
        "daily": {
            "avg_spend": round(daily_spend, 2),
            "avg_revenue": round(daily_revenue, 2),
            "avg_profit": round(daily_revenue - daily_spend, 2),
        },
        "period_days": period_days,
        "industry_benchmarks": benchmarks,
    }


def _ab_test_analyze(visitors_a: int, conversions_a: int,
                     visitors_b: int, conversions_b: int,
                     confidence_level: float) -> dict:
    """Analyze A/B test results with statistical significance."""
    if visitors_a <= 0 or visitors_b <= 0:
        return {"error": "Visitor counts must be positive"}

    rate_a = conversions_a / visitors_a
    rate_b = conversions_b / visitors_b
    lift = ((rate_b - rate_a) / max(rate_a, 0.0001)) * 100

    # Standard error and z-score
    se_a = math.sqrt(rate_a * (1 - rate_a) / visitors_a) if 0 < rate_a < 1 else 0.001
    se_b = math.sqrt(rate_b * (1 - rate_b) / visitors_b) if 0 < rate_b < 1 else 0.001
    se_diff = math.sqrt(se_a ** 2 + se_b ** 2)
    z_score = (rate_b - rate_a) / se_diff if se_diff > 0 else 0

    # Approximate p-value using normal CDF approximation
    abs_z = abs(z_score)
    p_value = math.exp(-0.5 * abs_z * abs_z) / (abs_z * math.sqrt(2 * math.pi)) if abs_z > 0.5 else 0.5
    p_value = min(1.0, max(0.0, p_value * 2))  # two-tailed

    is_significant = p_value < (1 - confidence_level)

    # Sample size adequacy
    min_sample = int(16 * (rate_a * (1 - rate_a)) / (0.05 * rate_a) ** 2) if rate_a > 0 else 1000
    sample_adequate = visitors_a >= min_sample and visitors_b >= min_sample

    if is_significant and lift > 0:
        winner = "B"
        recommendation = f"Variant B wins with {round(lift, 1)}% lift. Implement B."
    elif is_significant and lift < 0:
        winner = "A"
        recommendation = f"Control A wins. Variant B decreased performance by {round(abs(lift), 1)}%."
    else:
        winner = "Inconclusive"
        remaining = max(0, min_sample - min(visitors_a, visitors_b))
        recommendation = f"Not statistically significant yet. Need ~{remaining} more visitors per variant."

    return {
        "winner": winner,
        "is_significant": is_significant,
        "recommendation": recommendation,
        "variant_a": {
            "visitors": visitors_a,
            "conversions": conversions_a,
            "conversion_rate_pct": round(rate_a * 100, 3),
        },
        "variant_b": {
            "visitors": visitors_b,
            "conversions": conversions_b,
            "conversion_rate_pct": round(rate_b * 100, 3),
        },
        "analysis": {
            "lift_pct": round(lift, 2),
            "z_score": round(z_score, 4),
            "p_value": round(p_value, 4),
            "confidence_level": confidence_level,
            "standard_error": round(se_diff, 6),
        },
        "sample_size": {
            "minimum_recommended": min_sample,
            "adequate": sample_adequate,
        },
    }


def _funnel_optimizer(stages: list[dict]) -> dict:
    """Analyze a conversion funnel and identify optimization opportunities."""
    if not stages or len(stages) < 2:
        return {"error": "Need at least 2 funnel stages with 'name' and 'count' fields"}

    analyzed = []
    total_drop = 0
    biggest_leak_idx = 0
    biggest_leak_pct = 0

    for i, stage in enumerate(stages):
        name = stage.get("name", f"Stage {i + 1}")
        count = stage.get("count", 0)
        if count <= 0:
            return {"error": f"Stage '{name}' has invalid count: {count}"}

        entry = {"name": name, "count": count}

        if i == 0:
            entry["conversion_from_prev_pct"] = 100.0
            entry["cumulative_conversion_pct"] = 100.0
            entry["drop_count"] = 0
        else:
            prev_count = stages[i - 1]["count"]
            conv = (count / prev_count) * 100
            drop = prev_count - count
            cumulative = (count / stages[0]["count"]) * 100

            entry["conversion_from_prev_pct"] = round(conv, 2)
            entry["cumulative_conversion_pct"] = round(cumulative, 2)
            entry["drop_count"] = drop
            entry["drop_pct"] = round((drop / prev_count) * 100, 2)

            total_drop += drop
            if drop / prev_count > biggest_leak_pct:
                biggest_leak_pct = drop / prev_count
                biggest_leak_idx = i

        analyzed.append(entry)

    overall_conv = (stages[-1]["count"] / stages[0]["count"]) * 100

    optimizations = {
        "awareness": "Improve ad targeting and messaging to attract qualified traffic",
        "interest": "Enhance landing page value proposition and social proof",
        "consideration": "Add comparison content, case studies, and free trials",
        "intent": "Simplify pricing, add urgency, reduce friction in signup",
        "purchase": "Streamline checkout, add trust badges, offer guarantees",
        "retention": "Improve onboarding, add drip campaigns, loyalty programs",
    }

    leak_name = analyzed[biggest_leak_idx]["name"] if biggest_leak_idx < len(analyzed) else "unknown"
    tip = optimizations.get(leak_name.lower(), "Review UX and messaging at this stage")

    # Revenue impact estimation
    if biggest_leak_idx > 0:
        improved_conv = analyzed[biggest_leak_idx]["conversion_from_prev_pct"] * 1.1
        potential_gain = int(stages[biggest_leak_idx - 1]["count"] * (improved_conv / 100) - stages[biggest_leak_idx]["count"])
    else:
        potential_gain = 0

    return {
        "overall_conversion_pct": round(overall_conv, 2),
        "total_entries": stages[0]["count"],
        "total_conversions": stages[-1]["count"],
        "total_drop": total_drop,
        "stages": analyzed,
        "biggest_leak": {
            "stage": leak_name,
            "stage_index": biggest_leak_idx,
            "drop_pct": round(biggest_leak_pct * 100, 2),
            "optimization_tip": tip,
            "potential_gain_10pct_improvement": potential_gain,
        },
    }


def _attribution_model(touchpoints: list[dict], model: str) -> dict:
    """Apply attribution modeling to marketing touchpoints."""
    if not touchpoints:
        return {"error": "Provide touchpoints as [{channel, timestamp, cost}]"}

    valid_models = ["first_touch", "last_touch", "linear", "time_decay", "u_shaped", "w_shaped"]
    if model not in valid_models:
        return {"error": f"Invalid model '{model}'. Use: {valid_models}"}

    n = len(touchpoints)
    channels = {}

    for tp in touchpoints:
        ch = tp.get("channel", "unknown")
        if ch not in channels:
            channels[ch] = {"touches": 0, "cost": 0, "credit": 0.0}
        channels[ch]["touches"] += 1
        channels[ch]["cost"] += tp.get("cost", 0)

    # Apply attribution model
    if model == "first_touch":
        if touchpoints:
            ch = touchpoints[0].get("channel", "unknown")
            channels[ch]["credit"] = 1.0
    elif model == "last_touch":
        if touchpoints:
            ch = touchpoints[-1].get("channel", "unknown")
            channels[ch]["credit"] = 1.0
    elif model == "linear":
        credit_each = 1.0 / max(n, 1)
        for tp in touchpoints:
            ch = tp.get("channel", "unknown")
            channels[ch]["credit"] += credit_each
    elif model == "time_decay":
        total_weight = sum(2 ** i for i in range(n))
        for i, tp in enumerate(touchpoints):
            weight = (2 ** i) / total_weight
            ch = tp.get("channel", "unknown")
            channels[ch]["credit"] += weight
    elif model == "u_shaped":
        for i, tp in enumerate(touchpoints):
            ch = tp.get("channel", "unknown")
            if i == 0 or i == n - 1:
                channels[ch]["credit"] += 0.4
            else:
                channels[ch]["credit"] += 0.2 / max(n - 2, 1)
    elif model == "w_shaped":
        mid = n // 2
        for i, tp in enumerate(touchpoints):
            ch = tp.get("channel", "unknown")
            if i == 0 or i == n - 1 or i == mid:
                channels[ch]["credit"] += 0.3
            else:
                channels[ch]["credit"] += 0.1 / max(n - 3, 1)

    # Normalize credits
    total_credit = sum(c["credit"] for c in channels.values())
    if total_credit > 0:
        for ch in channels:
            channels[ch]["credit"] = round(channels[ch]["credit"] / total_credit, 4)
            channels[ch]["credit_pct"] = round(channels[ch]["credit"] * 100, 2)

    ranked = sorted(channels.items(), key=lambda x: x[1]["credit"], reverse=True)

    return {
        "model": model,
        "touchpoint_count": n,
        "channel_count": len(channels),
        "attribution": {ch: data for ch, data in ranked},
        "journey_sequence": [tp.get("channel", "unknown") for tp in touchpoints],
        "model_description": {
            "first_touch": "100% credit to first interaction",
            "last_touch": "100% credit to last interaction before conversion",
            "linear": "Equal credit to all touchpoints",
            "time_decay": "Exponentially more credit to recent touchpoints",
            "u_shaped": "40% first, 40% last, 20% split across middle",
            "w_shaped": "30% first, 30% middle, 30% last, 10% split across rest",
        }.get(model, ""),
    }


def _ad_copy_generator(product: str, audience: str, platform: str,
                       tone: str, cta: str) -> dict:
    """Generate ad copy variations for different platforms."""
    platform_specs = {
        "google_search": {"headline_max": 30, "description_max": 90, "headlines_needed": 3, "descriptions_needed": 2},
        "facebook": {"headline_max": 40, "text_max": 125, "link_desc_max": 30, "variants": 3},
        "instagram": {"caption_max": 2200, "hashtag_max": 30, "variants": 3},
        "linkedin": {"headline_max": 70, "intro_max": 150, "variants": 3},
        "twitter": {"tweet_max": 280, "variants": 3},
        "tiktok": {"caption_max": 150, "hashtag_max": 10, "variants": 3},
    }

    spec = platform_specs.get(platform, platform_specs["facebook"])

    tone_styles = {
        "professional": {"opener": "Discover", "closer": "Get started today", "adj": "proven"},
        "casual": {"opener": "Hey", "closer": "Try it out", "adj": "awesome"},
        "urgent": {"opener": "Don't miss out", "closer": "Act now", "adj": "limited-time"},
        "inspirational": {"opener": "Imagine", "closer": "Start your journey", "adj": "transformative"},
        "humorous": {"opener": "Tired of", "closer": "You're welcome", "adj": "game-changing"},
    }

    style = tone_styles.get(tone, tone_styles["professional"])
    cta_text = cta or style["closer"]

    variants = []
    templates = [
        f"{style['opener']} how {product} helps {audience}. {style['adj'].title()} results guaranteed. {cta_text}.",
        f"Stop struggling with outdated solutions. {product} gives {audience} the edge they need. {cta_text}.",
        f"Join thousands of {audience} who trust {product}. See {style['adj']} results in days. {cta_text}.",
        f"{product}: The {style['adj']} solution {audience} have been waiting for. {cta_text} - risk free.",
        f"Why {audience} are switching to {product}: Better results, less effort. {cta_text}.",
    ]

    for i, tmpl in enumerate(templates[:spec.get("variants", 3)]):
        variant = {
            "variant": i + 1,
            "primary_text": tmpl,
            "char_count": len(tmpl),
        }

        if platform == "google_search":
            variant["headlines"] = [
                f"{product} for {audience}"[:30],
                f"{style['adj'].title()} {product} Solution"[:30],
                f"{cta_text} | {product}"[:30],
            ]
            variant["descriptions"] = [
                tmpl[:90],
                f"Trusted by {audience}. {style['adj'].title()} results with {product}. {cta_text}."[:90],
            ]
        elif platform == "instagram":
            variant["hashtags"] = [
                f"#{product.replace(' ', '')}",
                f"#{audience.replace(' ', '')}",
                "#marketing", "#growth", "#results",
            ]

        variants.append(variant)

    return {
        "product": product,
        "audience": audience,
        "platform": platform,
        "tone": tone,
        "cta": cta_text,
        "platform_specs": spec,
        "variants": variants,
        "best_practices": [
            "Test 3-5 ad copy variants simultaneously",
            "Include social proof (numbers, testimonials)",
            "Match ad copy to landing page messaging",
            f"Platform tip: {platform} favors {'short, punchy copy' if platform in ['twitter', 'tiktok'] else 'detailed value propositions'}",
        ],
    }


# ---------------------------------------------------------------------------
# MCP Server
# ---------------------------------------------------------------------------
mcp = FastMCP(
    "Marketing Analytics AI MCP",
    instructions="Marketing analytics toolkit: campaign ROI, A/B test analysis, funnel optimization, attribution modeling, and ad copy generation. By MEOK AI Labs.")


@mcp.tool()
def campaign_roi(spend: float, revenue: float, conversions: int = 0,
                 impressions: int = 0, clicks: int = 0, period_days: int = 30, api_key: str = "") -> dict:
    """Calculate comprehensive campaign ROI including ROAS, CPA, CPC, CPM,
    CTR, conversion rate, and performance assessment with recommendations.

    Args:
        spend: Total campaign spend in dollars
        revenue: Total revenue attributed to campaign
        conversions: Number of conversions
        impressions: Total ad impressions
        clicks: Total ad clicks
        period_days: Campaign duration in days
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}

    err = _check_rate_limit()
    if err:
        return {"error": err}
    try:
        return _campaign_roi(spend, revenue, conversions, impressions, clicks, period_days)
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def ab_test_analyze(visitors_a: int, conversions_a: int,
                    visitors_b: int, conversions_b: int,
                    confidence_level: float = 0.95, api_key: str = "") -> dict:
    """Analyze A/B test results with statistical significance testing.
    Returns winner, z-score, p-value, lift percentage, and sample size adequacy.

    Args:
        visitors_a: Visitors in control group (A)
        conversions_a: Conversions in control group (A)
        visitors_b: Visitors in variant group (B)
        conversions_b: Conversions in variant group (B)
        confidence_level: Required confidence level (default: 0.95)
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}

    err = _check_rate_limit()
    if err:
        return {"error": err}
    try:
        return _ab_test_analyze(visitors_a, conversions_a, visitors_b, conversions_b, confidence_level)
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def funnel_optimizer(stages: list[dict], api_key: str = "") -> dict:
    """Analyze a conversion funnel and identify the biggest leak point with
    optimization recommendations.

    Args:
        stages: List of funnel stages as [{"name": "Awareness", "count": 10000}, {"name": "Interest", "count": 3000}, ...]
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}

    err = _check_rate_limit()
    if err:
        return {"error": err}
    try:
        return _funnel_optimizer(stages)
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def attribution_model(touchpoints: list[dict], model: str = "linear", api_key: str = "") -> dict:
    """Apply an attribution model to marketing touchpoints. Distributes conversion
    credit across channels based on the chosen model.

    Args:
        touchpoints: Journey as [{"channel": "google", "timestamp": "2024-01-01", "cost": 50}, ...]
        model: Attribution model (first_touch, last_touch, linear, time_decay, u_shaped, w_shaped)
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}

    err = _check_rate_limit()
    if err:
        return {"error": err}
    try:
        return _attribution_model(touchpoints, model)
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def ad_copy_generator(product: str, audience: str, platform: str = "facebook",
                      tone: str = "professional", cta: str = "", api_key: str = "") -> dict:
    """Generate ad copy variants tailored to a specific platform with proper
    character limits and best practices.

    Args:
        product: Product or service name
        audience: Target audience description
        platform: Ad platform (google_search, facebook, instagram, linkedin, twitter, tiktok)
        tone: Copy tone (professional, casual, urgent, inspirational, humorous)
        cta: Call to action text (default: auto-generated based on tone)
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}

    err = _check_rate_limit()
    if err:
        return {"error": err}
    try:
        return _ad_copy_generator(product, audience, platform, tone, cta)
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    mcp.run()
