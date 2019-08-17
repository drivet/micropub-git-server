mf2schema = """{
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "type": { "$ref": "#/definitions/types" },
        "properties": { "$ref": "#/definitions/properties" },
        "children": {
            "type": "array",
            "items": { "$ref": "#" }
        },
        "id": { "type": "string" }
    },
    "required": ["type", "properties"],
    "additionalProperties": false,
    "definitions" : {
        "types": {
            "type": "array",
            "items": {
                "type": "string",
                "pattern": "^h-([0-9a-z]+-)?[a-z]+(-[a-z]+)*$"
            },
            "minItems": 1
        },
        "properties": {
            "type": "object",
            "patternProperties": {
                "^([0-9a-z]+-)?[a-z]+(-[a-z]+)*$": {
                    "type": "array",
                    "items": {
                        "oneOf": [
                            { "type": "string" },
                            { "$ref": "#/definitions/htmlproperty" },
                            { "$ref": "#/definitions/complexproperty" },
                            { "$ref": "#/definitions/imageproperty" }
                        ]
                    }
                }
            },
            "additionalProperties": false
        },
        "htmlproperty": {
            "type": "object",
            "properties": {
                "html": { "type": "string" },
                "value": { "type": "string" }
            },
            "required": ["html", "value"],
            "additionalProperties": false
        },
        "complexproperty": {
            "type": "object",
            "properties": {
                "type": { "$ref": "#/definitions/types" },
                "properties": { "$ref": "#/definitions/properties" },
                "value": { "type": "string" },
                "html": { "type": "string" }
            },
            "required": ["type", "properties", "value"],
            "additionalProperties": false
        },
        "imageproperty": {
            "type": "object",
            "properties": {
                "value": { "type": "string" },
                "alt": { "type": "string" }
            },
            "required": ["value", "alt"],
            "additionalProperties": false
        }
    }
}
"""
