# Proper 404 Error Handling for Home Assistant Entity Requests

The 404 error is **expected behavior** when you request a non-existent entity. This is correct validation, not a bug!

## What Cloud AI Should Do

Instead of assuming entities exist, it should:

1.  **First discover available entities** to verify actual exist:
    
    ```bash
    POST /list_entities_native
    Body: {"domain": "light"}
    ```
    
    Or use targeted discovery:
    
    ```bash
    POST /discover_devices
    Body: {"domain": "light", "area": "living room"}
    ```
    
2.  **Then use a real entity** from that list in subsequent operations
    
3.  **Handle 404** as "entity not found" (not a generic server error)
    

* * *

## Error Format Standardization

### 404 Not Found Error Response Structure

```json
{
  "detail": "Entity not found"
}
```

**Cause:** Entity ID doesn't exist  
**Solution:** Use discovery APIs to find correct entity ID

* * *

## Best Practice Implementation

### ❌ BAD EXAMPLE - Without Discovery

```bash
POST /control_light
Body: {"entity_id": "light.unknown", "action": "turn_on"}
→ Response: 404 Not Found
→ AI Response: "Error: Entity not found"
```

### ✅ GOOD EXAMPLE - With Discovery

```bash
# Step 1: Discover all living room lights
POST /get_area_devices
Body: {"area_name": "living room"}
→ Returns: light.living_room_main, light.living_room_side

# Step 2: Control discovered entity
POST /control_light
Body: {"entity_id": "light.living_room_main", "action": "turn_on"}
→ Response: 200 OK
→ AI Response: "Living room lights turned on ✓"
```

* * *

## Complete Error Handling Protocol

Follow this workflow for 100% error-free responses:

```
1. Discovery Phase
   • list_entities_native
   • discover_devices
   • get_area_devices

2. Validation Phase
   • get_entity_state_native
   • check entity attributes

3. Action Phase
   • Execute intended command

4. Error Response Handling
   • 404 → "Entity not found" + suggest discovery
   • 500 → "Service failed" + suggest alternative actions
```

* * *

## Smart Error Messaging Guidelines

When returning errors to users:

**Always:**

*   Explain the root cause (e.g., "The light 'living_room_unknown' doesn't exist")
    
*   Offer immediate alternatives ("I found these lights, would you like me to control one of these?")
    
*   Suggest next steps (discovery commands)
    
*   Provide examples of working solutions
    

**Never:**

*   Return raw JSON error messages
    
*   Suggest the error is on your end
    
*   Make users search for entity IDs themselves
    
*   Give generic "entity doesn't exist" messages without context
    

* * *

## Documentation Reference

This workflow is documented in both:

*   `AI_TRAINING_GUIDE.md`
    
*   Home Assistant AI Control Guide, Sections 4.1 and 5.2