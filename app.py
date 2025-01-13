import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
from collections import defaultdict

# Initialize session state for user settings and datasets
if "user_settings" not in st.session_state:
    st.session_state.user_settings = defaultdict(lambda: {"dropped_columns": [], "dropped_rows": [], "dropped_rows_df": pd.DataFrame(), "dropped_columns_df": pd.DataFrame()})

if "datasets" not in st.session_state:
    st.session_state.datasets = {}

def main():
    st.set_page_config(page_title="Comprehensive Data Reporting Tool", layout="wide")
    st.title("📊 Comprehensive Data Reporting and Visualization Tool")
    
    # Introduction and feature overview
    st.markdown("""
    Features:
    - Upload CSV/Excel files for dynamic data cleaning, processing, and reporting
    - Handle duplicates, missing values, and data type errors
    - Sort, group by columns with aggregates, set indexes
    - Merge, concatenate, and join multiple datasets
    - Dynamic column dropping/restoration
    - Advanced visualization with Plotly
    """)
    
    uploaded_files = st.file_uploader("Upload CSV/Excel files", type=["csv", "xls", "xlsx"], accept_multiple_files=True)
    datasets = []
    if uploaded_files:
        for file in uploaded_files:
            if file.name not in st.session_state.datasets:
                try:
                    if file.name.endswith('.csv'):
                        data = pd.read_csv(file)
                    else:
                        data = pd.read_excel(file)
                    st.session_state.datasets[file.name] = data
                except Exception as e:
                    st.error(f"Failed to load {file.name}: {str(e)}")
                    continue

            data = st.session_state.datasets[file.name]
            settings = st.session_state.user_settings[file.name]

            st.subheader(f"Data Preview for {file.name}")
            st.dataframe(data.head())

            # Data cleaning and management options for each file
            with st.expander(f"Data Cleaning and Management for {file.name}"):
                # Handle Duplicates
                st.markdown("### Handle Duplicates")
                if st.checkbox(f"Remove Duplicates from {file.name}"):
                    data = data.drop_duplicates()
                    st.write("Duplicates removed.")
                    st.dataframe(data.head())

                # Handle Data Types conversion
                st.markdown("### Handle Data Types")
                column_to_convert = st.selectbox(f"Select Column to Convert in {file.name}", data.columns, key=f"convert_{file.name}")
                dtype_option = st.selectbox(f"Convert to Type in {file.name}", ["int", "float", "string", "datetime"], key=f"dtype_{file.name}")
                if st.button(f"Convert Column in {file.name}"):
                    try:
                        data[column_to_convert] = data[column_to_convert].astype(dtype_option)
                        st.success(f"Column '{column_to_convert}' converted to {dtype_option}.")
                    except Exception as e:
                        st.error(f"Error converting column: {str(e)}")

                # Sorting Data
                st.markdown("### Sorting")
                sort_col = st.selectbox(f"Select Column to Sort in {file.name}", data.columns, key=f"sort_{file.name}")
                sort_ascending = st.checkbox(f"Sort in Ascending Order in {file.name}", value=True, key=f"ascending_{file.name}")
                if st.button(f"Sort Data in {file.name}"):
                    data = data.sort_values(by=sort_col, ascending=sort_ascending)
                    st.dataframe(data.head())

                # Grouping and Aggregating Data
                st.markdown("### Group By and Aggregate")
                group_col = st.selectbox(f"Select Column to Group By in {file.name}", data.columns, key=f"group_{file.name}")
                agg_func = st.selectbox(f"Select Aggregation Function for {file.name}", ["sum", "mean", "count", "min", "max"], key=f"agg_{file.name}")
                if st.button(f"Group and Aggregate in {file.name}"):
                    grouped_data = data.groupby(group_col).agg(agg_func)
                    st.dataframe(grouped_data)

                # Set Index
                st.markdown("### Set Index")
                index_col = st.selectbox(f"Select Column to Set as Index in {file.name}", data.columns, key=f"index_{file.name}")
                if st.button(f"Set Index in {file.name}"):
                    data.set_index(index_col, inplace=True)
                    st.dataframe(data.head())

            # Data Preprocessing Options (e.g., filling missing values)
            with st.expander(f"Data Cleaning and Preprocessing Options for {file.name}"):
                if st.checkbox(f"Drop Rows with Missing Values in {file.name}"):
                    data = data.dropna()
                if st.checkbox(f"Fill Missing Values in {file.name}"):
                    fill_value = st.text_input(f"Enter value to fill missing cells in {file.name}", "0")
                    data = data.fillna(fill_value)
                if st.checkbox(f"Rename Columns in {file.name}"):
                    # Select the column to rename
                    column_to_rename = st.selectbox("Select Column to Rename", data.columns)
                    
                    # Get the new column name from user input
                    new_column_name = st.text_input(f"Enter new name for '{column_to_rename}'", "")
                    
                    # Rename column if the user provides a new name
                    if new_column_name:
                        data.rename(columns={column_to_rename: new_column_name}, inplace=True)
                        st.success(f"Column '{column_to_rename}' renamed to '{new_column_name}'")
                st.dataframe(data.head())

            # Row and Column Management
            with st.expander(f"Manage Rows/Columns for {file.name}"):
                settings = st.session_state.setdefault("user_settings", {}).setdefault(file.name, {"dropped_columns": [], "dropped_rows": []})

                # Column Management
                st.markdown("### Column Management")
                available_columns = [col for col in data.columns if col not in settings["dropped_columns"]]
                drop_columns = st.multiselect(f"Select Columns to Drop for {file.name}", available_columns)
                if st.button(f"Drop Selected Columns ({file.name})"):
                    try:
                        # Store dropped columns in a temporary DataFrame
                        dropped_columns_df = data[drop_columns].copy()  # Save the dropped columns to restore later
                        settings["dropped_columns_df"] = dropped_columns_df  # Store it in the session state

                        # Drop the columns from the main DataFrame
                        data.drop(columns=drop_columns, inplace=True)
                        settings["dropped_columns"].extend(drop_columns)

                        st.success(f"Dropped columns: {', '.join(drop_columns)}")
                        st.dataframe(data.head())
                    except Exception as e:
                        st.error(f"Column drop error: {str(e)}")

                restore_columns = st.multiselect(f"Select Columns to Restore for {file.name}", settings["dropped_columns"])
                if st.button(f"Restore Selected Columns ({file.name})"):
                    try:
                        # Ensure we have stored dropped columns in `dropped_columns_df`
                        if settings["dropped_columns_df"].empty:
                            st.warning("No columns to restore.")
                        else:
                            # Get the columns to restore based on the column names
                            restored_columns = settings["dropped_columns_df"][restore_columns].copy()

                            # Concatenate the restored columns back into the original DataFrame
                            data = pd.concat([data, restored_columns], axis=1)

                            # Update the session state with the restored data
                            st.session_state.datasets[file.name] = data.copy()

                            # Remove restored columns from dropped columns list
                            settings["dropped_columns"] = [col for col in settings["dropped_columns"] if col not in restore_columns]

                            st.success(f"Restored columns: {', '.join(restore_columns)}")
                            st.dataframe(data.head())
                    except Exception as e:
                        st.error(f"Column restore error: {str(e)}")

                # Row Management (no changes, remains the same as previous)
                st.markdown("### Row Management")
                available_rows = list(data.index.difference(settings["dropped_rows"]))
                drop_rows = st.multiselect(f"Select Rows to Drop for {file.name}", available_rows)
                if st.button(f"Drop Selected Rows ({file.name})"):
                    try:
                        # Store dropped rows in a temporary DataFrame
                        dropped_rows_df = data.loc[drop_rows].copy()  # Save the rows to restore later
                        settings["dropped_rows_df"] = dropped_rows_df  # Store it in the session state

                        # Now drop the rows from the main dataframe
                        data.drop(index=drop_rows, inplace=True)
                        settings["dropped_rows"].extend(drop_rows)

                        st.success(f"Dropped rows: {', '.join(map(str, drop_rows))}")
                        st.dataframe(data.head())
                    except Exception as e:
                        st.error(f"Row drop error: {str(e)}")

                restore_rows = st.multiselect(f"Select Rows to Restore for {file.name}", settings["dropped_rows"])
                if st.button(f"Restore Selected Rows ({file.name})"):
                    try:
                        # Ensure we have stored dropped rows in `dropped_rows_df`
                        if settings["dropped_rows_df"].empty:
                            st.warning("No rows to restore.")
                        else:
                            # Get the rows to restore based on the original index
                            restored_rows = settings["dropped_rows_df"].loc[settings["dropped_rows_df"].index.isin(restore_rows)].copy()

                            # Concatenate the restored rows back into the original DataFrame
                            data = pd.concat([data, restored_rows]).sort_index()

                            # Update the session state with the restored data
                            st.session_state.datasets[file.name] = data.copy()

                            # Remove restored rows from dropped rows list
                            settings["dropped_rows"] = [row for row in settings["dropped_rows"] if row not in restore_rows]

                            st.success(f"Restored rows: {', '.join(map(str, restore_rows))}")
                            st.dataframe(data.head())
                    except Exception as e:
                        st.error(f"Row restore error: {str(e)}")



            datasets.append(data)

        # Merging/Concatenating multiple datasets
        if len(datasets) > 1:
            merge_option = st.radio("Choose a method to combine files", ("Concatenate", "Merge/Join"))
            if merge_option == "Concatenate":
                data = pd.concat(datasets, ignore_index=True)
            elif merge_option == "Merge/Join":
                st.warning("Merging requires specifying key columns manually for demo.")
                merge_on = st.text_input("Enter column name to merge on (same for all files):")
                data = datasets[0]
                for df in datasets[1:]:
                    data = data.merge(df, on=merge_on, how="inner") if merge_on else data

        st.subheader("Combined Data Preview")
        st.dataframe(data.head())

        # Filtering and Custom Formula Inputs
        with st.expander("Custom Filtering and Formulas"):
            col_to_filter = st.selectbox("Select Column to Filter", data.columns)
            filter_value = st.text_input("Enter value to filter by")
            if st.button("Apply Filter"):
                data = data[data[col_to_filter].astype(str).str.contains(filter_value)]
                st.dataframe(data.head())

            custom_formula = st.text_area("Enter a formula using column names (e.g., `NewCol = ColA + ColB * 2`)")
            if custom_formula:
                try:
                    col_name, expression = custom_formula.split("=")
                    data[col_name.strip()] = data.eval(expression.strip())
                    st.success(f"Formula applied: {custom_formula}")
                except Exception as e:
                    st.error(f"Error applying formula: {str(e)}")
            st.dataframe(data.head())

        # Visualization (unchanged from the previous code)
        st.markdown("### Data Visualization")
        x_col = st.selectbox(f"Select X-axis Column for {file.name}", data.columns)
        y_col = st.selectbox(f"Select Y-axis Column for {file.name}", data.columns)
        plot_type = st.selectbox(f"Select Plot Type for {file.name}", ["Scatter Plot", "Line Plot", "Bar Plot", "Histogram", "Box Plot", "Heatmap"])

        if st.button(f"Generate Plot for {file.name}"):
            try:
                if plot_type == "Scatter Plot":
                    fig = px.scatter(data, x=x_col, y=y_col)
                elif plot_type == "Line Plot":
                    fig = px.line(data, x=x_col, y=y_col)
                elif plot_type == "Bar Plot":
                    fig = px.bar(data, x=x_col, y=y_col)
                elif plot_type == "Histogram":
                    fig = px.histogram(data, x=x_col)
                elif plot_type == "Box Plot":
                    fig = px.box(data, x=x_col, y=y_col)
                elif plot_type == "Heatmap":
                    corr = data.corr()
                    fig = sns.heatmap(corr, annot=True, cmap="coolwarm")
                    st.pyplot(plt.gcf())
                st.plotly_chart(fig)
            except Exception as e:
                st.error(f"Visualization error: {str(e)}")

        st.write("#### Descriptive Statistics")
        if st.button("Show Descriptive Statistics of the new file"):
            try:
                st.write(data.describe())
            except Exception as e:
                st.error(f"Statistics error: {str(e)}")


        # Generate and Export Report
        st.subheader("Generate Report")
        report_file = "cleaned_data_report.xlsx"
        if st.button("Export and Download Report"):
            with pd.ExcelWriter(report_file, engine='openpyxl') as writer:
                data.to_excel(writer, index=False, sheet_name="Cleaned Data")
            with open(report_file, "rb") as file:
                st.download_button("Download Cleaned Report", file, file_name=report_file)

if __name__ == "__main__":
    main()
