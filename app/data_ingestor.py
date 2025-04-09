"""
Data ingestor for processing and analyzing health statistics data.
"""

import pandas as pd

class DataIngestor:
    """Class for ingesting and processing health statistics data."""

    def __init__(self, csv_path: str):
        """
        Initialize the data ingestor.
        
        Args:
            csv_path: Path to the CSV file containing the data
        """
        self.data = pd.read_csv(csv_path, encoding='utf-8')

        # These lists help determine sorting order for best/worst endpoints
        self.questions_best_is_min = [
            'Percent of adults aged 18 years and older who have an overweight classification',
            'Percent of adults aged 18 years and older who have obesity',
            'Percent of adults who engage in no leisure-time physical activity',
            'Percent of adults who report consuming fruit less than one time daily',
            'Percent of adults who report consuming vegetables less than one time daily'
        ]

        self.questions_best_is_max = [
            'Percent of adults who achieve at least 150 minutes a week of moderate-intensity aerobic physical activity or 75 minutes a week of vigorous-intensity aerobic activity (or an equivalent combination)',
            'Percent of adults who achieve at least 150 minutes a week of moderate-intensity aerobic physical activity or 75 minutes a week of vigorous-intensity aerobic physical activity and engage in muscle-strengthening activities on 2 or more days a week',
            'Percent of adults who achieve at least 300 minutes a week of moderate-intensity aerobic physical activity or 150 minutes a week of vigorous-intensity aerobic activity (or an equivalent combination)',
            'Percent of adults who engage in muscle-strengthening activities on 2 or more days a week',
        ]

    def get_states_mean(self, data):
        """
        Returns the mean 'Data_Value' for each state for a given question
        across all years, sorted ascending by mean value.
        """
        question = data.get("question")
        print(question)
        filtered_data = self.data[(self.data['Question'] == question)]

        # Calculate mean per state and sort
        state_means = (filtered_data.groupby('LocationDesc')['Data_Value'].mean()
            .sort_values(ascending=True)
            .to_dict()
        )

        return state_means

    def get_state_mean(self, data):
        """
        Returns the mean value for a specific state for the given question
        """
        question = data.get("question")
        state = data.get("state")
        if not question or not state:
            raise ValueError("Missing 'question' or 'state' in request")

        # Filter data for the given question and state
        filtered_data = self.data[(self.data['Question'] == question) & (self.data['LocationDesc'] == state)]
        if filtered_data.empty:
            raise ValueError(f"No data found for question: {question} and state: {state}")

        # Check for required column
        if 'Data_Value' not in filtered_data.columns:
            raise ValueError("Required column 'Data_Value' is missing in the dataset")

        # Calculate the mean for 'Data_Value'
        result = filtered_data['Data_Value'].mean()

        return {state: result}

    def get_best5(self, data):
        """
        Returns the top 5 states with the best scores for the given question.
        'Best' is determined by whether lower or higher values are considered better.
        Filters the data for years 2011 to 2022.
        """
        question = data.get("question")
        if not question:
            raise ValueError("Missing 'question' in request data")

        if question not in self.questions_best_is_min and question not in self.questions_best_is_max:
            raise ValueError("Unknown question or not supported for best5 analysis")

        # Filter for question and year range
        filtered = self.data[
            (self.data["Question"] == question) &
            (self.data["YearStart"] >= 2011) &
            (self.data["YearStart"] <= 2022)
            ]

        if filtered.empty:
            raise ValueError("No data found for the provided question in years 2011–2022")

        # Compute mean Data_Value per state
        state_means = filtered.groupby("LocationDesc")["Data_Value"].mean()

        # Determine sorting order
        if question in self.questions_best_is_min:
            best_states = state_means.nsmallest(5)  # For questions where lower is better
        else:
            best_states = state_means.nlargest(5)  # For questions where higher is better

        return best_states.to_dict()

    def get_worst5(self, data):
        """
        Returns the bottom 5 states with the worst scores for the given question
        """
        question = data.get("question")
        if not question:
            raise ValueError("Missing 'question' in request")

        # Filter data for the given question
        filtered_data = self.data[self.data['Question'] == question]
        if filtered_data.empty:
            raise ValueError(f"No data found for question: {question}")

        # Check for required columns
        if 'Data_Value' not in filtered_data.columns or 'LocationDesc' not in filtered_data.columns:
            raise ValueError("Required columns 'Data_Value' or 'LocationDesc' are missing in the dataset")

        # Calculate the mean for 'Data_Value' for each state
        state_means = (
            filtered_data.groupby('LocationDesc')['Data_Value']
            .mean()
            .sort_values(ascending=not (question in self.questions_best_is_min))
            .head(5)
            .to_dict()
        )

        return state_means

    def get_global_mean(self, data):
        """
        Returns the global mean for the given question.
        """
        question = data.get("question")
        if not question:
            raise ValueError("Missing 'question' in request")

        # Filter data for the given question
        filtered_data = self.data[self.data['Question'] == question]
        if filtered_data.empty:
            raise ValueError(f"No data found for question: {question}")

        # Check for required column
        if 'Data_Value' not in filtered_data.columns:
            raise ValueError("Required column 'Data_Value' is missing in the dataset")

        # Calculate the global mean
        global_mean = filtered_data['Data_Value'].mean()
        return {"global_mean": global_mean}

    def get_diff_from_mean(self, data):
        """
        Returns the difference between the global mean and state means for all states.
        """
        global_mean = self.get_global_mean(data)['global_mean']
        state_means = self.get_states_mean(data)

        # Calculate the difference for each state (global_mean - state_mean)
        diff = {state: round(global_mean - state_mean, 6) for state, state_mean in state_means.items()}
        
        # Sort the dictionary by values in descending order
        sorted_diff = dict(sorted(diff.items(), key=lambda item: item[1], reverse=True))
        
        return sorted_diff

    def get_state_diff_from_mean(self, data):
        """
        Returns the difference between the global mean and the mean for a specific state.
        """
        global_mean = self.get_global_mean(data)['global_mean']
        state_mean = self.get_state_mean(data)
        state, mean_value = next(iter(state_mean.items()))

        # Calculate the difference (global_mean - state_mean)
        return {state: round(global_mean - mean_value, 6)}

    def get_mean_by_category(self, data):
        """
        Returns the mean for each category (Stratification1) for the given question.
        """
        question = data.get("question")
        if not question:
            raise ValueError("Missing 'question' in request")

        # Filter data for the given question
        filtered_data = self.data[self.data['Question'] == question]
        if filtered_data.empty:
            raise ValueError(f"No data found for question: {question}")

        # Check for required columns
        required_columns = ['Data_Value', 'Stratification1', 'StratificationCategory1', 'LocationDesc']
        missing_columns = [col for col in required_columns if col not in filtered_data.columns]
        if missing_columns:
            raise ValueError(f"Required columns {missing_columns} are missing in the dataset")

        # Calculate the mean for each state, category, and segment
        result = {}
        for state in filtered_data['LocationDesc'].unique():
            state_data = filtered_data[filtered_data['LocationDesc'] == state]
            for category in state_data['StratificationCategory1'].unique():
                category_data = state_data[state_data['StratificationCategory1'] == category]
                for segment in category_data['Stratification1'].unique():
                    segment_data = category_data[category_data['Stratification1'] == segment]
                    mean_value = segment_data['Data_Value'].mean()
                    # Convert tuple to string key
                    key = f"('{state}', '{category}', '{segment}')"
                    result[key] = mean_value

        return result

    def get_state_mean_by_category(self, data):
        """
        Returns the mean for each category (Stratification1) for a specific state.
        """
        question = data.get("question")
        state = data.get("state")
        if not question or not state:
            raise ValueError("Missing 'question' or 'state' in request")

        # Filter data for the given question and state
        filtered_data = self.data[(self.data['Question'] == question) & (self.data['LocationDesc'] == state)]
        if filtered_data.empty:
            raise ValueError(f"No data found for question: {question} and state: {state}")

        # Check for required columns
        required_columns = ['Data_Value', 'Stratification1', 'StratificationCategory1']
        missing_columns = [col for col in required_columns if col not in filtered_data.columns]
        if missing_columns:
            raise ValueError(f"Required columns {missing_columns} are missing in the dataset")

        # Calculate the mean for each category and segment
        result = {}
        # Get unique categories and sort them
        categories = sorted(filtered_data['StratificationCategory1'].unique())
        for category in categories:
            category_data = filtered_data[filtered_data['StratificationCategory1'] == category]
            # Get unique segments and sort them
            segments = sorted(category_data['Stratification1'].unique())
            for segment in segments:
                segment_data = category_data[category_data['Stratification1'] == segment]
                mean_value = segment_data['Data_Value'].mean()
                # Convert tuple to string key
                key = f"('{category}', '{segment}')"
                result[key] = mean_value

        # Wrap the result in a state-level dictionary
        return {state: result}