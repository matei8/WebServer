"""
Unit tests for the health statistics webserver.
"""

import unittest
import json
import os
import pandas as pd
from app.data_ingestor import DataIngestor
from app.task_runner import ThreadPool
from app import webserver

class TestWebserver(unittest.TestCase):
    """Test class for the webserver implementation."""

    def setUp(self):
        """Set up test environment."""
        # Create a test CSV file with sample data
        self.test_csv_path = "test_data.csv"
        self.create_test_csv()

        # Create results directory if it doesn't exist
        if not os.path.exists('results'):
            os.makedirs('results')

        # Initialize test components
        self.data_ingestor = DataIngestor(self.test_csv_path)
        self.thread_pool = ThreadPool(logger=webserver.logger, webserver=webserver)
        webserver.data_ingestor = self.data_ingestor
        webserver.tasks_runner = self.thread_pool
        webserver.job_counter = 1

    def create_test_csv(self):
        """Create a test CSV file with sample data."""
        test_data = {
            'Question': [
                'Percent of adults who engage in no leisure-time physical activity',
                'Percent of adults who engage in no leisure-time physical activity',
                'Percent of adults who engage in muscle-strengthening activities on 2 or more days a week',
                'Percent of adults who engage in muscle-strengthening activities on 2 or more days a week'
            ],
            'LocationDesc': ['California', 'New York', 'California', 'New York'],
            'Data_Value': [25.0, 30.0, 40.0, 35.0],
            'YearStart': [2020, 2020, 2020, 2020],
            'StratificationCategory1': ['Overall', 'Overall', 'Overall', 'Overall'],
            'Stratification1': ['Total', 'Total', 'Total', 'Total']
        }
        df = pd.DataFrame(test_data)
        df.to_csv(self.test_csv_path, index=False)

    def tearDown(self):
        """Clean up after tests."""
        # Clean up test CSV file
        if os.path.exists(self.test_csv_path):
            os.remove(self.test_csv_path)

        # Clean up results directory
        if os.path.exists('results'):
            # Remove all files in results directory
            for file in os.listdir('results'):
                file_path = os.path.join('results', file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print(f"Error deleting {file_path}: {e}")
            
            # Remove the directory itself
            try:
                os.rmdir('results')
            except Exception as e:
                print(f"Error removing results directory: {e}")

    def test_states_mean(self):
        """Test the states_mean endpoint."""
        data = {
            "question": "Percent of adults who engage in no leisure-time physical activity"
        }
        result = self.data_ingestor.get_states_mean(data)
        self.assertEqual(len(result), 2)  # We have data for 2 states
        self.assertEqual(result['California'], 25.0)
        self.assertEqual(result['New York'], 30.0)

    def test_state_mean(self):
        """Test the state_mean endpoint."""
        data = {
            "question": "Percent of adults who engage in no leisure-time physical activity",
            "state": "California"
        }
        result = self.data_ingestor.get_state_mean(data)
        self.assertEqual(result['California'], 25.0)

    def test_best5(self):
        """Test the best5 endpoint."""
        data = {
            "question": "Percent of adults who engage in muscle-strengthening activities on 2 or more days a week"
        }
        result = self.data_ingestor.get_best5(data)
        self.assertEqual(len(result), 2)  # We have data for 2 states
        self.assertEqual(result['California'], 40.0)  # California has higher value

    def test_worst5(self):
        """Test the worst5 endpoint."""
        data = {
            "question": "Percent of adults who engage in no leisure-time physical activity"
        }
        result = self.data_ingestor.get_worst5(data)
        self.assertEqual(len(result), 2)  # We have data for 2 states
        self.assertEqual(result['New York'], 30.0)  # New York has higher value

    def test_global_mean(self):
        """Test the global_mean endpoint."""
        data = {
            "question": "Percent of adults who engage in no leisure-time physical activity"
        }
        result = self.data_ingestor.get_global_mean(data)
        self.assertEqual(result['global_mean'], 27.5)  # (25.0 + 30.0) / 2

    def test_diff_from_mean(self):
        """Test the diff_from_mean endpoint."""
        data = {
            "question": "Percent of adults who engage in no leisure-time physical activity"
        }
        result = self.data_ingestor.get_diff_from_mean(data)
        self.assertEqual(len(result), 2)
        self.assertEqual(result['California'], 2.5)  # 27.5 - 25.0
        self.assertEqual(result['New York'], -2.5)  # 27.5 - 30.0

    def test_state_diff_from_mean(self):
        """Test the state_diff_from_mean endpoint."""
        data = {
            "question": "Percent of adults who engage in no leisure-time physical activity",
            "state": "California"
        }
        result = self.data_ingestor.get_state_diff_from_mean(data)
        self.assertEqual(result['California'], 2.5)  # 27.5 - 25.0

    def test_mean_by_category(self):
        """Test the mean_by_category endpoint."""
        data = {
            "question": "Percent of adults who engage in no leisure-time physical activity"
        }
        result = self.data_ingestor.get_mean_by_category(data)
        expected_key = "('California', 'Overall', 'Total')"
        self.assertEqual(result[expected_key], 25.0)

    def test_state_mean_by_category(self):
        """Test the state_mean_by_category endpoint."""
        data = {
            "question": "Percent of adults who engage in no leisure-time physical activity",
            "state": "California"
        }
        result = self.data_ingestor.get_state_mean_by_category(data)
        expected_key = "('Overall', 'Total')"
        self.assertEqual(result['California'][expected_key], 25.0)

    def test_missing_parameters(self):
        """Test handling of missing parameters."""
        data = {
            "state": "California"
        }
        with self.assertRaises(ValueError):
            self.data_ingestor.get_state_mean(data)

    def test_empty_data(self):
        """Test handling of empty data."""
        data = {
            "question": "Percent of adults who engage in no leisure-time physical activity",
            "state": "NonExistentState"
        }
        with self.assertRaises(ValueError):
            self.data_ingestor.get_state_mean(data)

    def test_task_runner(self):
        """Test the task runner functionality."""
        data = {
            "question": "Percent of adults who engage in no leisure-time physical activity"
        }
        job_id = self.thread_pool.add_task((1, self.data_ingestor.get_states_mean, data))
        self.assertEqual(job_id, 1)
        self.assertEqual(self.thread_pool.job_status[1], 'running')

if __name__ == '__main__':
    unittest.main() 
