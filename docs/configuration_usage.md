# Configuration System Usage Guide

This guide explains how to use the externalized configuration system for agency-specific order processing.

## Overview

The configuration system uses a hybrid approach with:
- **Static Configuration**: Type-safe data (column widths, folder structures, agency names)
- **Behavioral Configuration**: Callable functions (search mappings, dynamic behavior)

## Basic Usage

### Using Default Configuration

```python
from src.core.processors import NMSLOOrderProcessor, FederalOrderProcessor

# Use default NMSLO configuration
nmslo_processor = NMSLOOrderProcessor(
    order_form="nmslo_orders.xlsx",
    agency="NMSLO",
    order_type="Runsheet",
    order_date="2024-01-01",
    order_number="12345"
)

# Use default Federal configuration
federal_processor = FederalOrderProcessor(
    order_form="federal_orders.xlsx",
    agency="Federal",
    order_type="Runsheet",
    order_date="2024-01-01",
    order_number="54321"
)
```

### Using Custom Configuration

```python
from src.core.config.models import AgencyStaticConfig, AgencyBehaviorConfig
from src.core.processors import NMSLOOrderProcessor

# Create custom static configuration
custom_static = AgencyStaticConfig(
    column_widths={
        "Agency": 20,
        "Order Type": 25,
        "Lease": 20,
        "Custom Column": 15
    },
    folder_structure=["^Custom Archive", "Custom Folder"],
    dropbox_agency_name="CustomAgency"
)

# Create custom behavioral configuration
def custom_search_func(data):
    return f"custom_search_{data}"

custom_behavioral = AgencyBehaviorConfig(
    search_mappings={
        "Custom Search": custom_search_func,
        "Another Search": lambda x: f"lambda_{x}"
    },
    blank_columns=["Custom Column", "Another Column"]
)

# Use custom configuration
processor = NMSLOOrderProcessor(
    order_form="custom_orders.xlsx",
    agency="CustomAgency",
    static_config=custom_static,
    behavioral_config=custom_behavioral
)
```

## Configuration Factory Methods

### Getting Complete Configuration

```python
from src.core.config.factory import get_agency_config

# Get complete configuration for an agency
config = get_agency_config("NMSLO")
static_config = config["static"]
behavioral_config = config["behavioral"]
```

### Getting Specific Configuration Types

```python
from src.core.config.factory import get_static_config, get_behavioral_config

# Get static configuration only
static_config = get_static_config("NMSLO")
print(f"Column widths: {static_config.column_widths}")
print(f"Folder structure: {static_config.folder_structure}")

# Get behavioral configuration only
behavioral_config = get_behavioral_config("Federal")
print(f"Search columns: {behavioral_config.get_search_columns()}")
print(f"Blank columns: {behavioral_config.get_blank_columns()}")
```

### Getting All Columns

```python
from src.core.config.factory import get_all_columns

# Get all columns that will be in the final worksheet
nmslo_columns = get_all_columns("NMSLO")
federal_columns = get_all_columns("Federal")

print(f"NMSLO columns: {nmslo_columns}")
print(f"Federal columns: {federal_columns}")
```

## Validation and Error Handling

### Validating Agency Types

```python
from src.core.config.factory import validate_agency_type

# Check if an agency is supported
if validate_agency_type("NMSLO"):
    print("NMSLO is supported")
else:
    print("NMSLO is not supported")

# Get list of supported agencies
from src.core.config.factory import get_supported_agencies
supported = get_supported_agencies()
print(f"Supported agencies: {supported}")
```

### Error Handling

```python
from src.core.config.exceptions import InvalidAgencyError, ConfigurationError

try:
    config = get_agency_config("InvalidAgency")
except InvalidAgencyError as e:
    print(f"Invalid agency: {e}")
    print(f"Supported agencies: {e.supported_agencies}")

try:
    static_config = get_static_config("NMSLO")
except ConfigurationError as e:
    print(f"Configuration error: {e}")
```

## Creating Custom Configurations

### Static Configuration

```python
from src.core.config.models import AgencyStaticConfig

# Create static configuration with validation
static_config = AgencyStaticConfig(
    column_widths={
        "Agency": 15,
        "Order Type": 20,
        "Lease": 15,
        "Requested Legal": 25,
        "Report Start Date": 20
    },
    folder_structure=[
        "^Document Archive",
        "^Custom Index",
        "Runsheets"
    ],
    dropbox_agency_name="CustomAgency"
)

# Access configuration values
print(f"Column width for 'Agency': {static_config.get_column_width('Agency')}")
print(f"Default column width: {static_config.get_column_width('NonExistent', 12)}")
```

### Behavioral Configuration

```python
from src.core.config.models import AgencyBehaviorConfig

# Create search functions
def full_search(lease_data):
    return f"full_search_{lease_data}"

def partial_search(lease_data):
    return f"partial_search_{lease_data}"

# Create behavioral configuration
behavioral_config = AgencyBehaviorConfig(
    search_mappings={
        "Full Search": full_search,
        "Partial Search": partial_search,
        "Lambda Search": lambda x: f"lambda_{x}"
    },
    blank_columns=[
        "New Format",
        "Tractstar",
        "Documents",
        "Search Notes",
        "Link"
    ]
)

# Use behavioral configuration
search_columns = behavioral_config.get_search_columns()
blank_columns = behavioral_config.get_blank_columns()

# Process search data
import pandas as pd
lease_data = pd.Series(["B-1234-5", "B-6789-0"])
search_data = behavioral_config.create_search_data(lease_data)
```

## Testing with Mock Configurations

### Creating Test Configurations

```python
from tests.core.config.test_utils import create_mock_static_config, create_mock_behavioral_config

# Create mock configurations for testing
mock_static = create_mock_static_config("TestAgency")
mock_behavioral = create_mock_behavioral_config()

# Use in tests
processor = NMSLOOrderProcessor(
    order_form="test.xlsx",
    static_config=mock_static,
    behavioral_config=mock_behavioral
)
```

### Testing Configuration Validation

```python
import pytest
from src.core.config.exceptions import ConfigurationError

def test_invalid_static_config():
    with pytest.raises(ConfigurationError):
        AgencyStaticConfig(
            column_widths={},  # Empty - will raise error
            folder_structure=["Test"],
            dropbox_agency_name="Test"
        )

def test_invalid_behavioral_config():
    with pytest.raises(ConfigurationError):
        AgencyBehaviorConfig(
            search_mappings={},  # Empty - will raise error
            blank_columns=["Test"]
        )
```

## Best Practices

### 1. Use Factory Methods

✅ **Good:**
```python
from src.core.config.factory import get_static_config
static_config = get_static_config("NMSLO")
```

❌ **Avoid:**
```python
from src.core.config.registry import AGENCY_CONFIGS
static_config = AGENCY_CONFIGS["NMSLO"]["static"]  # Direct registry access
```

### 2. Handle Configuration Errors

✅ **Good:**
```python
try:
    config = get_agency_config(agency_type)
except InvalidAgencyError as e:
    logger.error(f"Unsupported agency: {e.agency_name}")
    return None
```

❌ **Avoid:**
```python
config = get_agency_config(agency_type)  # May raise unhandled exception
```

### 3. Use Dependency Injection for Testing

✅ **Good:**
```python
# In tests
processor = NMSLOOrderProcessor(
    order_form="test.xlsx",
    static_config=mock_static,
    behavioral_config=mock_behavioral
)
```

❌ **Avoid:**
```python
# Hard to test
processor = NMSLOOrderProcessor("test.xlsx")  # Uses real config
```

### 4. Validate Custom Configurations

✅ **Good:**
```python
# Configuration is validated automatically
static_config = AgencyStaticConfig(...)  # Validates on creation
behavioral_config = AgencyBehaviorConfig(...)  # Validates on creation
```

### 5. Use Type Hints

✅ **Good:**
```python
from src.core.config.models import AgencyStaticConfig, AgencyBehaviorConfig

def process_with_config(
    static_config: AgencyStaticConfig,
    behavioral_config: AgencyBehaviorConfig
) -> pd.DataFrame:
    # Process with typed configuration
    pass
```

## Adding New Agency Types

To add a new agency type:

1. **Add to Registry:**
```python
# In src/core/config/registry.py
AGENCY_CONFIGS["NewAgency"] = {
    "static": AgencyStaticConfig(...),
    "behavioral": AgencyBehaviorConfig(...)
}
```

2. **Create Processor (Optional):**
```python
class NewAgencyProcessor(OrderProcessor):
    def __init__(self, order_form, **kwargs):
        super().__init__(order_form, **kwargs)
        self.static_config = kwargs.get('static_config') or get_static_config("NewAgency")
        self.behavioral_config = kwargs.get('behavioral_config') or get_behavioral_config("NewAgency")
```

3. **Test Configuration:**
```python
def test_new_agency_configuration():
    config = get_agency_config("NewAgency")
    assert config["static"].dropbox_agency_name == "NewAgency"
    assert "Custom Search" in config["behavioral"].search_mappings
```

## Performance Considerations

- Configuration is loaded once per processor instance
- Factory methods cache configuration access
- Validation happens at startup, not during processing
- Search functions should be efficient for large datasets

## Troubleshooting

### Common Issues

1. **Invalid Agency Error:**
   - Check agency name spelling
   - Use `get_supported_agencies()` to see available agencies

2. **Configuration Validation Error:**
   - Ensure all required fields are provided
   - Check data types (integers for widths, strings for names)
   - Verify search functions are callable

3. **Search Function Errors:**
   - Ensure search functions handle NaN/empty values
   - Test with sample data before production use

### Debug Configuration

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Configuration access will be logged
config = get_agency_config("NMSLO")
``` 