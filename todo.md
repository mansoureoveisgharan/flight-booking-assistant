price_function = {
    "name": "get_ticket_price",
    "description": "Get the price of a return ticket to the destination city.",
    "parameters": {
        "type": "object",
        "properties": {
            "destination_city": {
                "type": "string",
                "description": "The city that the customer wants to travel to",
            },
        },
        "required": ["destination_city"],
        "additionalProperties": False
    }
}

price_function = {
    "name": "...",              # اسم تابع
    "description": "...",       # توضیح (LLM می‌خونه تا بفهمه کی صدا بزنه)
    "parameters": {             # پارامترهای ورودی تابع
        "type": "object",       # نوع داده (معمولاً object)
        "properties": {...},    # تعریف هر پارامتر
        "required": [...],      # پارامترهای اجباری
        "additionalProperties": False  # فقط همین پارامترها قبول باشه
    }
}

چندین ورودی
"properties": {
    "origin_city": {
        "type": "string",
        "description": "Departure city"
    },
    "destination_city": {
        "type": "string", 
        "description": "Arrival city"
    },
    "passengers": {
        "type": "integer",
        "description": "Number of passengers",
        "minimum": 1
    }
}