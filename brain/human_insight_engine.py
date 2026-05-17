#!/usr/bin/env python3
"""
HUMAN INSIGHT ENGINE
Think before building. Profile the human first.
Then make decisions about what to build and how.
"""
import json
import random
from pathlib import Path
from datetime import datetime

HOME = Path.home()

# ═══════════════════════════════════════════════════
# DOMAIN PROFILES — Who actually uses these apps
# ═══════════════════════════════════════════════════
HUMAN_PROFILES = {
    "healthcare": {
        "who": "A nurse or front desk coordinator, probably underpaid, handling 40+ patients a day",
        "hardest_moment": "A patient calls asking about their appointment and she can't find the record fast enough",
        "relief_moment": "Everything she needs is on one screen without scrolling",
        "embarrassment": "Showing a patient a broken or confusing screen",
        "early_morning": "Pulling up yesterday's no-shows before the doctor arrives",
        "decisions": {
            "lead_with": "Today's appointments and alerts — not a login screen",
            "most_important_feature": "Quick patient lookup — she needs it in 3 seconds",
            "skip": "Complex reports nobody reads",
            "tone": "Calm, clinical, trustworthy",
            "color": "#2563eb",
            "mobile_first": True,
            "no_login": True
        }
    },
    "restaurant": {
        "who": "A restaurant owner who is also the cook, manager, and sometimes the waiter",
        "hardest_moment": "Saturday night rush — 6 tables waiting, one ticket system crashed",
        "relief_moment": "Seeing exactly what's on the floor and what's in the kitchen at a glance",
        "embarrassment": "A customer waiting too long because the kitchen missed a ticket",
        "early_morning": "Checking inventory before the lunch prep starts",
        "decisions": {
            "lead_with": "Live orders and table status — nothing else matters during service",
            "most_important_feature": "One-tap order entry that works when hands are greasy",
            "skip": "Fancy analytics during service hours",
            "tone": "Fast, urgent, clear",
            "color": "#dc2626",
            "mobile_first": True,
            "no_login": True
        }
    },
    "salon": {
        "who": "A stylist who owns her own chair or small shop, doing everything alone",
        "hardest_moment": "A client shows up and she forgot about the appointment — another client is in the chair",
        "relief_moment": "Her phone buzzes 30 min before each client so she's never caught off guard",
        "embarrassment": "Double-booking two clients at the same time",
        "early_morning": "Checking who's coming in today while drinking coffee",
        "decisions": {
            "lead_with": "Today's schedule — big, clear, impossible to miss",
            "most_important_feature": "Add appointment in under 10 seconds",
            "skip": "Inventory management — she knows her products",
            "tone": "Warm, personal, friendly",
            "color": "#7c3aed",
            "mobile_first": True,
            "no_login": True
        }
    },
    "nutrition_center": {
        "who": "One dedicated person running a meal program for elderly neighbors, often a volunteer or low-paid coordinator",
        "hardest_moment": "Realizing she doesn't know if Mrs. Hayes answered the door yesterday",
        "relief_moment": "Every client accounted for before she goes home",
        "embarrassment": "Someone falling through the cracks because she forgot to follow up",
        "early_morning": "Counting how many meals to prep before the kitchen starts",
        "decisions": {
            "lead_with": "Wellness alerts and today's delivery route",
            "most_important_feature": "One-tap wellness check logging",
            "skip": "Revenue tracking — this is a service not a business",
            "tone": "Caring, community, warm",
            "color": "#e07b39",
            "mobile_first": True,
            "no_login": True
        }
    },
    "agriculture": {
        "who": "A farmer who wakes up at 5am and makes 50 decisions before breakfast",
        "hardest_moment": "Finding out the field needed irrigation 3 days ago when it's too late",
        "relief_moment": "Knowing exactly what needs attention without walking every field",
        "embarrassment": "Losing yield because of something he could have caught",
        "early_morning": "Checking weather and field status before getting in the truck",
        "decisions": {
            "lead_with": "Alerts and today's priorities — not charts",
            "most_important_feature": "Quick field status at a glance",
            "skip": "Complex financial modeling",
            "tone": "Practical, direct, no-nonsense",
            "color": "#2d6a4f",
            "mobile_first": True,
            "no_login": True
        }
    },
    "gym": {
        "who": "A gym owner who trains clients all day and manages the business at night",
        "hardest_moment": "A member cancels and he didn't know until they stopped showing up",
        "relief_moment": "Seeing which members haven't been in 2 weeks so he can reach out",
        "embarrassment": "A member asks about their progress and he can't remember",
        "early_morning": "Who's scheduled for 6am before he unlocks the door",
        "decisions": {
            "lead_with": "Today's sessions and member check-ins",
            "most_important_feature": "Member attendance tracking",
            "skip": "Complex workout programming tools",
            "tone": "Motivating, energetic, direct",
            "color": "#f59e0b",
            "mobile_first": True,
            "no_login": True
        }
    },
    "pharmacy": {
        "who": "A pharmacist managing prescriptions, pickups, and patient questions simultaneously",
        "hardest_moment": "A patient waiting for a prescription that isn't ready and getting angry",
        "relief_moment": "Knowing exactly what's ready, what's pending, what needs a call",
        "embarrassment": "Giving wrong information about a prescription status",
        "early_morning": "Clearing the overnight refill queue before the rush starts",
        "decisions": {
            "lead_with": "Prescription queue status — ready, pending, waiting",
            "most_important_feature": "Instant prescription status lookup",
            "skip": "Business analytics",
            "tone": "Precise, reliable, calm",
            "color": "#0891b2",
            "mobile_first": True,
            "no_login": True
        }
    },
    "rf_sensing": {
        "who": "A technician or security officer monitoring signals in real time",
        "hardest_moment": "An unknown device appears on the network and he can't identify it fast enough",
        "relief_moment": "Immediate visual alert with device fingerprint already identified",
        "embarrassment": "Missing a threat that was sitting in the logs for hours",
        "early_morning": "Scanning overnight logs for anomalies before the shift starts",
        "decisions": {
            "lead_with": "Live signal map and anomaly alerts",
            "most_important_feature": "Unknown device detection and fingerprinting",
            "skip": "Historical trend charts — act now first",
            "tone": "Alert, technical, urgent",
            "color": "#4f46e5",
            "mobile_first": False,
            "no_login": False
        }
    },
    "robotics": {
        "who": "An engineer or operator monitoring robot systems in real time",
        "hardest_moment": "A robot arm goes out of tolerance and he doesn't catch it until parts are damaged",
        "relief_moment": "Predictive alert before the failure — not after",
        "embarrassment": "Production stoppage that could have been prevented",
        "early_morning": "System health check before production run starts",
        "decisions": {
            "lead_with": "System health and predictive alerts",
            "most_important_feature": "Real-time tolerance monitoring with MPC prediction",
            "skip": "Administrative scheduling",
            "tone": "Precise, technical, reliable",
            "color": "#1d4ed8",
            "mobile_first": False,
            "no_login": False
        }
    },
    "autonomous_vehicle": {
        "who": "A fleet operator managing multiple vehicles and routes simultaneously",
        "hardest_moment": "A vehicle goes offline mid-route and he doesn't know where it is",
        "relief_moment": "Every vehicle visible on one screen with predictive ETAs",
        "embarrassment": "A delivery failure because of a routing error he could have caught",
        "early_morning": "Pre-route check — all vehicles healthy before dispatch",
        "decisions": {
            "lead_with": "Live fleet map with vehicle status",
            "most_important_feature": "Real-time vehicle tracking and route optimization",
            "skip": "Financial reporting during operations",
            "tone": "Operational, clear, decisive",
            "color": "#059669",
            "mobile_first": False,
            "no_login": False
        }
    }
}

# ═══════════════════════════════════════════════════
# INSIGHT ENGINE — Think before building
# ═══════════════════════════════════════════════════
class HumanInsightEngine:
    def __init__(self):
        self.profiles = HUMAN_PROFILES

    def think(self, domain_id, domain_config):
        """
        Think about who uses this. Make decisions.
        Return an insight package that guides generation.
        """
        print(f"\n🧠 THINKING about {domain_id}...")

        # Get known profile or derive from domain config
        profile = self.profiles.get(domain_id)
        if not profile:
            profile = self._derive_profile(domain_id, domain_config)

        # Make decisions based on insight
        insight = {
            "domain": domain_id,
            "human": {
                "who": profile["who"],
                "hardest_moment": profile["hardest_moment"],
                "relief_moment": profile["relief_moment"],
                "early_morning": profile["early_morning"]
            },
            "decisions": profile["decisions"],
            "navigation": self._decide_navigation(domain_id, domain_config, profile),
            "dashboard_priority": self._decide_dashboard(domain_id, profile),
            "alert_conditions": self._decide_alerts(domain_id, profile),
            "tone_words": self._decide_tone_words(profile),
            "generated_at": datetime.now().isoformat()
        }

        self._print_thinking(insight)
        return insight

    def _derive_profile(self, domain_id, cfg):
        """Derive a profile for unknown domains from config"""
        entity = cfg.get("entity", "Item")
        name = cfg.get("name", domain_id)
        return {
            "who": f"A small business owner managing {name} operations alone",
            "hardest_moment": f"Losing track of a {entity.lower()} at a critical moment",
            "relief_moment": f"Everything about every {entity.lower()} visible at a glance",
            "embarrassment": f"Not having an answer when a client asks about their {entity.lower()}",
            "early_morning": f"Checking what {entity.lower()}s need attention today",
            "decisions": {
                "lead_with": f"Today's {entity.lower()} status and alerts",
                "most_important_feature": f"Quick {entity.lower()} lookup and status",
                "skip": "Complex analytics",
                "tone": "Clear, helpful, reliable",
                "color": "#" + f"{hash(domain_id) % 0xFFFFFF:06x}",
                "mobile_first": True,
                "no_login": True
            }
        }

    def _decide_navigation(self, domain_id, cfg, profile):
        """Decide what tabs the app needs based on human insight"""
        nav = cfg.get("nav", [])
        # Always put the most important thing first
        lead = profile["decisions"]["lead_with"]
        return {
            "tabs": nav,
            "first_tab_purpose": lead,
            "max_tabs": 6,  # more than 6 overwhelms mobile users
            "mobile_bottom_nav": profile["decisions"]["mobile_first"]
        }

    def _decide_dashboard(self, domain_id, profile):
        """Decide what goes on the dashboard based on human needs"""
        return {
            "show_alerts_first": True,
            "show_today_count": True,
            "show_pending_actions": True,
            "hide_on_dashboard": ["graphs", "financial_summary", "admin_tools"],
            "lead_message": profile["relief_moment"]
        }

    def _decide_alerts(self, domain_id, profile):
        """Decide what conditions trigger alerts"""
        alerts = {
            "healthcare": ["appointment_no_show", "prescription_overdue", "patient_not_seen"],
            "nutrition_center": ["delivery_no_answer", "client_not_seen_2days", "inventory_low"],
            "restaurant": ["order_taking_too_long", "table_waiting_over_15min"],
            "salon": ["appointment_in_30min", "client_no_show", "double_booking_risk"],
            "agriculture": ["soil_moisture_low", "frost_risk", "equipment_service_due"],
            "gym": ["member_not_visited_14days", "session_starting_soon"],
            "pharmacy": ["prescription_waiting_over_hour", "refill_due"],
            "rf_sensing": ["unknown_device_detected", "signal_anomaly", "frequency_violation"],
            "robotics": ["tolerance_exceeded", "predictive_failure_warning", "system_offline"],
            "autonomous_vehicle": ["vehicle_offline", "route_deviation", "eta_exceeded"]
        }
        return alerts.get(domain_id, ["item_overdue", "action_required"])

    def _decide_tone_words(self, profile):
        """Pull tone words that will influence copy throughout the app"""
        tone_map = {
            "Calm, clinical, trustworthy": ["Ready", "Confirmed", "Scheduled", "On track"],
            "Fast, urgent, clear": ["Now", "Ready", "Up next", "Fire"],
            "Warm, personal, friendly": ["Welcome", "All set", "Looking good", "Great"],
            "Caring, community, warm": ["Safe", "Checked in", "Accounted for", "Cared for"],
            "Practical, direct, no-nonsense": ["Done", "Check", "Good", "On it"],
            "Motivating, energetic, direct": ["Strong", "Crushing it", "On track", "Let's go"],
            "Precise, reliable, calm": ["Verified", "Confirmed", "Accurate", "Ready"],
            "Alert, technical, urgent": ["Detected", "Monitoring", "Alert", "Scanning"],
            "Precise, technical, reliable": ["Nominal", "Within tolerance", "Predictive", "Stable"],
            "Operational, clear, decisive": ["En route", "On schedule", "Dispatched", "Clear"]
        }
        tone = profile["decisions"]["tone"]
        return tone_map.get(tone, ["Ready", "Done", "Good", "OK"])

    def _print_thinking(self, insight):
        print(f"  👤 WHO:     {insight['human']['who'][:60]}...")
        print(f"  😰 PAIN:    {insight['human']['hardest_moment'][:60]}...")
        print(f"  😮‍💨 RELIEF:  {insight['human']['relief_moment'][:60]}...")
        print(f"  🎯 LEAD WITH: {insight['decisions']['lead_with']}")
        print(f"  ⭐ KEY FEAT:  {insight['decisions']['most_important_feature']}")
        print(f"  🚫 SKIP:      {insight['decisions']['skip']}")
        print(f"  🎨 TONE:      {insight['decisions']['tone']}")
        print(f"  📱 MOBILE:    {insight['decisions']['mobile_first']}")


# ═══════════════════════════════════════════════════
# TEST THE ENGINE
# ═══════════════════════════════════════════════════
if __name__ == "__main__":
    engine = HumanInsightEngine()

    test_domains = [
        "healthcare", "nutrition_center", "salon",
        "agriculture", "rf_sensing", "robotics"
    ]

    print("=" * 60)
    print("HUMAN INSIGHT ENGINE — THINKING LAYER")
    print("=" * 60)

    insights = {}
    for domain in test_domains:
        insight = engine.think(domain, {})
        insights[domain] = insight
        print()

    # Save insights
    out = HOME / "swarm-platform" / "human_insights.json"
    out.write_text(json.dumps(insights, indent=2))
    print(f"\n✅ Insights saved to {out}")
    print(f"📊 {len(insights)} domains profiled")
    print("\nNext: Wire this into turbo_evolve.py so every")
    print("app is built from human insight, not domain name.")
