# Maps.me App Tasks Documentation

## Overview

The Maps.me app tasks test offline navigation and mapping operations using the MAPS.ME app. Tasks include route queries, nearby place searches, bookmark management, and navigation operations.

**Package Name**: `com.mapswithme.maps.pro`  
**Total Tasks**: 15  
**Complexity Range**: 2.0 - 3.5

## Task List

### Query Tasks - Route Distance and Time (5)

#### MapsMeCheckWalkingDistanceTime
- **Complexity**: 2.5
- **Description**: Check walking distance and time between two locations
- **Goal**: "In Maps.me, check the walking distance and time between {origin} and {destination}"
- **Success Criteria**: Agent provides answer containing distance/time units (km, mi, min, hour)

#### MapsMeCheckDrivingDistanceTime
- **Complexity**: 2.5
- **Description**: Check driving distance and time between two locations
- **Goal**: "In Maps.me, check the driving distance and time between {origin} and {destination}"
- **Success Criteria**: Agent provides answer containing distance/time information

#### MapsMeCheckRidingTime
- **Complexity**: 2.5
- **Description**: Check cycling/riding time between two locations
- **Goal**: "In Maps.me, check the riding time between {origin} and {destination}"
- **Success Criteria**: Agent provides answer with time information

#### MapsMeCheckPublicTransportRoute
- **Complexity**: 3.0
- **Description**: Check route by public transportation
- **Goal**: "In Maps.me, check the route by public transportation between {origin} and {destination}"
- **Success Criteria**: Agent provides route/time information

#### MapsMeCompareRidingVsPublicTransport
- **Complexity**: 3.5
- **Description**: Compare travel times between riding and public transport
- **Goal**: "In Maps.me, compare which takes less time to travel between {origin} and {destination}, by riding or by public transportation?"
- **Success Criteria**: Agent mentions either "riding/bike/cycling" or "public/transit/bus"

### Query Tasks - Nearby Places (4)

#### MapsMeCheckNearestPlace
- **Complexity**: 2.0
- **Description**: Find the nearest place of a specific type
- **Goal**: "In Maps.me, check the nearest {place_type} and tell me what is it"
- **Success Criteria**: Agent provides place name, optionally verified via PlacesHistory SQLite table

#### MapsMeCheckNearestPlaceWalkTime
- **Complexity**: 2.5
- **Description**: Find nearest place and walking time to it
- **Goal**: "In Maps.me, check the nearest {place_type}, and tell me the time it will take to walk to the {place_type}."
- **Success Criteria**: Agent provides time information (min, minute, hour, etc.)

#### MapsMeCheckNearestHotel
- **Complexity**: 2.0
- **Description**: Find the nearest hotel
- **Goal**: "In Maps.me, check the nearest hotel, tell me what is it"
- **Success Criteria**: Agent provides hotel name, verified via PlacesHistory.isHotel field

#### MapsMeCheckNearestPlaceDriveTime
- **Complexity**: 2.5
- **Description**: Find nearest specific place and driving time
- **Goal**: "In Maps.me, check the nearest {place_name}, and tell me how long it will take to drive to the {place_name}"
- **Success Criteria**: Agent provides time information

### Operation Tasks - Bookmarks (1)

#### MapsMeAddWorkPlace
- **Complexity**: 3.0
- **Description**: Add an address to Work bookmark
- **Goal**: "In Maps.me, add the address of {place_name} to my Work place"
- **Success Criteria**: "Work" category and matching bookmark found in favorites SQLite database

### Operation Tasks - Navigation (5)

#### MapsMeNavigateToLocation
- **Complexity**: 2.0
- **Description**: Navigate from current location to a destination
- **Goal**: "In Maps.me, navigate from my location to {destination}"
- **Success Criteria**: Destination visible in UI AND navigation mode active

#### MapsMeNavigateToStanford
- **Complexity**: 2.0
- **Description**: Navigate to Stanford University
- **Goal**: "In Maps.me, navigate from my location to Stanford University"
- **Success Criteria**: "Stanford" visible AND navigation active

#### MapsMeNavigateToUniversitySouth
- **Complexity**: 2.0
- **Description**: Navigate to University South
- **Goal**: "In Maps.me, navigate from my location to University South"
- **Success Criteria**: "University South" visible AND navigation active

#### MapsMeNavigateToOpenAI
- **Complexity**: 2.0
- **Description**: Navigate to OpenAI
- **Goal**: "In Maps.me, navigate from my location to OpenAI"
- **Success Criteria**: "OpenAI" visible AND navigation active

#### MapsMeNavigateToBerkeley
- **Complexity**: 2.0
- **Description**: Navigate to UC Berkeley
- **Goal**: "In Maps.me, navigate from my location to University of California, Berkeley"
- **Success Criteria**: "Berkeley" or "California" visible AND navigation active

## Testing

To test Maps.me tasks, use the test script:

```bash
# Test a specific task
python scripts/test_androidlab_apps.py --app maps.me --task MapsMeNavigateToStanford

# Test with custom emulator ports
python scripts/test_androidlab_apps.py --app maps.me --task MapsMeCheckNearestHotel --console_port 5706 --grpc_port 8556
```

## Implementation Details

### Database Paths

- **Favorites Database**: `/data/data/com.mapswithme.maps.pro/databases/favorites`
- **Search History Database**: `/data/data/com.mapswithme.maps.pro/databases/search-history`

### SQLite Tables

#### Favorites Database
| Table | Description |
|-------|-------------|
| `Bookmark` | Saved places with coordinates |
| `Category` | Bookmark categories (e.g., "Work") |
| `CategoryBookmarkRelations` | Links categories to bookmarks |

#### Search History Database
| Table | Description |
|-------|-------------|
| `PlacesHistory` | Places viewed with metadata |
| `QueryHistory` | Search queries |

### Sample Locations Used

- Stanford University
- University of California, Berkeley
- OpenAI
- University South
- San Francisco Airport
- Golden Gate Bridge

### Place Types Searched

- restaurant, hotel, cafe
- gas station, pharmacy, supermarket
- hospital, bank

### Validation Methods

- **Query Tasks**: Check agent's answer for relevant terms (km, min, etc.) + optional SQLite verification
- **Bookmark Tasks**: Verify via favorites database (Category + Bookmark tables)
- **Navigation Tasks**: UI-based check for destination text AND navigation indicators

## Notes

- Navigation validation uses AND logic: destination must be visible AND navigation must be active
- Query tasks accept various units (km, mi, mile, meter, min, hour, hr)
- Nearby place searches can be verified via PlacesHistory table
- Hotel searches check the `isHotel` field in PlacesHistory

