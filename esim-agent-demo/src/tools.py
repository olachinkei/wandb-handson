"""
Tools for eSIM Agent Demo

This module defines all the tools used by different agents.
"""

from datetime import datetime
from typing import Optional

from agents import function_tool

from src.utils import (
    load_price_list,
    load_user_cache,
    check_user_login,
    check_payment_method,
    format_price,
    calculate_days_between_dates,
    get_closest_plan_duration,
)


# =============================================================================
# Plan Search Tools
# =============================================================================

def ask_country_period_impl(countries: str, start_date: Optional[str] = None, 
                             end_date: Optional[str] = None, days: Optional[int] = None) -> dict:
    """
    Process country and travel period information from user.
    
    Args:
        countries: Comma-separated list of countries (e.g., "Japan, South Korea")
        start_date: Start date in YYYY-MM-DD format (optional)
        end_date: End date in YYYY-MM-DD format (optional)
        days: Number of days (optional, alternative to dates)
        
    Returns:
        Dictionary with processed countries list and days calculation
    """
    # Parse countries
    country_list = [c.strip() for c in countries.split(',')]
    
    # Calculate days
    if start_date and end_date:
        try:
            calculated_days = calculate_days_between_dates(start_date, end_date)
        except ValueError as e:
            return {"error": f"Invalid date format: {e}"}
    elif days:
        calculated_days = days
    else:
        return {"error": "Please provide either dates (start_date, end_date) or number of days"}
    
    # Get closest available plan duration
    plan_duration = get_closest_plan_duration(calculated_days)
    
    return {
        "countries": country_list,
        "requested_days": calculated_days,
        "plan_duration": plan_duration,
        "message": f"Travel to {', '.join(country_list)} for {calculated_days} days. Recommended plan: {plan_duration} days"
    }


# Wrap with function_tool for agent use
ask_country_period = function_tool(ask_country_period_impl)


def plan_search_impl(countries: list[str], days: int) -> dict:
    """
    Search for eSIM plans based on countries and duration.
    
    Args:
        countries: List of countries
        days: Number of days
        
    Returns:
        Dictionary with available plans and pricing
    """
    price_list = load_price_list()
    
    results = {
        "requested_countries": countries,
        "requested_days": days,
        "plans": []
    }
    
    # Determine plan type: local, regional, or global
    if len(countries) == 1:
        # Local plan for single country
        country = countries[0]
        if country in price_list["local"]:
            local_data = price_list["local"][country]
            region = local_data["region"]
            
            # Find matching plan by days
            for plan in local_data["plans"]:
                if plan["days"] == days:
                    results["plans"].append({
                        "type": "local",
                        "name": f"{country} Local Plan",
                        "countries": [country],
                        "days": plan["days"],
                        "data_gb": plan["data_gb"],
                        "price": format_price(plan["price"]),
                        "price_value": plan["price"],
                        "region": region
                    })
                    break
            
            # Also suggest regional plan as alternative
            if region in price_list["regional"]:
                regional_data = price_list["regional"][region]
                for plan in regional_data["plans"]:
                    if plan["days"] == days:
                        results["plans"].append({
                            "type": "regional",
                            "name": f"{region} Regional Plan",
                            "countries": regional_data["countries"],
                            "days": plan["days"],
                            "data_gb": plan["data_gb"],
                            "price": format_price(plan["price"]),
                            "price_value": plan["price"],
                            "region": region
                        })
                        break
        else:
            results["error"] = f"Country '{country}' not found in database"
            
    else:
        # Multiple countries - check regions
        regions_needed = set()
        for country in countries:
            if country in price_list["local"]:
                regions_needed.add(price_list["local"][country]["region"])
        
        if len(regions_needed) == 1:
            # All in same region - regional plan
            region = list(regions_needed)[0]
            if region in price_list["regional"]:
                regional_data = price_list["regional"][region]
                for plan in regional_data["plans"]:
                    if plan["days"] == days:
                        results["plans"].append({
                            "type": "regional",
                            "name": f"{region} Regional Plan",
                            "countries": regional_data["countries"],
                            "days": plan["days"],
                            "data_gb": plan["data_gb"],
                            "price": format_price(plan["price"]),
                            "price_value": plan["price"],
                            "region": region
                        })
                        break
        else:
            # Cross-regional - need global plan
            global_data = price_list["global"]["Discover Global"]
            for plan in global_data["plans"]:
                if plan["days"] == days:
                    results["plans"].append({
                        "type": "global",
                        "name": "Global Plan",
                        "countries": ["130+ countries worldwide"],
                        "days": plan["days"],
                        "data_gb": plan["data_gb"],
                        "price": format_price(plan["price"]),
                        "price_value": plan["price"],
                        "coverage": global_data["coverage"]
                    })
                    break
    
    return results


# Wrap with function_tool for agent use
plan_search = function_tool(plan_search_impl)


# =============================================================================
# Booking Tools
# =============================================================================

def status_check_impl(user_id: str = "user_001") -> dict:
    """
    Check user login status and payment method registration.
    
    Args:
        user_id: User ID to check (default: user_001)
        
    Returns:
        Dictionary with login and payment status
    """
    is_logged_in = check_user_login(user_id)
    has_payment = check_payment_method(user_id)
    
    user_cache = load_user_cache()
    user = user_cache["users"].get(user_id, {})
    
    return {
        "user_id": user_id,
        "is_logged_in": is_logged_in,
        "has_payment_method": has_payment,
        "user_name": user.get("name", "Unknown"),
        "email": user.get("email", "Unknown"),
        "ready_to_book": is_logged_in and has_payment,
        "message": (
            "Ready to proceed with booking" if (is_logged_in and has_payment)
            else "Please log in and add payment method" if not is_logged_in
            else "Please add a payment method to proceed"
        )
    }


# Wrap with function_tool for agent use
status_check = function_tool(status_check_impl)


def cost_calculator_impl(plan_price: float, quantity: int = 1) -> dict:
    """
    Calculate total cost for eSIM purchase.
    
    Args:
        plan_price: Price of single plan
        quantity: Number of plans (default: 1)
        
    Returns:
        Dictionary with cost breakdown
    """
    subtotal = plan_price * quantity
    tax_rate = 0.08  # 8% tax
    tax = subtotal * tax_rate
    total = subtotal + tax
    
    return {
        "plan_price": format_price(plan_price),
        "quantity": quantity,
        "subtotal": format_price(subtotal),
        "tax_rate": f"{tax_rate * 100}%",
        "tax": format_price(tax),
        "total": format_price(total),
        "total_value": total
    }


# Wrap with function_tool for agent use
cost_calculator = function_tool(cost_calculator_impl)


# =============================================================================
# Tool Lists for Agents
# =============================================================================

PLAN_SEARCH_TOOLS = [ask_country_period, plan_search]
BOOKING_TOOLS = [status_check, cost_calculator]

