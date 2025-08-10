> DEPRECATED — Legacy documentation. Reference-only on branch `django-migration`. Do not modify. New development is under `web/`.

# 🏢 AA Order Manager

> **Professional order processing application for State and Federal lease management**

A modern GUI application built with Python and Tkinter for processing NMSLO Orders and Federal Orders. Streamlines the creation of Excel worksheets and optional lease folder structures with an intuitive user interface.

## ✨ Features

### 📊 **Order Processing**
- **NMSLO Orders**: Process New Mexico State Land Office lease orders with full search capabilities
- **Federal Orders**: Handle Federal lease orders with specialized formatting
- **Excel Integration**: Generate formatted Excel worksheets with auto-filled columns
- **Date Management**: Smart date handling with calendar picker interface

### 📁 **Flexible Folder Management** *(New!)*
- **Optional Directory Creation**: Choose whether to create lease folder structures
- **Smart Defaults**: Folders disabled by default for faster processing
- **NMSLO-Specific Folders**: Creates `^Document Archive`, `^MI Index`, `Runsheets`
- **Federal-Specific Folders**: Creates `^Document Archive`, `Runsheets`

### 🎯 **User Experience**
- **Intuitive GUI**: Clean, professional interface with logical workflow
- **Validation**: Input validation and helpful error messages
- **Auto-Reset**: Interface resets after each order for fresh processing
- **File Browser**: Easy Excel file selection with Downloads folder default

### 🔍 **Search Generation**
- **Automated Search Strings**: Generates multiple search patterns for lease lookup
- **NMSLO Orders**: Full search, partial search patterns
- **Federal Orders**: File search, Tractstar search patterns
- **Error Handling**: Robust lease number parsing and validation

## 🚀 Quick Start

### **Option 1: Command Line (If Installed)**
```bash
order-manager
```

### **Option 2: Direct Execution**
```bash
cd /path/to/aa-order-manager
python3 app.py
```

## 📋 Requirements

### **System Requirements**
- **OS**: Linux (tested on Ubuntu/Pop!_OS)
- **Python**: 3.6 or higher
- **Display**: GUI desktop environment

### **Python Dependencies**
```bash
pip install -r requirements.txt
```
- `pandas` - Excel file processing
- `openpyxl` - Excel formatting and styles  
- `tkcalendar` - Calendar widget for date selection

## 🔧 Installation

### **Method 1: System-Wide Installation**
1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd aa-order-manager
   ```

2. **Install dependencies**:
   ```bash
   pip3 install -r requirements.txt
   ```

3. **Create system command** (optional):
   ```bash
   sudo tee /usr/local/bin/order-manager << 'EOF'
   #!/usr/bin/env bash
   cd /home/chris/Code/aa-order-manager
   python3 app.py
   EOF
   
   sudo chmod +x /usr/local/bin/order-manager
   ```

### **Method 2: Local Development**
```bash
git clone <repository-url>
cd aa-order-manager
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 app.py
```

## 📖 Usage Guide

### **Basic Workflow**
1. **Launch Application**: Run `order-manager` or `python3 app.py`
2. **Select Agency**: Choose "NMSLO" or "Federal"
3. **Choose Order Type**: Select "Runsheet" (Abstract not implemented)
4. **Set Order Date**: Use calendar picker to select date
5. **Enter Order Number**: Input your order identifier
6. **Select Excel File**: Browse and select your order form (.xlsx)
7. **Configure Options**: Check "Generate Lease Folders" if needed
8. **Process Order**: Click "Process Order" to generate output

### **Options Panel**
The Options section provides control over processing behavior:

- **🗂️ Generate Lease Folders**: 
  - ✅ **Checked**: Creates Excel worksheet + lease folder structure
  - ❌ **Unchecked**: Creates Excel worksheet only (faster, default)

### **Output Files**
Generated files follow the naming pattern:
```
Order_{OrderNumber}_{Agency}_{OrderType}.xlsx
```

**Example**: `Order_2024-001_NMSLO_Runsheet.xlsx`

### **Folder Structure** *(When enabled)*

**NMSLO Orders**:
```
LeaseNumber/
├── ^Document Archive/
├── ^MI Index/
└── Runsheets/
```

**Federal Orders**:
```
LeaseNumber/
├── ^Document Archive/
└── Runsheets/
```

## 🛠️ Development

### **Project Structure**
```
aa-order-manager/
├── app.py              # Main GUI application
├── processors.py       # Order processing logic
├── models.py          # Data models (empty)
├── requirements.txt   # Python dependencies
├── tasks/            # Documentation and PRDs
└── README.md         # This file
```

### **Key Components**
- **`app.py`**: Main GUI interface built with Tkinter
- **`processors.py`**: Contains `NMSLOOrderProcessor` and `FederalOrderProcessor` classes
- **Abstract base class**: `OrderProcessor` defines the processing interface

### **Running Tests**
```bash
# Basic functionality test
python3 processors.py
```

## 🔄 Recent Updates

### **Version 2.1.0** - Generate Lease Folders Feature
- ✨ Added optional folder generation with checkbox control
- 🎨 Improved GUI with Options section and visual borders
- 📏 Adjusted window size for better layout (390px height)
- 🔄 Enhanced reset functionality for checkbox state
- ✅ Comprehensive testing for NMSLO and Federal workflows

### **Previous Updates**
- 📝 Filename generation with descriptive order information
- 🎯 GUI enhancements with date picker and improved validation
- 📊 Enhanced Excel formatting with proper column widths and styles

## 🐛 Troubleshooting

### **Common Issues**

**"Command not found: order-manager"**
- Install the system command using Method 1 above
- Or run directly with `python3 app.py`

**"ModuleNotFoundError"**
- Install dependencies: `pip3 install -r requirements.txt`
- Activate virtual environment if using one

**"Permission denied"**
- Ensure script is executable: `chmod +x /usr/local/bin/order-manager`
- Check file paths in the script match your installation

**"Invalid file type"**
- Ensure you're selecting `.xlsx` files only
- Check file isn't corrupted or password-protected

## 📞 Support

For issues, feature requests, or questions:
1. Check the troubleshooting section above
2. Review recent commits for related fixes
3. Create detailed issue reports with error messages and steps to reproduce

## 📄 License

This project is for internal use. All rights reserved.

---

**Built with ❤️ using Python and Tkinter** 