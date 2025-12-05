# MAPS.ME M3A Agent Results

## Summary

| Metric | Value |
|--------|-------|
| App | MAPS.ME (Navigation) |
| Total Tasks | 15 |
| Successful | 0 |
| Failed | 15 |
| Success Rate | 0.0% |

## Results by Task

| Task | Status | Score | Steps | Complexity |
|------|--------|-------|-------|------------|
| MapsMeCheckWalkingDistanceTime | ❌ Fail | 0.00 | 7/25 | 2.5 |
| MapsMeCheckDrivingDistanceTime | ❌ Fail | 0.00 | 10/25 | 2.5 |
| MapsMeCheckRidingTime | ❌ Fail | 0.00 | 4/25 | 2.5 |
| MapsMeCheckPublicTransportRoute | ❌ Fail | 0.00 | 5/30 | 3 |
| MapsMeCompareRidingVsPublicTransport | ❌ Fail | 0.00 | 6/35 | 3.5 |
| MapsMeCheckNearestPlace | ❌ Fail | 0.00 | 7/20 | 2 |
| MapsMeCheckNearestPlaceWalkTime | ❌ Fail | 0.00 | 4/25 | 2.5 |
| MapsMeCheckNearestHotel | ❌ Fail | 0.00 | 4/20 | 2 |
| MapsMeCheckNearestPlaceDriveTime | ❌ Fail | 0.00 | 8/25 | 2.5 |
| MapsMeAddWorkPlace | ❌ Fail | 0.70 | 5/30 | 3 |
| MapsMeNavigateToLocation | ❌ Fail | 0.00 | 9/20 | 2 |
| MapsMeNavigateToStanford | ❌ Fail | 0.00 | 12/20 | 2 |
| MapsMeNavigateToUniversitySouth | ❌ Fail | 0.00 | 5/20 | 2 |
| MapsMeNavigateToOpenAI | ❌ Fail | 0.00 | 8/20 | 2 |
| MapsMeNavigateToBerkeley | ❌ Fail | 0.00 | 5/20 | 2 |

## Detailed Results

### Task 1: MapsMeCheckWalkingDistanceTime ❌
- **Goal**: In the MAPS.ME app, check the walking distance and time between University of California, Berkeley and OpenAI
- **Complexity**: 2.5
- **Steps**: 7/25
- **Result**: Agent did not provide an answer via the answer action.

### Task 2: MapsMeCheckDrivingDistanceTime ❌
- **Goal**: In the MAPS.ME app, check the driving distance and time between Bus Stop of Oxford Street & University Avenue and OpenAI
- **Complexity**: 2.5
- **Steps**: 10/25
- **Result**: Agent did not provide an answer via the answer action.

### Task 3: MapsMeCheckRidingTime ❌
- **Goal**: In the MAPS.ME app, check the riding time between Bus stop of 2700 Coast Avenue and University South
- **Complexity**: 2.5
- **Steps**: 4/25
- **Result**: Agent did not provide an answer via the answer action.

### Task 4: MapsMeCheckPublicTransportRoute ❌
- **Goal**: In the MAPS.ME app, check the route by public transportation between Stanford University and OpenAI
- **Complexity**: 3
- **Steps**: 5/30
- **Result**: Agent did not provide an answer via the answer action.

### Task 5: MapsMeCompareRidingVsPublicTransport ❌
- **Goal**: In the MAPS.ME app, compare which takes less time to travel between OpenAI and Bus Stop of Oxford Street & University Avenue, by riding or by public transportation?
- **Complexity**: 3.5
- **Steps**: 6/35
- **Result**: Agent did not provide an answer via the answer action.

### Task 6: MapsMeCheckNearestPlace ❌
- **Goal**: In the MAPS.ME app, check the nearest supermarket and tell me what is it
- **Complexity**: 2
- **Steps**: 7/20
- **Result**: Agent did not provide an answer via the answer action.

### Task 7: MapsMeCheckNearestPlaceWalkTime ❌
- **Goal**: In the MAPS.ME app, check the nearest restaurant, and tell me the time it will take to walk to the restaurant.
- **Complexity**: 2.5
- **Steps**: 4/25
- **Result**: Agent did not provide an answer via the answer action.

### Task 8: MapsMeCheckNearestHotel ❌
- **Goal**: In the MAPS.ME app, check the nearest hotel, tell me what is it
- **Complexity**: 2
- **Steps**: 4/20
- **Result**: Agent did not provide an answer via the answer action.

### Task 9: MapsMeCheckNearestPlaceDriveTime ❌
- **Goal**: In the MAPS.ME app, check the nearest IKEA, and tell me how long it will take to drive to the IKEA
- **Complexity**: 2.5
- **Steps**: 8/25
- **Result**: Agent did not provide an answer via the answer action.

### Task 10: MapsMeAddWorkPlace ❌
- **Goal**: In the MAPS.ME app, add the address of Stanford University to my Work place
- **Complexity**: 3
- **Steps**: 5/30
- **Score**: 0.70 (partial success)
- **Result**: Task partially completed.

### Task 11: MapsMeNavigateToLocation ❌
- **Goal**: In the MAPS.ME app, navigate from my location to San Francisco Airport
- **Complexity**: 2
- **Steps**: 9/20
- **Result**: Agent completed but task conditions not met.

### Task 12: MapsMeNavigateToStanford ❌
- **Goal**: In the MAPS.ME app, navigate from my location to Stanford University
- **Complexity**: 2
- **Steps**: 12/20
- **Result**: Agent completed but task conditions not met.

### Task 13: MapsMeNavigateToUniversitySouth ❌
- **Goal**: In the MAPS.ME app, navigate from my location to University South
- **Complexity**: 2
- **Steps**: 5/20
- **Result**: Agent completed but task conditions not met.

### Task 14: MapsMeNavigateToOpenAI ❌
- **Goal**: In the MAPS.ME app, navigate from my location to OpenAI
- **Complexity**: 2
- **Steps**: 8/20
- **Result**: Agent completed but task conditions not met.

### Task 15: MapsMeNavigateToBerkeley ❌
- **Goal**: In the MAPS.ME app, navigate from my location to University of California, Berkeley
- **Complexity**: 2
- **Steps**: 5/20
- **Result**: Agent completed but task conditions not met.

## Failure Analysis

| Failure Type | Count | Tasks |
|--------------|-------|-------|
| No answer action | 9 | MapsMeCheckWalkingDistanceTime, MapsMeCheckDrivingDistanceTime, MapsMeCheckRidingTime, MapsMeCheckPublicTransportRoute, MapsMeCompareRidingVsPublicTransport, MapsMeCheckNearestPlace, MapsMeCheckNearestPlaceWalkTime, MapsMeCheckNearestHotel, MapsMeCheckNearestPlaceDriveTime |
| Task conditions not met | 5 | MapsMeNavigateToLocation, MapsMeNavigateToStanford, MapsMeNavigateToUniversitySouth, MapsMeNavigateToOpenAI, MapsMeNavigateToBerkeley |
| Partial success | 1 | MapsMeAddWorkPlace (score: 0.70) |

**Observations**:
- All 15 tasks failed (0% success rate)
- 9 tasks failed because the agent did not use the `answer` action to provide results
- 5 navigation tasks completed but did not meet the task conditions
- One task (MapsMeAddWorkPlace) achieved partial success with 0.70 score

## Command Used

```bash
python scripts/test_androidlab_apps.py --app maps.me --run_all --console_port 5706 --grpc_port 8556
```

