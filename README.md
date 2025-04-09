# Health Statistics Analysis System

A Flask-based web service for analyzing health statistics data with concurrent task processing capabilities.

## Overview

This system provides a RESTful API for analyzing health statistics data from the U.S. Department of Health & Human Services. The data covers nutrition, physical activity, and obesity statistics across U.S. states from 2011 to 2022.

## Architecture

### 1. Flask Web Server (`app/__init__.py`)
- **Initialization**: Sets up the Flask application with proper configuration
- **Logging**: Implements RotatingFileHandler for efficient log management
- **Components**:
  - DataIngestor: Handles data loading and processing
  - ThreadPool: Manages concurrent task execution
  - Job Counter: Tracks and assigns unique job IDs
- **Logging Configuration**:
  - Uses UTC timestamps for consistency
  - Implements log rotation with size limits
  - Tracks all API endpoint access and errors

### 2. Data Ingestor (`app/data_ingestor.py`)
- **Data Loading**: Efficiently loads and processes CSV data
- **Statistical Analysis**:
  - State-level means calculation
  - Global statistics computation
  - Category-based analysis
  - Best/worst performing states identification
- **Data Validation**: Implements robust error checking and validation
- **Performance Optimizations**:
  - Efficient pandas operations
  - Optimized data filtering
  - Memory-efficient processing

### 3. Task Runner (`app/task_runner.py`)
- **Thread Pool Implementation**:
  - Configurable number of threads (via TP_NUM_OF_THREADS)
  - Efficient task queuing and execution
  - Graceful shutdown handling
- **Job Management**:
  - Unique job ID assignment
  - Status tracking
  - Result storage and retrieval
- **Concurrency Control**:
  - Thread-safe operations
  - Proper synchronization
  - Efficient resource utilization

## API Endpoints

### Task Management
- `POST /api/start`: Initiates new task processing
  - Returns unique job ID
  - Queues task for execution
- `GET /api/status/<job_id>`: Checks task status
  - Returns current processing state
- `GET /api/results/<job_id>`: Retrieves task results
  - Returns processed data or error status

### Data Analysis Endpoints
1. **State Statistics**
   - `POST /api/states_mean`: Calculates mean values for all states
   - `POST /api/state_mean`: Calculates mean for specific state
   - `POST /api/best5`: Identifies top 5 performing states
   - `POST /api/worst5`: Identifies bottom 5 performing states

2. **Global Analysis**
   - `POST /api/global_mean`: Computes overall mean value
   - `POST /api/diff_from_mean`: Calculates differences from global mean
   - `POST /api/state_diff_from_mean`: Computes difference for specific state

3. **Category Analysis**
   - `POST /api/mean_by_category`: Calculates means by category
   - `POST /api/state_mean_by_category`: Computes category means for specific state

### System Management
- `GET /api/graceful_shutdown`: Initiates controlled shutdown
- `GET /api/jobs`: Lists all jobs and their statuses
- `GET /api/num_jobs`: Returns count of pending jobs

## Implementation Details

### Data Processing
- **Efficient Data Loading**:
  - Single CSV load at startup
  - Optimized data structures
  - Memory-efficient processing

- **Statistical Calculations**:
  - Vectorized operations using pandas
  - Efficient filtering and aggregation
  - Proper handling of edge cases

### Concurrency Implementation
- **Thread Pool**:
  - Dynamic thread count based on CPU cores
  - Efficient task distribution
  - Proper resource management

- **Job Management**:
  - Atomic job ID assignment
  - Thread-safe status updates
  - Efficient result storage

### Error Handling
- **Input Validation**:
  - Comprehensive parameter checking
  - Clear error messages
  - Proper status codes

- **System Errors**:
  - Graceful error recovery
  - Detailed logging
  - User-friendly error responses

## Performance Considerations

### Data Processing
- Optimized pandas operations
- Efficient memory usage
- Minimized data copying

### Concurrency
- Proper thread synchronization
- Efficient resource utilization
- Scalable architecture

### I/O Operations
- Efficient file handling
- Optimized logging
- Proper resource cleanup

## DataIngestor Implementation Details

The DataIngestor class (`app/data_ingestor.py`) is responsible for processing and analyzing the health statistics data. Here's a detailed breakdown of its functions:

### 1. Initialization (`__init__`)
```python
def __init__(self, csv_path: str)
```
- Loads the CSV file containing health statistics data
- Initializes lists to determine sorting order for best/worst endpoints
- Sets up data structures for efficient querying

### 2. State-Level Analysis

#### `get_states_mean(data)`
```python
def get_states_mean(self, data)
```
- **Purpose**: Calculates mean values for all states for a given question
- **Input**: Dictionary containing the question to analyze
- **Process**:
  - Filters data for the specified question
  - Groups by state
  - Calculates mean Data_Value for each state
  - Sorts results in ascending order
- **Output**: Dictionary mapping states to their mean values

#### `get_state_mean(data)`
```python
def get_state_mean(self, data)
```
- **Purpose**: Calculates mean value for a specific state
- **Input**: Dictionary containing question and state
- **Process**:
  - Filters data for specified question and state
  - Calculates mean Data_Value
- **Output**: Dictionary with single state and its mean value

### 3. Best/Worst Performing States

#### `get_best5(data)`
```python
def get_best5(self, data)
```
- **Purpose**: Identifies top 5 best performing states
- **Input**: Dictionary containing the question
- **Process**:
  - Filters data for specified question and year range (2011-2022)
  - Calculates mean per state
  - Determines sorting order based on question type
  - Returns top 5 states
- **Output**: Dictionary of top 5 states and their values

#### `get_worst5(data)`
```python
def get_worst5(self, data)
```
- **Purpose**: Identifies bottom 5 worst performing states
- **Input**: Dictionary containing the question
- **Process**:
  - Similar to get_best5 but returns bottom 5 states
  - Sorting order depends on question type
- **Output**: Dictionary of bottom 5 states and their values

### 4. Global Analysis

#### `get_global_mean(data)`
```python
def get_global_mean(self, data)
```
- **Purpose**: Calculates global mean across all states
- **Input**: Dictionary containing the question
- **Process**:
  - Filters data for specified question
  - Calculates mean of all Data_Values
- **Output**: Dictionary with single global mean value

#### `get_diff_from_mean(data)`
```python
def get_diff_from_mean(self, data)
```
- **Purpose**: Calculates difference between global mean and state means
- **Input**: Dictionary containing the question
- **Process**:
  - Gets global mean
  - Gets state means
  - Calculates difference for each state
  - Sorts by difference
- **Output**: Dictionary mapping states to their differences from global mean

#### `get_state_diff_from_mean(data)`
```python
def get_state_diff_from_mean(self, data)
```
- **Purpose**: Calculates difference for a specific state
- **Input**: Dictionary containing question and state
- **Process**:
  - Gets global mean
  - Gets state mean
  - Calculates difference
- **Output**: Dictionary with state and its difference from global mean

### 5. Category Analysis

#### `get_mean_by_category(data)`
```python
def get_mean_by_category(self, data)
```
- **Purpose**: Calculates means by category for all states
- **Input**: Dictionary containing the question
- **Process**:
  - Filters data for specified question
  - Groups by state, category, and segment
  - Calculates means for each combination
- **Output**: Dictionary mapping (state, category, segment) tuples to means

#### `get_state_mean_by_category(data)`
```python
def get_state_mean_by_category(self, data)
```
- **Purpose**: Calculates means by category for a specific state
- **Input**: Dictionary containing question and state
- **Process**:
  - Filters data for specified question and state
  - Groups by category and segment
  - Calculates means for each combination
- **Output**: Dictionary mapping (category, segment) tuples to means

### Error Handling
- All functions include validation for:
  - Missing required parameters
  - Invalid question types
  - Empty data sets
  - Missing required columns
- Returns appropriate error messages with status codes

### Performance Considerations
- Efficient data filtering using pandas
- Optimized groupby operations
- Memory-efficient processing
- Proper error handling to prevent crashes

## Usage

### Setup
```bash
# Create and activate virtual environment
make create_venv
source venv/bin/activate

# Install dependencies
make install

# Start server
make run_server
```

### API Usage Examples
```bash
# Start analysis task
curl -X POST http://localhost:5000/api/states_mean \
  -H "Content-Type: application/json" \
  -d '{"question": "Percent of adults who engage in no leisure-time physical activity"}'

# Check task status
curl http://localhost:5000/api/status/1

# Get results
curl http://localhost:5000/api/results/1
