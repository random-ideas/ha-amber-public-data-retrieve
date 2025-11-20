# Amber Energy Home Assistant Integration

A Home Assistant custom component to track and display real-time energy pricing data from Amber Electric for Australian postcodes.

## Features

This integration provides the following sensors for both **General Usage** and **Feed-In** tariffs:

- **Current Price** - Current electricity price per kWh (time-aware)
- **Next Price** - Next interval's electricity price per kWh
- **Renewables** - Current renewable energy percentage in the grid
- **Descriptor** - Price level descriptor (e.g., "extremelyLow", "low", "neutral", "high", "spike")

### Time-Aware Logic

The integration intelligently determines the current and next intervals based on NEM timestamps:
- **Current interval**: Most recent interval where `nemTime <= now`
- **Next interval**: Earliest interval where `nemTime > now`

This ensures accurate pricing even when the API returns past, current, and future intervals.

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Go to "Integrations"
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add this repository URL and select "Integration" as the category
6. Click "Install"
7. Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/amber_energy` folder to your Home Assistant `custom_components` directory
2. Restart Home Assistant

## Configuration

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for "Amber Energy"
4. Enter your Australian postcode (e.g., `2000`)
5. Optionally configure the number of past hours to retrieve (default: 1)

## Sensors Created

After configuration, the following sensors will be available:

### General Usage Sensors
- `sensor.amber_general_usage_current_price`
- `sensor.amber_general_usage_next_price`
- `sensor.amber_general_usage_renewables`
- `sensor.amber_general_usage_descriptor`

### Feed-In Sensors
- `sensor.amber_feed_in_current_price`
- `sensor.amber_feed_in_next_price`
- `sensor.amber_feed_in_renewables`
- `sensor.amber_feed_in_descriptor`

## Attributes

Each sensor includes additional attributes:
- `nem_time` - NEM timestamp for the data point
- `descriptor` - Price level descriptor
- `renewables` - Renewable energy percentage
- `postcode` - Configured postcode

## Usage Examples

### Display Current Price in Lovelace

```yaml
type: entities
entities:
  - entity: sensor.amber_general_usage_current_price
    name: Current Electricity Price
  - entity: sensor.amber_general_usage_renewables
    name: Renewables
  - entity: sensor.amber_general_usage_descriptor
    name: Price Level
```

### Automation Based on Price

```yaml
automation:
  - alias: "Start Dishwasher on Low Price"
    trigger:
      - platform: state
        entity_id: sensor.amber_general_usage_descriptor
        to: "extremelyLow"
    action:
      - service: notify.mobile_app
        data:
          message: "Electricity prices are extremely low! Good time to run appliances."
```

### Template Sensor for Positive Feed-In Display

If you prefer to display feed-in prices as positive values (the API may return negative values to indicate income), create a template sensor:

```yaml
template:
  - sensor:
      - name: "Amber Feed-In Current Price (Positive)"
        state: "{{ (states('sensor.amber_feed_in_current_price') | float(0)) | abs }}"
        unit_of_measurement: "¢/kWh"
        device_class: monetary
```

### Energy Dashboard Integration

Add the price sensors to your Energy Dashboard to track costs in real-time.

## API Information

This integration uses the public Amber Electric API:
- Endpoint: `https://backend.amber.com.au/postcode/{postcode}/prices`
- No authentication required for public postcode data
- Updates every 5 minutes

## Data Structure

The API returns pricing intervals with:
- `perKwh` - Price in cents per kilowatt-hour
- `renewables` - Percentage of renewable energy
- `nemTime` - National Electricity Market timestamp (ISO 8601 format)
- `descriptor` - Price level indicator

## Troubleshooting

### No Data Available
- Verify your postcode is valid and serviced by Amber Electric
- Check your internet connection
- Review Home Assistant logs for API errors

### Sensors Not Updating
- Check the integration is enabled in **Settings → Devices & Services**
- Verify the coordinator is updating (check logs)
- Try reloading the integration

### Feed-In Prices Showing as Negative
This is expected behavior - the API returns negative values for feed-in to indicate income vs expense. Use a template sensor (see example above) to display as positive if preferred.

## Credits

Inspired by the [HA_AemoNemData](https://github.com/cabberley/HA_AemoNemData) integration.

## License

MIT License - feel free to use and modify as needed.

## Support

For issues and feature requests, please use the GitHub issue tracker.
