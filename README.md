# AA Order Manager

A GUI application for processing New Mexico State Orders and Federal Orders.

## Quick Start

From any terminal, simply run:
```bash
order-manager
```

## Installation Details

The `order-manager` script is installed at:
```
/usr/local/bin/order-manager
```

This allows you to run the application from anywhere in your terminal.

## Usage

1. Open terminal
2. Type `order-manager` and press Enter
3. Select order type (New Mexico State Orders or Federal Orders)
4. Click "Process Order" and select your Excel file
5. The application will create worksheets and folders automatically

## Script Contents

The installed script:
- Navigates to `/home/chris/Code/aa-order-manager`
- Runs `python3 app.py`

```bash
#!/usr/bin/env bash

# Navigate to the app directory and run the Python application
cd /home/chris/Code/aa-order-manager
python3 app.py
```

## Reinstallation

If you need to reinstall the command:
1. Create the script file again
2. Make it executable: `chmod +x order-manager`
3. Copy to system path: `sudo cp order-manager /usr/local/bin/` 