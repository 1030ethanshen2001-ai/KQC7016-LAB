import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns


def preprocess_lab2_data(file_path):
    """
    Lab 2: Data Preprocessing Module
    This module is responsible for data cleaning, feature filtering,
    baseline year labeling, and aggregation calculations.
    """

    # ==========================================
    # Step 1: Environment Setup and Robustness Checks
    # ==========================================
    if not os.path.exists(file_path):
        raise FileNotFoundError(
            f"Dataset file not found: {file_path}. Please ensure it is in the same directory as the script."
        )

    try:
        # ==========================================
        # Step 2: Data Loading and Core Feature Extraction
        # ==========================================
        print("Loading and extracting the core dataset...")
        df = pd.read_csv(file_path)

        core_columns = [
            'country', 'year', 'iso_code', 'gdp',
            'renewables_share_energy', 'fossil_share_energy'
        ]
        df_subset = df[[col for col in core_columns if col in df.columns]].copy()

        # ==========================================
        # Step 3: Data Cleaning
        # ==========================================
        # Remove regional aggregate rows, keep data after year 2000,
        # and drop rows with missing values in key columns
        df_cleaned = df_subset.dropna(subset=['iso_code']).copy()
        df_cleaned = df_cleaned[df_cleaned['year'] >= 2000]
        df_cleaned = df_cleaned.dropna(
            subset=['gdp', 'renewables_share_energy', 'fossil_share_energy']
        )

        # ==========================================
        # Step 4: Feature Engineering and Baseline Year Selection
        # ==========================================
        base_year = 2019
        if base_year not in df_cleaned['year'].values:
            base_year = df_cleaned['year'].max()

        base_data = df_cleaned[df_cleaned['year'] == base_year]
        median_gdp = base_data['gdp'].median()
        print(
            f"\nBaseline year ({base_year}) with the global median GDP used as the classification threshold: "
            f"{median_gdp:,.2f}"
        )

        high_gdp_countries = base_data[base_data['gdp'] >= median_gdp]['country'].unique()

        # Assign permanent group labels
        df_cleaned['income_group'] = df_cleaned['country'].apply(
            lambda x: 'High GDP' if x in high_gdp_countries else 'Low/Mid GDP'
        )

        # ==========================================
        # Step 5: Generate Three Datasets for Visualization
        # ==========================================
        df_scatter = df_cleaned[df_cleaned['year'] == base_year].copy()

        df_trend = (
            df_cleaned.groupby(['year', 'income_group'])['renewables_share_energy']
            .mean()
            .reset_index()
        )

        df_structure = (
            df_scatter.groupby('income_group')[
                ['renewables_share_energy', 'fossil_share_energy']
            ]
            .mean()
            .reset_index()
        )

        print("Data preprocessing is complete, and the dataset is ready for visualization.")
        return df_scatter, df_trend, df_structure

    except Exception as e:
        print(f"An error occurred during data processing: {e}")
        return None, None, None


def plot_figures(scatter_data, trend_data, structure_data):
    """
    Plot and save all figures for Lab 2.
    """
    sns.set(style="whitegrid")
    output_dir = "figures"
    os.makedirs(output_dir, exist_ok=True)

    # ==========================================
    # Figure 1: Scatter Plot
    # GDP vs Renewable Energy Share
    # ==========================================
    plt.figure(figsize=(10, 6))
    sns.scatterplot(
        data=scatter_data,
        x="gdp",
        y="renewables_share_energy",
        hue="income_group",
        palette="Set2",
        s=70,
        alpha=0.8
    )
    plt.xscale("log")
    plt.title("Figure 1. GDP vs Renewable Energy Share (Baseline Year)", fontsize=14)
    plt.xlabel("GDP (log scale)", fontsize=12)
    plt.ylabel("Renewables Share of Energy (%)", fontsize=12)
    plt.legend(title="Income Group")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "figure1_scatter.png"), dpi=300)
    plt.show()

    # ==========================================
    # Figure 2: Trend Line
    # Renewable Energy Share Trend by Income Group
    # ==========================================
    plt.figure(figsize=(10, 6))
    sns.lineplot(
        data=trend_data,
        x="year",
        y="renewables_share_energy",
        hue="income_group",
        palette="Set2",
        linewidth=2.5
    )
    plt.title("Figure 2. Renewable Energy Share Trend by Income Group", fontsize=14)
    plt.xlabel("Year", fontsize=12)
    plt.ylabel("Average Renewables Share of Energy (%)", fontsize=12)
    plt.legend(title="Income Group")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "figure2_trend.png"), dpi=300)
    plt.show()

    # ==========================================
    # Figure 3: Bar Chart
    # Average Energy Structure Comparison
    # ==========================================
    df_structure_melted = structure_data.melt(
        id_vars="income_group",
        value_vars=["renewables_share_energy", "fossil_share_energy"],
        var_name="Energy Type",
        value_name="Average Share"
    )

    plt.figure(figsize=(10, 6))
    sns.barplot(
        data=df_structure_melted,
        x="income_group",
        y="Average Share",
        hue="Energy Type",
        palette="Set2"
    )
    plt.title("Figure 3. Average Energy Structure Comparison", fontsize=14)
    plt.xlabel("Income Group", fontsize=12)
    plt.ylabel("Average Share of Energy (%)", fontsize=12)
    plt.legend(title="Energy Type")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "figure3_structure.png"), dpi=300)
    plt.show()

    print(f"\nAll figures have been saved in the '{output_dir}' folder.")


# --- Main Execution ---
if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    target_file = os.path.join(current_dir, "worldenergy.csv")

    scatter_data, trend_data, structure_data = preprocess_lab2_data(target_file)

    if structure_data is not None:
        print("\nEnergy Structure Comparison Between Two Country Groups")
        print(structure_data)

        plot_figures(scatter_data, trend_data, structure_data)