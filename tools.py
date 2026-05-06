# tools.py
"""
Flight booking and weather tools for LLM function calling.
Compatible with Ollama, OpenAI, and Anthropic APIs.
"""

from typing import Dict, Any, Optional
import logging

# Configure logging (instead of print)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================
# Data Layer (could be moved to database)
# ============================================

class FlightData:
    """Mock database for flight prices"""
    PRICES: Dict[str, str] = {
        "london": "$799",
        "paris": "$899", 
        "tokyo": "$1400",
        "berlin": "$499",
        "new york": "$1099",
        "dubai": "$699"
    }
    
    @classmethod
    def get_price(cls, city: str) -> Optional[str]:
        """Get ticket price for a city"""
        return cls.PRICES.get(city.lower())


class WeatherData:
    """Mock database for weather data"""
    TEMPERATURES: Dict[str, int] = {
        "london": 12,
        "paris": 8,
        "tokyo": 15,
        "berlin": 6,
        "new york": 5,
        "dubai": 28
    }
    
    CONDITIONS: Dict[str, str] = {
        "london": "cloudy ☁️",
        "paris": "rainy 🌧️",
        "tokyo": "sunny ☀️",
        "berlin": "cold ❄️",
        "new york": "windy 🌬️",
        "dubai": "hot 🔥"
    }
    
    @classmethod
    def get_weather(cls, city: str) -> Optional[Dict[str, Any]]:
        """Get weather data for a city"""
        city_lower = city.lower()
        if city_lower not in cls.TEMPERATURES:
            return None
        return {
            "temperature": cls.TEMPERATURES[city_lower],
            "condition": cls.CONDITIONS.get(city_lower, "unknown"),
            "city": city
        }


# ============================================
# Tool Definitions (JSON Schema for LLM)
# ============================================

def create_tool(name: str, description: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Helper to create consistent tool definitions"""
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": parameters,
                "required": list(parameters.keys()),
                "additionalProperties": False
            }
        }
    }


# Individual tool definitions
GET_TICKET_PRICE_TOOL = create_tool(
    name="get_ticket_price",
    description="Get the current ticket price for a return flight to a destination city. Returns price in USD.",
    parameters={
        "destination_city": {
            "type": "string",
            "description": "The name of the destination city (e.g., London, Paris, Tokyo, Berlin)"
        }
    }
)

GET_WEATHER_TOOL = create_tool(
    name="get_weather",
    description="Get current weather conditions (temperature and conditions) for a destination city. Useful for travel planning.",
    parameters={
        "destination_city": {
            "type": "string", 
            "description": "The name of the city to check weather for (e.g., London, Paris, Tokyo)"
        }
    }
)

# Export all tools as a list
ALL_TOOLS = [GET_TICKET_PRICE_TOOL, GET_WEATHER_TOOL]


# ============================================
# Tool Implementations (Actual Functions)
# ============================================

def get_ticket_price(destination_city: str) -> str:
    """
    Get ticket price for a destination city.
    
    Args:
        destination_city: Name of the city to get price for
        
    Returns:
        Formatted string with price information
        
    Example:
        >>> get_ticket_price("london")
        "💰 Ticket to London costs $799"
    """
    logger.info(f"Tool called: get_ticket_price(city={destination_city})")
    
    price = FlightData.get_price(destination_city)
    
    if price:
        return f"💰 The price of a return ticket to {destination_city.title()} is {price}"
    else:
        return f"❌ Sorry, I don't have price information for '{destination_city}'. Available cities: {', '.join(FlightData.PRICES.keys())}"


def get_weather(destination_city: str) -> str:
    """
    Get weather information for a destination city.
    
    Args:
        destination_city: Name of the city to get weather for
        
    Returns:
        Formatted string with weather information
        
    Example:
        >>> get_weather("london")
        "🌤️ Weather in London: 12°C, cloudy ☁️"
    """
    logger.info(f"Tool called: get_weather(city={destination_city})")
    
    weather_data = WeatherData.get_weather(destination_city)
    
    if weather_data:
        return (
            f"🌤️ Weather in {weather_data['city'].title()}: "
            f"{weather_data['temperature']}°C, {weather_data['condition']}"
        )
    else:
        available = ', '.join(WeatherData.TEMPERATURES.keys())
        return f"❌ Sorry, I don't have weather data for '{destination_city}'. Available cities: {available}"


# ============================================
# Tool Dispatcher
# ============================================

TOOL_HANDLERS = {
    "get_ticket_price": get_ticket_price,
    "get_weather": get_weather,
}


def execute_tool(tool_name: str, arguments: Dict[str, Any]) -> str:
    """
    Route and execute the appropriate tool based on LLM's decision.
    
    Args:
        tool_name: Name of the tool to execute
        arguments: Dictionary of arguments for the tool
        
    Returns:
        Result of the tool execution
        
    Raises:
        ValueError: If tool_name is not recognized
    """
    logger.info(f"Executing tool: {tool_name} with args: {arguments}")
    
    if tool_name not in TOOL_HANDLERS:
        error_msg = f"Unknown tool: {tool_name}. Available: {list(TOOL_HANDLERS.keys())}"
        logger.error(error_msg)
        return f"❌ {error_msg}"
    
    try:
        # Get the handler function and execute
        handler = TOOL_HANDLERS[tool_name]
        result = handler(**arguments)
        logger.info(f"Tool execution successful: {result[:100]}...")
        return result
    except Exception as e:
        error_msg = f"Error executing {tool_name}: {str(e)}"
        logger.error(error_msg)
        return f"❌ {error_msg}"


# ============================================
# Schema Validation (Optional but good practice)
# ============================================

def validate_tool_call(tool_name: str, arguments: Dict[str, Any]) -> bool:
    """Validate that a tool call has the correct arguments"""
    expected_args = {
        "get_ticket_price": ["destination_city"],
        "get_weather": ["destination_city"]
    }
    
    if tool_name not in expected_args:
        return False
    
    required = expected_args[tool_name]
    return all(arg in arguments for arg in required)


# ============================================
# Public API (what other modules should import)
# ============================================

__all__ = [
    "ALL_TOOLS",
    "execute_tool", 
    "get_ticket_price",
    "get_weather",
    "validate_tool_call"
]


# ============================================
# Self-test (runs when script is executed directly)
# ============================================

if __name__ == "__main__":
    # Test the tools
    print("=" * 50)
    print("Testing Tools...")
    print("=" * 50)
    
    # Test get_ticket_price
    print("\n1. Testing get_ticket_price:")
    print(get_ticket_price("london"))
    print(get_ticket_price("paris"))
    print(get_ticket_price("unknown"))
    
    # Test get_weather
    print("\n2. Testing get_weather:")
    print(get_weather("tokyo"))
    print(get_weather("berlin"))
    print(get_weather("unknown"))
    
    # Test dispatcher
    print("\n3. Testing tool dispatcher:")
    print(execute_tool("get_ticket_price", {"destination_city": "dubai"}))
    print(execute_tool("get_weather", {"destination_city": "new york"}))
    
    # Test validation
    print("\n4. Testing validation:")
    print(f"Valid call: {validate_tool_call('get_ticket_price', {'destination_city': 'london'})}")
    print(f"Invalid call: {validate_tool_call('get_ticket_price', {'wrong_arg': 'london'})}")