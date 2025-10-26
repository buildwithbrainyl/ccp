import json
import datetime
import time

def validate(slots):

    valid_programs = ['ccp', 'sa', 'genai']
    
    # Validate ProgramType
    if not slots['ProgramType']:
        print("Inside Empty ProgramType")
        return {
        'isValid': False,
        'violatedSlot': 'ProgramType'
        }        
        
    if slots['ProgramType']['value']['originalValue'].lower() not in valid_programs:
        
        print("Not valid program")
        
        return {
        'isValid': False,
        'violatedSlot': 'ProgramType',
        'message': 'We currently support only {} as valid programs. Please choose one.'.format(", ".join(['CCP', 'SA', 'GenAI']))
        }
    
    # Validate StartDate
    if not slots['StartDate']:
        
        return {
        'isValid': False,
        'violatedSlot': 'StartDate',
    }
    
    # Validate Months
    if not slots['Months']:
        return {
        'isValid': False,
        'violatedSlot': 'Months'
    }
    
    # Validate Months is between 3 and 6
    if slots['Months']:
        try:
            months = int(slots['Months']['value']['interpretedValue'])
            if months < 3 or months > 6:
                return {
                'isValid': False,
                'violatedSlot': 'Months',
                'message': 'Commitment must be between 3 and 6 months. Please choose a valid duration.'
                }
        except (ValueError, KeyError):
            return {
            'isValid': False,
            'violatedSlot': 'Months',
            'message': 'Please provide a valid number of months (3-6).'
            }

    return {'isValid': True}
    
def lambda_handler(event, context):
    
    print("Event:", json.dumps(event))
    slots = event['sessionState']['intent']['slots']
    intent = event['sessionState']['intent']['name']
    print("invocationSource:", event['invocationSource'])
    print("slots:", slots)
    print("intent:", intent)
    validation_result = validate(event['sessionState']['intent']['slots'])
    
    if event['invocationSource'] == 'DialogCodeHook':
        if not validation_result['isValid']:
            
            if 'message' in validation_result:
            
                response = {
                "sessionState": {
                    "dialogAction": {
                        'slotToElicit':validation_result['violatedSlot'],
                        "type": "ElicitSlot"
                    },
                    "intent": {
                        'name':intent,
                        'slots': slots
                        
                        }
                },
                "messages": [
                    {
                        "contentType": "PlainText",
                        "content": validation_result['message']
                    }
                ]
               } 
            else:
                response = {
                "sessionState": {
                    "dialogAction": {
                        'slotToElicit':validation_result['violatedSlot'],
                        "type": "ElicitSlot"
                    },
                    "intent": {
                        'name':intent,
                        'slots': slots
                        
                        }
                }
               } 
    
            return response
           
        else:
            response = {
            "sessionState": {
                "dialogAction": {
                    "type": "Delegate"
                },
                "intent": {
                    'name':intent,
                    'slots': slots
                    
                    }
        
            }
        }
            return response
    
    if event['invocationSource'] == 'FulfillmentCodeHook':
        
        # Add mentorship booking to Database
        
        response = {
        "sessionState": {
            "dialogAction": {
                "type": "Close"
            },
            "intent": {
                'name':intent,
                'slots': slots,
                'state':'Fulfilled'
                
                }
    
        },
        "messages": [
            {
                "contentType": "PlainText",
                "content": "Thanks! I have booked your AWS mentorship session. You'll receive a confirmation email shortly."
            }
        ]
    }
            
        return response
