# Emergency Workflow Implementation

## Overview
Implemented asynchronous event-driven workflow for realistic emergency alert lifecycle with step-by-step delays and real-time UI updates.

## Architecture

### Backend (Python)
**File**: `app/services/emergency_orchestrator.py`
- `EmergencyOrchestrator` class manages the entire workflow
- Uses `asyncio` for non-blocking delays
- Updates Firestore in real-time at each step

### Workflow Steps

1. **SEARCHING_HOSPITALS** (2s delay)
   - Coordinator analyzes alert
   - Finds nearest hospital with available beds

2. **HOSPITAL_SELECTED** (1s delay)
   - Hospital selected and logged
   - Distance calculated

3. **DISPATCHING_AMBULANCE** (1s delay)
   - Finds nearest available ambulance
   - Matches ambulance type to emergency level

4. **EN_ROUTE_TO_PATIENT** (5s delay)
   - Calculates route: Ambulance → Patient
   - Draws BLUE route on map
   - Shows ETA

5. **PATIENT_PICKUP** (3s delay)
   - Simulates patient stabilization
   - Prepares for transport

6. **EN_ROUTE_TO_HOSPITAL** (5s delay)
   - Calculates route: Patient → Hospital
   - Draws RED route on map
   - Shows new ETA

7. **RESOLVED**
   - Patient admitted
   - Mission complete
   - Total time calculated

### Frontend (JavaScript)
**File**: `app/static/js/emergency_workflow.js`
- `EmergencyWorkflowManager` class polls backend every 2 seconds
- Updates UI components dynamically:
  - Activity log
  - Status badge
  - Map routes (blue → red)
  - ETA display
  - Hospital info panel

### API Endpoint
**Route**: `/api/alert/<alert_id>/data`
- Returns structured real-time data
- Includes: status, logs, route_geometry, eta_minutes, hospital, ambulance

## Usage

### Trigger Workflow
```python
# In api.py - automatically triggered on alert creation
orchestrator = EmergencyOrchestrator()
asyncio.run(orchestrator.run_workflow(alert_id, lat, lng, emergency_level))
```

### Frontend Integration
```javascript
// Automatically starts on tracking page load
const workflowManager = new EmergencyWorkflowManager(alertId, mapInstance);
workflowManager.startPolling();

// Custom callbacks
workflowManager.onStatusChange((data) => {
    // Handle status updates
});
```

## Key Features

✅ **Realistic Delays**: Simulates actual emergency response times
✅ **Real-time Updates**: Frontend polls backend every 2 seconds
✅ **Visual Feedback**: Map routes change color based on phase
✅ **Activity Log**: Shows timestamped agent actions
✅ **State Management**: Firestore stores current workflow state
✅ **Auto-stop**: Polling stops when workflow completes

## Testing

1. Create an alert from `/alert` page
2. Navigate to tracking page
3. Watch workflow progress through all phases
4. Observe map route changes (blue → red)
5. Check activity log for timestamped updates

## Customization

### Adjust Delays
Edit `emergency_orchestrator.py`:
```python
await asyncio.sleep(2)  # Change delay duration
```

### Change Route Colors
Edit `emergency_workflow.js`:
```javascript
const color = phase === 'TO_PATIENT' ? '#3b82f6' : '#ef4444';
```

### Modify Polling Interval
Edit `emergency_workflow.js`:
```javascript
this.pollingInterval = setInterval(() => {
    this.fetchStatus();
}, 2000); // Change from 2000ms
```
